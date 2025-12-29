import os
from datetime import datetime
from functools import wraps
from flask_mail import Message
from flask import render_template,redirect,request,url_for,make_response,session,flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from tcg import app,csrf,mail
from tcg.models import db,ServiceCategory,ServiceSubcategory,Admin,QuoteRequest,Staff,ContactUs
from tcg.form import AdminLoginForm,QuoteForm
from tcg.utils import generate_temp_password 

@app.after_request
def after_request(resp):
    resp.headers['Cache-Control']='no-cache,no-store,must-revalidate'
    return resp

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'adminonline' not in session:
            flash("Please login as admin to access that page.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapped


    # This is my admin home page route 
@app.route('/admin/',methods=['GET','POST'])
def admin_home():
    admin_id = session.get('adminonline')

    if not admin_id:
        flash("You must be logged in as an admin.", category='error')
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html')

#this is the admin dashboard route
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_categories = ServiceCategory.query.count()
    total_subcategories = ServiceSubcategory.query.count()
    total_quotes = QuoteRequest.query.count()

    recent_quotes = QuoteRequest.query.order_by(QuoteRequest.id.desc()).limit(5).all()

    return render_template("admin/dashboard.html",
                           total_categories=total_categories,
                           total_subcategories=total_subcategories,
                           total_quotes=total_quotes,
                           recent_quotes=recent_quotes)



    # This is my admin login route 
@app.route('/admin/login/', methods=['POST', 'GET'])
def admin_login():
    adminloginform=AdminLoginForm()
    if request.method=='GET':
        return render_template('admin/admin_login.html',adminloginform=adminloginform)
    else:
        if adminloginform.validate_on_submit(): #this is where they login and i validate thier details
            username=adminloginform.username.data
            password=adminloginform.password.data
            admin_details=Admin.query.filter(Admin.admin_username==username).first()

            if admin_details: #means the username is correct and they can proceed 
                stored_password=admin_details.admin_pwd
                check_password= check_password_hash(stored_password,password)
                if check_password ==True:
                    session.clear()
                    session['adminonline']=admin_details.admin_id
                    return redirect('/admin/dashboard')
                else: #comes here if the password is wrong 
                    flash('Invalid Login Password', category='error')
                    return redirect(url_for('admin_login'))
            else: #come to this if the username is wrong 
                flash('Invalid Username, Try Again', category='error')
                return redirect(url_for('admin_login'))
        else:
            return render_template('admin/admin_login.html',adminloginform=adminloginform)


        # this is my admin logout route
@app.route('/admin/logout/', methods=['POST', 'GET'])
def admin_logout():
    if session.get('adminonline')!=None:
        session.pop('adminonline')   
    return redirect('/admin/login/')



# this is the route to manage staffs

@app.route('/admin/manage-staff/', methods=['GET', 'POST'])
# @admin_required
def admin_manage_staff():
    """
    GET: show list of staff and add form
    POST: handle add-staff form (form_type='add_staff')
    """
    if request.method == "POST":
        form_type = request.form.get('form_type')
        if form_type == 'add_staff':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            role = request.form.get('role', '').strip()
            status = request.form.get('status', 'active').strip()
            password = request.form.get('password', '').strip()

            if not full_name or not email or not role:
                flash("Name, email and role are required.", "danger")
                return redirect(url_for('admin_manage_staff'))

            # prevent duplicate email
            if Staff.query.filter_by(email=email).first():
                flash("A staff account with that email already exists.", "danger")
                return redirect(url_for('admin_manage_staff'))

            # if password not provided, generate a temp one
            generated_pw = None
            if not password:
                generated_pw = generate_temp_password(10)
                password_to_set = generated_pw
            else:
                password_to_set = password

            new_staff = Staff(
                full_name=full_name,
                email=email,
                phone=phone,
                role=role,
                status=status
            )
            new_staff.set_password(password_to_set)
            db.session.add(new_staff)
            db.session.commit()

            if generated_pw:
                flash(f"Staff created. Temporary password: {generated_pw}", "success")
                # OPTIONAL: send email to staff with the password here
            else:
                flash("Staff created successfully.", "success")

            return redirect(url_for('admin_manage_staff'))

    # GET: render page
    staff_list = Staff.query.order_by(Staff.full_name).all()
    roles = ['engineer', 'plumber', 'electrician', 'supervisor'] 
    return render_template('admin/manage_staff.html', staff_list=staff_list, roles=roles)


# this is the route to edit staffs 

@app.route('/admin/edit-staff/<int:id>/', methods=['GET', 'POST'])
def admin_edit_staff(id):
    staff = Staff.query.get_or_404(id)

    if request.method == "POST":
        staff.full_name = request.form.get('full_name', staff.full_name).strip()
        staff.email = request.form.get('email', staff.email).strip().lower()
        staff.phone = request.form.get('phone', staff.phone).strip()
        staff.role = request.form.get('role', staff.role).strip()
        staff.status = request.form.get('status', staff.status).strip()

        # optional: allow admin to set a new password
        new_password = request.form.get('password', '').strip()
        if new_password:
            staff.set_password(new_password)

        db.session.commit()
        flash("Staff updated successfully.", "success")
        return redirect(url_for('admin_manage_staff'))

    roles = ['engineer', 'plumber', 'electrician', 'supervisor', 'admin']
    return render_template('admin/edit_staff.html', staff=staff, roles=roles)

# route to delete staff 

@app.route('/admin/delete-staff/<int:id>/')
@admin_required
def admin_delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    flash("Staff deleted.", "success")
    return redirect(url_for('admin_manage_staff'))



@app.route('/admin/manage-services/', methods=['GET', 'POST'])
def admin_manage_services():
    categories = ServiceCategory.query.all()
    subcategories = ServiceSubcategory.query.all()

    # ADD CATEGORY
    if request.method == 'POST' and request.form.get('form_type') == 'category':
        name = request.form.get('name')
        if name:
            cat = ServiceCategory(name=name)
            db.session.add(cat)
            db.session.commit()
        return redirect(url_for('admin_manage_services'))

    # ADD SUBCATEGORY
    if request.method == 'POST' and request.form.get('form_type') == 'subcategory':
        name = request.form.get('name')
        category_id = request.form.get('category_id')

        sub = ServiceSubcategory(name=name, category_id=category_id)
        db.session.add(sub)
        db.session.commit()

        return redirect(url_for('admin_manage_services'))

    return render_template('admin/manage_services.html',
                           categories=categories,
                           subcategories=subcategories)

# This is the admin delete category route
@app.route('/admin/delete-category/<int:id>/')
def admin_delete_category(id):
    cat = ServiceCategory.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return redirect(url_for('admin_manage_services'))


# this is the admin delete sub category 
@app.route('/admin/delete/subcat/<int:id>/')
def admin_delete_subcat(id):
    sub=ServiceSubcategory.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for('admin_manage_services'))


