from flask import Flask
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

csrf=CSRFProtect()
mail = Mail()

def create_app():
    from tcg import config
    from tcg.models import db
    app=Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile('config.py',silent=True)
    app.config.from_object(config.DevelopmentConfig)
    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    Migrate(app,db)
    return app

app=create_app()

print("MAIL SERVER:", app.config.get("MAIL_SERVER"))
print("MAIL PORT:", app.config.get("MAIL_PORT"))
print("MAIL USER:", app.config.get("MAIL_USERNAME"))
print("MAIL PASS SET:", bool(app.config.get("MAIL_PASSWORD")))

from tcg import route,admin_route,staff_route
from tcg import models,form
