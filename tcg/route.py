import os
from datetime import datetime
from flask_mail import Message
from flask import render_template,redirect,request,url_for,make_response,session,flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from tcg import app,csrf,mail
from tcg.models import db,ServiceCategory,ServiceSubcategory,ContactUs
from tcg.form import QuoteForm,ContactForm


# @app.route('/')
# def home_page():
#     form = QuoteForm()

#     # Load categories
#     categories = ServiceCategory.query.all()
#     form.category.choices =  [(c.id, c.name) for c in categories]

#     # Leave subcategory empty until a category is selected
#     form.subcategory.choices = []

#     return render_template('users/index.html', form=form)


@app.route('/')
def home_page():
    form = QuoteForm()

    # Load categories
    categories = ServiceCategory.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]

    # Default: empty subcategory choices
    form.subcategory.choices = []

    # Check if category/subcategory are in query params
    category_id = request.args.get('category', type=int)
    subcategory_id = request.args.get('subcategory', type=int)

    selected_category = None
    selected_subcategory = None

    if category_id:
        selected_category = ServiceCategory.query.get(category_id)
        if selected_category:
            form.category.data = selected_category.id
            # Populate subcategories for this category
            form.subcategory.choices = [(s.id, s.name) for s in selected_category.subcategories]

    if subcategory_id:
        selected_subcategory = ServiceSubcategory.query.get(subcategory_id)
        if selected_subcategory:
            form.subcategory.data = selected_subcategory.id

    return render_template('users/index.html', form=form, selected_category=selected_category, selected_subcategory=selected_subcategory, categories=categories)


@app.route('/get_subcategories/<int:category_id>')
def get_subcategories(category_id):
    subs = ServiceSubcategory.query.filter_by(category_id=category_id).all()
    return jsonify([{"id": s.id, "name": s.name} for s in subs])

@app.route('/about/')
def about():
    categories = ServiceCategory.query.all()

    return render_template('users/about.html',categories=categories)

@app.route('/services/')
def services():
    categories = ServiceCategory.query.all()

    return render_template('users/services.html',categories=categories)

@app.route('/projects/')
def projects():
    categories = ServiceCategory.query.all()

    return render_template('users/projects.html',categories=categories)

# @app.route('/blog/')
# def blog():
#     return render_template('users/blog.html')


@app.route('/contact/', methods=['GET','POST'])
def contact():
    contact= ContactForm()
    categories = ServiceCategory.query.all()

    if request.method == 'POST':
        if contact.validate_on_submit():
            name= contact.name.data
            email = contact.email.data
            message= contact.message.data
            contact_method=contact.contact_method.data
            phone = contact.phone.data

            co=ContactUs(name=name,email=email,message=message,contact_method=contact_method,phone=phone)
            db.session.add(co)
            db.session.commit()

            # send email to admin email
            msg=Message(
                subject= "New Contact Request From User - TCG",
                recipients=["michealerinola9@gmail.com"]
            )
            msg.body = f"""
            A new Contact Form has been Submitted 
            Name: 
            {name}
            Email: 
            {email}
            Phone Number: 
            {phone}
            Contact_Method: 
            {contact_method}


            Message:
                {message}

            Regards, 
                Tomide Construction Group
            """
            mail.send(msg)
            flash('You Message has been sent and you will recieve a feedback', 'success')
            return redirect(url_for("contact"))
        else:
            flash('Please correct the errors in the form.', 'danger ')

    return render_template('users/contact.html',contact=contact,categories=categories)