# admin view quotes route

@app.route('/admin/view-quotes/')
def admin_view_quotes():
    """
    Fetch all quote requests and send them to the admin_view_quotes.html page.
    Admin can see:
    - Customer name, email, phone
    - Selected service category & subcategory
    - Message and date submitted
    """

    quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).all()
    all_staff = Staff.query.filter_by(status='active').all()  # only active staff
    return render_template('admin/view_quotes.html', quotes=quotes,all_staff=all_staff)


@app.route('/admin/view/contact/')
def admin_contact_msg():
    """
    Fetch all quote requests and send them to the admin_view_quotes.html page.
    Admin can see:
    - Customer name, email, phone
    - Selected service category & subcategory
    - Message and date submitted
    """

    contact = ContactUs.query.order_by(ContactUs.date_sent.desc()).all()
    all_staff = Staff.query.filter_by(status='active').all()  # only active staff
    return render_template('admin/view_contact.html', contact=contact,all_staff=all_staff)


# to assign staff to contact user that dropped the quote

@app.route('/admin/assign-staff/<int:request_id>', methods=['POST'])
def admin_assign_staff(request_id):
    if 'adminonline' not in session:
        return redirect(url_for('admin_login'))

    staff_id = request.form.get('staff_id')
    quote = QuoteRequest.query.get_or_404(request_id)

    if not staff_id:
        flash("Please select a staff member.", "danger")
        return redirect(url_for('admin_view_quotes'))

    # Assign staff
    quote.assigned_staff_id = staff_id
    quote.assignment_status = "assigned"  # 🔥 THIS is what fixes your issue!

    db.session.commit()

    flash(f"Quote no{quote.id} assigned successfully! to {quote.assigned_staff.full_name}!!", "success")
    return redirect(url_for('admin_view_quotes'))



