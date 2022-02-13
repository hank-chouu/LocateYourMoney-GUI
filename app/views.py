from flask import Blueprint, redirect, render_template, request, flash, url_for, Response
from flask_login import login_required, current_user
import json
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .auth import now_support_bank, now_support_crypto, user_dict
from .functions import Custom_plot, user_dict, log



views = Blueprint('views', __name__)



'''
accounts_list = get_account_list(user_dict[current_user.id])
recent_date, recent_log = get_recent_dates_logs(log[current_user.id])
crypto_balance, bank_balance = get_balances(recent_date, recent_log, accounts_list)
current_crypto = most_recent_crypto(recent_log[0])
'''




@views.route('/crypto-bar-plot.png')
def crypto_plot():

    ID = current_user.id
    balance = Custom_plot(user_dict[ID], log[ID])
    fig = balance.grouped_bar()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@views.route('/bank-changes-plot.png')
def bank_changes():

    ID = current_user.id
    balance = Custom_plot(user_dict[ID], log[ID])
    fig = balance.lines_chart()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')  

@views.route('/crypto-pie-chart.png')
def crypto_pie():

    ID = current_user.id
    balance = Custom_plot(user_dict[ID], log[ID])
    fig = balance.get_pie('crypto')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')   

@views.route('/bank-pie-chart.png')
def bank_pie():

    ID = current_user.id
    balance = Custom_plot(user_dict[ID], log[ID])
    fig = balance.get_pie('bank')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')



@views.route('/')
@login_required
def home():

    ID = current_user.id
    
    if len(user_dict[ID]['info']) == 0:

        if ID not in log:

            return render_template('home.html', 
                                    type = 1, 
                                    username = ID)
        else:
            balance = Custom_plot(user_dict[ID], log[ID])
            bank_recent, crypto_recent = balance.get_recent_balance()
            latest_update = balance.get_latest_date()

            return render_template('home.html', 
                                    type = 0, 
                                    username = ID,
                                    last_date = latest_update)

    else:

        balance = Custom_plot(user_dict[ID], log[ID])
        bank_recent, crypto_recent = balance.get_recent_balance()
        latest_update = balance.get_latest_date()

        return render_template('home.html',
                                type = 2,  
                                username = ID, 
                                bank=bank_recent.to_dict(orient='records'),
                                crypto=crypto_recent.to_dict(orient='records'),
                                last_date = latest_update)