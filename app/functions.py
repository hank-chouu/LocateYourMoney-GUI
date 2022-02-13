from calendar import c
from datetime import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .google_drive import downloadFile


log_file_id = '1ARGlhdeMGqaJ1gGslbV1zWO9fFhnlsy3'
user_file_id = '1obX_BMPSTeL-VeG8pjuLOKPFXunFiio1'


downloadFile('log.json', log_file_id)
downloadFile('user.json', user_file_id)
with open('user.json', 'r') as f:
    user_dict = json.load(f)
with open('log.json', 'r') as f:
    log = json.load(f)

color = ['#1496BB', '#EBC944', '#F58B4C', '#829356', '#9A2617']

class Custom_plot(object):

    def __init__(self, user, log):
        self._user_dict = user
        self._user_log = log

    def _get_account_list(self):
        
        # crypto 0, bank 1
        account_list = [[],[]]
        for n, v in self._user_dict['info'].items():
            if v['Provider'] in ['Ftx', 'Max']:
                account_list[0].append(n)
            else:
                account_list[1].append(n)
                
        return account_list


    # return 2 lists
    def _get_recent_dates_logs(self):
        
        date_list0 = []
        date_list1 = []
        recent_log = []
        
        for n, v in self._user_log.items():
            date = datetime.strptime(n, '%Y/%m/%d')
            date_list0.append(date)
            
        date_list0.sort()
        for i in date_list0:
            date_list1.append(datetime.strftime(i, '%Y/%m/%d'))
            
        length = 4 if len(date_list1) > 5 else len(date_list1)
        recent_date = date_list1[0:length]
        
        for date in recent_date:
            recent_log.append(self._user_log[date])
            
        return recent_date, recent_log

    # return 2 df

    def _get_balances(self, recent_dates, recent_logs, accounts):
        
        crypto_balance = {'Date':recent_dates}
        bank_balance = {'Date':recent_dates}
        
        for acc in accounts[0]:
            
            account_log = []
            for i in range(len(recent_dates)):
                for key, values in recent_logs[i].items():
                    if acc in key:
                        if 'total' in key:
                            account_log.append(values)
                        
            crypto_balance[acc] = account_log
            
            
        for acc in accounts[1]:
            
            account_log = []
            for i in range(len(recent_dates)):
                for key, values in recent_logs[i].items():
                    if acc in key:
                        account_log.append(values)
                        
            bank_balance[acc] = account_log
        
        crypto_balance = pd.DataFrame(crypto_balance)
        crypto_balance = crypto_balance.set_index('Date')
        crypto_balance['Total'] = crypto_balance.sum(axis=1)
        
        bank_balance = pd.DataFrame(bank_balance)
        bank_balance = bank_balance.set_index('Date')
        bank_balance['Total'] = bank_balance.sum(axis=1)
        
        return crypto_balance, bank_balance

    # input: most recent one-day-log of an user
    # return: coins as col, exchange a row

    # e.g., recent_log = recent_logs[0]
                
    def _most_recent_crypto(self, recent_log):
        
        df = pd.DataFrame()
        flag=0
        
        for key, v in recent_log.items():
            
            if 'coin' in key:
                if flag==0:
                    series = pd.Series(v, name = key.replace('_coin', ''))
                    index = list(series.index)
                    new_index = [x.upper() for x in index]
                    series.index = new_index
                    df = pd.DataFrame(series).transpose()
                    flag=1
                else:
                    series = pd.Series(v, name = key.replace('_coin', ''))
                    index = list(series.index)
                    new_index = [x.upper() for x in index]
                    series.index = new_index
                    row = pd.DataFrame(series).transpose()
                    df = pd.concat([df, row], sort=False).fillna(0)
                
        cols = df.columns      
        df[cols] = df[cols].apply(np.floor)
        df = df.loc[:, (df != 0).any(axis=0)]
        
        
        return df.transpose()

    def grouped_bar(self):

        accounts_list = self._get_account_list()
        recent_date, recent_log = self._get_recent_dates_logs()
        crypto_balance, bank_balance = self._get_balances(recent_date, recent_log, accounts_list)
        current_crypto = self._most_recent_crypto(recent_log[-1])

        fig = plt.Figure()
        axis = fig.add_subplot(1,1,1)
        current_crypto.plot.bar(rot=0, color = color, ax = axis)

        return fig

    def lines_chart(self):

        accounts_list = self._get_account_list()
        recent_date, recent_log = self._get_recent_dates_logs()
        crypto_balance, bank_balance = self._get_balances(recent_date, recent_log, accounts_list)
        

        fig = plt.Figure()
        axis = fig.add_subplot(1,1,1)

        if len(bank_balance.columns) == 2:
            bank_balance.iloc[:,0].plot.line(color = color,ax = axis)
        else:
            bank_balance.plot.line(color = color, ax = axis)
            
        fig.legend(loc = 'upper left')
        return fig

    def get_recent_balance(self):

        accounts_list = self._get_account_list()
        recent_date, recent_log = self._get_recent_dates_logs()
        crypto_balance, bank_balance = self._get_balances(recent_date, recent_log, accounts_list)

        bank_recent = bank_balance.iloc[-1, :].to_frame()
        bank_recent.reset_index(inplace= True)
        bank_recent.rename({recent_date[-1]:'TWD', 'index':'Account'}, axis = 1, inplace=True)

        crypto_recent = crypto_balance.iloc[-1, :].to_frame()
        crypto_recent = crypto_recent.round(2)
        crypto_recent.reset_index(inplace = True)
        crypto_recent.rename({recent_date[-1]:'USD', 'index':'Account'}, axis = 1, inplace=True)

        return bank_recent, crypto_recent

    def get_latest_date(self):

        accounts_list = self._get_account_list()
        recent_date, recent_log = self._get_recent_dates_logs()

        return recent_date[-1]

    def get_pie(self, type):

        accounts_list = self._get_account_list()
        recent_date, recent_log = self._get_recent_dates_logs()
        crypto_balance, bank_balance = self._get_balances(recent_date, recent_log, accounts_list)

        if type.lower() == 'crypto':
            selected_df = crypto_balance
        else:
            selected_df = bank_balance

        labels = selected_df.columns[:-1]
        

        if len(labels) > 1:

            labels = tuple(labels)
            values = selected_df.iloc[-1, :-1].to_list()
            explode = [0]*len(labels)
            explode[1] = 0.1
            explode = tuple(explode)

            fig, ax = plt.subplots()
            ax.pie(values, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, colors=color, textprops={'fontsize': 16})
            ax.axis('equal')

        
            
        else:

            value = [selected_df.iloc[-1, 0]]
            labels = [labels[0]]
            fig, ax = plt.subplots()
            ax.pie(value, labels=labels, autopct='%1.1f%%', shadow=True, startangle=271, colors=color, textprops={'fontsize': 16})
            ax.axis('equal')

        return fig




