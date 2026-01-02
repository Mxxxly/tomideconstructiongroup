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

# this is the staff login route 
@app.route('/staff/login/', methods=['GET', 'POST'])
def staff_login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        staff = Staff.query.filter_by(email=email).first()

        if staff and staff.check_password(password):

            if staff.status != "active":
                flash("Your account is inactive. Contact the administrator.", "danger")
                return redirect(url_for('staff_login'))

            # Save login to session
            session.clear()
            session['staff_id'] = staff.id

            return redirect(url_for('staff_dashboard'))

        flash("Invalid email or password", "danger")
        return redirect(url_for('staff_login'))

    return render_template('staff/staff_login.html')

# this is the staff dashboard route 
@app.route('/staff/dashboard/')
def staff_dashboard():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff = Staff.query.get(session['staff_id'])
    assigned_requests = QuoteRequest.query.filter_by(assigned_staff_id=staff.id).all()
    contact_assigned_requests= ContactUs.query.filter_by(assigned_staff_id=staff.id).all()
    pending_requests = [r for r in assigned_requests if r.assignment_status == "pending"]
    completed_requests = [r for r in assigned_requests if r.assignment_status == "completed"]
    contact_pending_requests = [r for r in contact_assigned_requests if r.contact_status == "assigned"]
    contact_completed_requests = [r for r in contact_assigned_requests if r.contact_status == "completed"]
    pending_requests_count = QuoteRequest.query.filter(
    QuoteRequest.assigned_staff_id == staff.id,
    QuoteRequest.assignment_status != "completed"
    ).count()

    contact_pending_requests_count = ContactUs.query.filter(
        ContactUs.assigned_staff_id == staff.id,
        ContactUs.contact_status != "completed"
    ).count()

    return render_template(
        'staff/staff_dashboard.html',
        staff=staff,
        assigned_requests=assigned_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,contact_assigned_requests=contact_assigned_requests,
        contact_pending_requests=contact_pending_requests,
        contact_completed_requests=contact_completed_requests,
        pending_requests_count=pending_requests_count,
        contact_pending_requests_count=contact_pending_requests_count
    )


@app.route('/view/quote-requests/')
def view_quote_request():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff = Staff.query.get(session['staff_id'])
    assigned_requests = QuoteRequest.query.filter_by(assigned_staff_id=staff.id).all()
    contact_assigned_requests= ContactUs.query.filter_by(assigned_staff_id=staff.id).all()
    pending_requests = [r for r in assigned_requests if r.assignment_status == "pending"]
    completed_requests = [r for r in assigned_requests if r.assignment_status == "completed"]
    contact_pending_requests = [r for r in contact_assigned_requests if r.contact_status == "assigned"]
    contact_completed_requests = [r for r in contact_assigned_requests if r.contact_status == "completed"]
    pending_requests_count = QuoteRequest.query.filter(
    QuoteRequest.assigned_staff_id == staff.id,
    QuoteRequest.assignment_status != "completed"
    ).count()

    contact_pending_requests_count = ContactUs.query.filter(
        ContactUs.assigned_staff_id == staff.id,
        ContactUs.contact_status != "completed"
    ).count()



    return render_template(
        'staff/view_quote_request.html',
        staff=staff,
        assigned_requests=assigned_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,
        contact_assigned_requests=contact_assigned_requests,
        contact_completed_requests=contact_completed_requests,
        contact_pending_requests=contact_pending_requests,
        pending_requests_count=pending_requests_count,
        contact_pending_requests_count=contact_pending_requests_count

    )



@app.route('/view/contact-requests/')
def view_contact_request():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff = Staff.query.get(session['staff_id'])
    assigned_requests = QuoteRequest.query.filter_by(assigned_staff_id=staff.id).all()
    contact_assigned_requests= ContactUs.query.filter_by(assigned_staff_id=staff.id).all()
    pending_requests = [r for r in assigned_requests if r.assignment_status == "pending"]
    completed_requests = [r for r in assigned_requests if r.assignment_status == "completed"]
    contact_pending_requests = [r for r in contact_assigned_requests if r.contact_status == "assigned"]
    contact_completed_requests = [r for r in contact_assigned_requests if r.contact_status == "completed"]
    pending_requests_count = QuoteRequest.query.filter(
    QuoteRequest.assigned_staff_id == staff.id,
    QuoteRequest.assignment_status != "completed"
    ).count()

    contact_pending_requests_count = ContactUs.query.filter(
        ContactUs.assigned_staff_id == staff.id,
        ContactUs.contact_status != "completed"
    ).count()


    return render_template(
        'staff/view_contact_request.html',
        staff=staff,
        assigned_requests=assigned_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,
        contact_assigned_requests=contact_assigned_requests,
        contact_completed_requests=contact_completed_requests,
        contact_pending_requests=contact_pending_requests,
        pending_requests_count=pending_requests_count,
        contact_pending_requests_count=contact_pending_requests_count

    )


@app.route('/test-mail')
def test_mail():
    msg = Message(
        subject="SendGrid Test",
        recipients=["michealerinola9@gmail.com"],
        body="If you received this, SendGrid SMTP is working 🎉"
    )
    mail.send(msg)
    return "Mail sent successfully"



    # This is the staff profile route
@app.route('/staff/profile/', methods=['GET', 'POST'])
def staff_profile():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff = Staff.query.get(session['staff_id'])

    if request.method == "POST":
        staff.full_name = request.form.get('full_name', staff.full_name).strip()
        staff.email = request.form.get('email', staff.email).strip().lower()
        staff.phone = request.form.get('phone', staff.phone).strip()

        new_password = request.form.get('password', '').strip()
        if new_password:
            staff.set_password(new_password)  # Use your model's set_password method

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('staff_profile'))

    return render_template('staff/staff_profile.html', staff=staff)


# this is the staff update request route 

@app.route('/staff/update-request/<int:id>/', methods=['GET', 'POST'])
def staff_update_request(id):
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff = Staff.query.get(session['staff_id'])
    request_item = QuoteRequest.query.get_or_404(id)

    if request_item.assigned_staff_id != staff.id:
        flash("You cannot update this request.", "danger")
        return redirect(url_for('staff_dashboard'))

    if request.method == "POST":
        new_status = request.form.get('status')
        if new_status:
            request_item.assignment_status = new_status
            db.session.commit()
            flash("Request status updated.", "success")
        return redirect(url_for('staff_dashboard'))

    return render_template('staff/staff_update_request.html', request_item=request_item)


@app.route('/staff/contact/update-request/<int:id>/', methods=['GET', 'POST'])
def staff_update_contact_request(id):
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    staff = Staff.query.get(session['staff_id'])
    request_item = ContactUs.query.get_or_404(id)

    if request_item.assigned_staff_id != staff.id:
        flash("You cannot update this contact request.", "danger")
        return redirect(url_for('staff_dashboard'))

    if request.method == "POST":
        new_status = request.form.get('status')
        if new_status:
            request_item.contact_status = new_status
            db.session.commit()
            flash("Request status updated.", "success")
        return redirect(url_for('view_contact_request'))

    return render_template('staff/staff_contact_update.html', request_item=request_item)



# this is the logout for staffs 

@app.route('/staff/logout/')
def staff_logout():
    session.pop('staff_id', None)
    session.pop('staff_role', None)
    return redirect(url_for('staff_login'))
