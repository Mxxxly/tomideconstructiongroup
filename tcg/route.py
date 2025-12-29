import os
from datetime import datetime
from flask_mail import Message
from flask import render_template,redirect,request,url_for,make_response,session,flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from tcg import app,csrf,mail
from tcg.models import db,ServiceCategory,ServiceSubcategory,ContactUs
from tcg.form import QuoteForm,ContactForm


@app.route('/')
def home_page():
    form = QuoteForm()

    # Load categories
    categories = ServiceCategory.query.all()
    form.category.choices =  [(c.id, c.name) for c in categories]

    # Leave subcategory empty until a category is selected
    form.subcategory.choices = []

    return render_template('users/index.html', form=form)


@app.route('/get_subcategories/<int:category_id>')
def get_subcategories(category_id):
    subs = ServiceSubcategory.query.filter_by(category_id=category_id).all()
    return jsonify([{"id": s.id, "name": s.name} for s in subs])

@app.route('/about/')
def about():
    return render_template('users/about.html')

@app.route('/services/')
def services():
    return render_template('users/services.html')

@app.route('/projects/')
def projects():
    return render_template('users/projects.html')

# @app.route('/blog/')
# def blog():
#     return render_template('users/blog.html')


@app.route('/contact/', methods=['GET','POST'])
def contact():
    contact= ContactForm()
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

    return render_template('users/contact.html',contact=contact)