# to assign staff to contact user that dropped the contact us

@app.route('/admin/contact/assign/staff/<int:request_id>', methods=['POST'])
def admin_contact_assign_staff(request_id):
    if 'adminonline' not in session:
        return redirect(url_for('admin_login'))

    staff_id = request.form.get('staff_id')
    quote = ContactUs.query.get_or_404(request_id)

    if not staff_id:
        flash("Please select a staff member.", "danger")
        return redirect(url_for('admin_view_contact'))

    # Assign staff
    quote.assigned_staff_id = staff_id
    quote.contact_status = "assigned"  # 🔥 THIS is what fixes your issue!

    db.session.commit()

    flash(f"Quote no{quote.id} assigned successfully! to {quote.assigned_staff.full_name}!!", "success")
    return redirect(url_for('admin_contact_msg'))




# admin get quotes route

@app.route('/get-quote/', methods=['GET', 'POST'])
def get_quote():
    form = QuoteForm()

    # Add placeholders
    form.category.choices = [(0, "Select Category")] + [
        (c.id, c.name) for c in ServiceCategory.query.all()
    ]
    form.subcategory.choices = [(0, "Select Subcategory")]

    if request.method == "POST":
        # Reload subcategories for validation
        if form.category.data:
            subcats = ServiceSubcategory.query.filter_by(category_id=form.category.data).all()
            form.subcategory.choices = [(0, "Select Subcategory")] + [
                (s.id, s.name) for s in subcats
            ]

        if form.validate_on_submit():
            # Get actual category and subcategory names
            category = ServiceCategory.query.get(form.category.data)
            subcategory = ServiceSubcategory.query.get(form.subcategory.data)

            # Save quote in DB
            q = QuoteRequest(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                category_id=form.category.data,
                subcategory_id=form.subcategory.data,
                message=form.message.data
            )
            db.session.add(q)
            db.session.commit()

            # Send email to admin
            msg = Message(
                subject="New Quote Request - TCG",
                recipients=["michealerinola9@gmail.com"],  # Replace with your email
            )

            msg.body = f"""
A new quote request has been submitted.

Name: {form.name.data}
Email: {form.email.data}
Phone: {form.phone.data}
Category: {category.name if category else 'N/A'}
Subcategory: {subcategory.name if subcategory else 'N/A'}
status: {q.assignment_status}

Message:
{form.message.data}

Regards,
 Tomide Construction Group
"""
            mail.send(msg)

            flash("Your quote request has been sent successfully! You will be contacted soon.", "success")
            return redirect(url_for('get_quote'))

        else:
            flash("Please correct the errors in the form.", "danger")

    return render_template('users/index.html', form=form)











# route to create services 

@app.route('/create/service_categories/')
def create_service_categories():
    s1 = ServiceCategory(name='Building Construction')
    s2 = ServiceCategory(name='Civil Engineering')
    s3 = ServiceCategory(name='Electrical Services')
    s4 = ServiceCategory(name='Plumbing Services')
    s5 = ServiceCategory(name='Painting & Finishing')
    s6 = ServiceCategory(name='Architectural & Design')
    s7 = ServiceCategory(name='Renovation & Remodeling')
    s8 = ServiceCategory(name='Structural Repairs')

    db.session.add_all([s1, s2, s3, s4, s5, s6, s7, s8])
    db.session.commit()

    return "Service Categories Created"

