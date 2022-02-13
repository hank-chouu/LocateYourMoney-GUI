from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user

import os

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(16).hex()

    from .views import views
    from .auth import auth, user_dict, User
    
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    
    
    @login_manager.user_loader
    def user_loader(name):  
        
        if name not in user_dict:
            return

        user = User()  
        user.id = name
        return user


    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    return app

