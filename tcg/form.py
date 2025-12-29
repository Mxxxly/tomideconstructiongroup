from flask_wtf import FlaskForm
from wtforms import StringField, EmailField,PasswordField,SubmitField,TelField,TextAreaField,FileField,DateField, RadioField,DecimalField,IntegerField,SelectField,MultipleFileField,SelectMultipleField
from wtforms.validators import DataRequired,Email,Length,EqualTo,Optional,NumberRange
from flask_wtf.file import FileAllowed,FileRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ServiceCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class ServiceSubcategoryForm(FlaskForm):
    category = SelectField('Category', coerce=int)
    name = StringField('Subcategory Name', validators=[DataRequired()])
    submit = SubmitField('Add Subcategory')



class QuoteForm(FlaskForm):
    category = SelectField("Category", coerce=int)
    subcategory = SelectField("Subcategory", coerce=int)
    name = StringField("Name")
    phone = StringField('Phone')
    email = StringField("Email")
    message = TextAreaField("Message")
    submit = SubmitField("Get Quote")



class ContactForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    phone = TelField("Phone Number", validators=[DataRequired(), Length(min=5, max=20)])
    message= TextAreaField('Message', validators=[DataRequired()])
    contact_method = RadioField('Preferred Contact Method',choices=[('call', 'Call'), ('text', 'Text')],validators=[DataRequired()])
    submit = SubmitField('Send Message')


class AdminLoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()] )
    submit = SubmitField('Login')