# route to load them 
@app.route('/load-subcategories/<int:category_id>/')
def load_subcategories(category_id):
    subs = ServiceSubcategory.query.filter_by(category_id=category_id).all()
    data = [{'id': s.id, 'name': s.name} for s in subs]
    return jsonify(data)

# route to create subcat 
@app.route('/create/service_subcategories/')
def create_service_subcategories():

    # Building Construction
    sc1  = ServiceSubcategory(category_id=1, name='Residential Building')
    sc2  = ServiceSubcategory(category_id=1, name='Commercial Building')
    sc3  = ServiceSubcategory(category_id=1, name='Foundation Construction')
    sc4  = ServiceSubcategory(category_id=1, name='Structural Framing')

    # Civil Engineering
    sc5  = ServiceSubcategory(category_id=2, name='Road Construction')
    sc6  = ServiceSubcategory(category_id=2, name='Drainage Construction')
    sc7  = ServiceSubcategory(category_id=2, name='Bridge & Culvert Works')
    sc8  = ServiceSubcategory(category_id=2, name='Site Preparation')

    # Electrical Services
    sc9  = ServiceSubcategory(category_id=3, name='Electrical Installation')
    sc10 = ServiceSubcategory(category_id=3, name='Wiring & Rewiring')
    sc11 = ServiceSubcategory(category_id=3, name='Solar Power Installation')
    sc12 = ServiceSubcategory(category_id=3, name='Generator Installation')

    # Plumbing Services
    sc13 = ServiceSubcategory(category_id=4, name='Pipe Installation')
    sc14 = ServiceSubcategory(category_id=4, name='Bathroom Fittings')
    sc15 = ServiceSubcategory(category_id=4, name='Water Tank Installation')
    sc16 = ServiceSubcategory(category_id=4, name='Leak Repairs')

    # Painting & Finishing
    sc17 = ServiceSubcategory(category_id=5, name='Interior Painting')
    sc18 = ServiceSubcategory(category_id=5, name='Exterior Painting')
    sc19 = ServiceSubcategory(category_id=5, name='POP Ceiling')
    sc20 = ServiceSubcategory(category_id=5, name='Tiling & Flooring')

    # Architectural & Design
    sc21 = ServiceSubcategory(category_id=6, name='Architectural Design')
    sc22 = ServiceSubcategory(category_id=6, name='3D Modeling')
    sc23 = ServiceSubcategory(category_id=6, name='Building Plan Approval')
    sc24 = ServiceSubcategory(category_id=6, name='Land Surveying')

    # Renovation & Remodeling
    sc25 = ServiceSubcategory(category_id=7, name='Home Renovation')
    sc26 = ServiceSubcategory(category_id=7, name='Office Remodeling')
    sc27 = ServiceSubcategory(category_id=7, name='Partial Upgrades')
    sc28 = ServiceSubcategory(category_id=7, name='Space Extension')

    # Structural Repairs
    sc29 = ServiceSubcategory(category_id=8, name='Crack Repairs')
    sc30 = ServiceSubcategory(category_id=8, name='Reinforcement Works')
    sc31 = ServiceSubcategory(category_id=8, name='Foundation Repairs')
    sc32 = ServiceSubcategory(category_id=8, name='Concrete Restoration')

    db.session.add_all([
        sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8,
        sc9, sc10, sc11, sc12, sc13, sc14, sc15, sc16,
        sc17, sc18, sc19, sc20, sc21, sc22, sc23, sc24,
        sc25, sc26, sc27, sc28, sc29, sc30, sc31, sc32
    ])

    db.session.commit()
    return "Service Subcategories Created"

