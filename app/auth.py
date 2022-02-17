from flask import Blueprint, redirect, render_template, request, flash, session, url_for
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import json
from .functions import Custom_plot, user_dict, log, user_file_id, log_file_id
from .google_drive import updateFile


auth = Blueprint('auth', __name__)

class User(UserMixin):  
        pass


now_support_bank = ['Ctbc']
now_support_crypto = ['Ftx', 'Max']

now_support = now_support_crypto + now_support_bank



@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nickname = request.form.get('signupname')
        username = request.form.get('signupusername')
        password = request.form.get('signuppassword')

        flag = 0
        flag2 = 0
        
        for name, values in user_dict.items():
            existed_name = values['username']
            if existed_name == username:
                flag=1
            if nickname == name:
                flag2=1

        if flag2==1:
            flash('You are already registered. Choose another nickname.', category='error')
        elif flag==1:
            flash('User name already existed.', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            user_dict.update({nickname:{'username':username,
                                        'password':password,
                                        'info':{}}})
            
            updateFile('user.json', user_dict, user_file_id)

            user = User() 
            user.id = username
            
            login_user(user, remember=True)
            flash('Account created successfully!', category='success')            
            return redirect(url_for('views.home'))

    return render_template("signup.html")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('loginusername')
        password = request.form.get('loginpassword')

        flag=0
        fetch_password = None
        fetch_name = None

        # change to hash password in the future

        for name, values in user_dict.items():
            existed_name = values['username']
            if existed_name == username:
                flag=1
                fetch_password = values['password']
                fetch_name = name

        if flag==0:
            flash('User does not exist.', category='error')
        elif fetch_password!= password:
            flash('Incorrect password. Try again.', category='error')
        else:
            # return name to fetch log
            user = User() 
            user.id = fetch_name
            login_user(user)
            flash('Login successfully!', category='success')

            return redirect(url_for('views.home'))

            

    return render_template("login.html")

@auth.route('/add-provider', methods=['GET', 'POST'])
@login_required
def add_account():

    existed_account_names = []
    for n, v in user_dict[current_user.id]['info'].items():
        existed_account_names.append(n)

    
    if request.method == 'POST':

        custom_name = request.form.get('account_name')

        if custom_name in existed_account_names:
            flash('You already picked this name. Choose another one.', category='error')
        else:
            
            provider = request.form.get('provider')

            if provider in now_support_bank:
                id = request.form.get('id')
                usercode = request.form.get('usercode')
                password = request.form.get('password')
                
                # update to user.json
                user_dict[current_user.id]['info'].update({
                    custom_name:{ 'Provider': provider,
                            'Type': 'Bank', 
                            'Login_info':{
                                'ID':id, 
                                'User code':usercode, 
                                'Password':password
                            }

                    }
                })
                

            else:
                api_key = request.form.get('api_key')
                api_secret = request.form.get('api_secret')
                custom_name = request.form.get('account_name')
                # update to user.json
                user_dict[current_user.id]['info'].update({
                    custom_name:{
                        'Provider':provider, 
                        'Type':'Crypto',
                        'Login_info':{
                            'API_KEY':api_key,
                            'API_SECRET':api_secret
                        }
                    }
                })
                
            
            updateFile('user.json', user_dict, user_file_id)
            flash('Provider created successfully!', category='success')

            return redirect(url_for('auth.add_account'))

    return render_template('add_provider.html', now_support = now_support, user = current_user)

# logout

@auth.route('/logout-confirm-home', methods = ['POST', 'GET'])
@login_required
def logout_confirm():

    ID = current_user.id
    
    if ID not in log:

        if len(user_dict[ID]['info']) == 0:

            return render_template('logout_modal.html', 
                                    type = 0, 
                                    username = ID)
        else:

            return render_template('logout_modal.html', 
                                    type = 1, 
                                    username = ID)

    else:

        balance = Custom_plot(user_dict[ID], log[ID])
        bank_recent, crypto_recent = balance.get_recent_balance()
        latest_update = balance.get_latest_date()

        return render_template('logout_modal.html',
                                type = 2,  
                                username = ID, 
                                bank=bank_recent.to_dict(orient='records'),
                                crypto=crypto_recent.to_dict(orient='records'),
                                last_date = latest_update)


@auth.route('/logout-confirm-settings', methods = ['POST', 'GET'])
@login_required
def logout_confirm2():

    accounts = []
    for k,v in user_dict[current_user.id]['info'].items():
        accounts.append(k)
    return render_template('logout_modal_settings.html', accounts = accounts)


@auth.route('/logout-confirm-add-provider', methods = ['POST', 'GET'])
@login_required
def logout_confirm3():
    return render_template('logout_modal_add_provider.html', now_support = now_support, user = current_user)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# settings


@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    accounts = []
    for k,v in user_dict[current_user.id]['info'].items():
        accounts.append(k)

    if request.method == 'POST':

        acc = request.form.get('provider')
        session['acc'] = acc

        return render_template('delete_provider_modal.html', accounts = accounts)

    

    return render_template('settings.html', accounts = accounts)    
        

    
        
# delete a provider
@auth.route('/delete-provider', methods=["POST"])
@login_required
def delete_provider():

    name = current_user.id
    acc = session.get('acc',None)

    user_dict[name]['info'].pop(acc)
    updateFile('user.json', user_dict, user_file_id)
    
    return redirect(url_for('auth.settings'))



@auth.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_user():

    name = current_user.id
    user_dict.pop(name)
    log.pop(name)

    updateFile('user.json', user_dict, user_file_id)
    updateFile('log.json', log, log_file_id)

    logout_user()
    
    return redirect(url_for('auth.login'))


@auth.route('delete-user-confirm', methods=['GET', 'POST'])
@login_required
def delete_user_confirm():
    return render_template('delete_user_modal.html')

