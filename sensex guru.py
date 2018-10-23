import quandl as q
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta 
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from tkinter import *
from tkinter import messagebox
import sqlite3 as sql

class LinearRegressionModel:

    def __init__(self):

        self.database = sql.connect('sensex_guru.db')
        self.cur = self.database.cursor()
        try:
            x = self.cur.execute(' Create table tickers (ticker varchar (20))')
        except:
            pass
        
        self.scr = Tk(className = 'Prediction')
        self.scr.state('zoomed')
        self.scr.resizable(0,0)

        Label(self.scr,text='Ticker', font=("default",20)).place(x=400,y=240)

        self.e=Entry(self.scr,font=("arial",30))
        self.e.place(x=550, y=240)
        self.e.bind('<Return>',self.enter)

        Label(self.scr,text='calculate data', font=("default",20)).place(x=370, y=308)

        self.e1 = Entry(self.scr, font=("default",30))
        self.e1.place(x=550, y=300)
        self.e1.bind('<Return>',self.enter)

        self.b = Button(self.scr, text = 'Predict', font=("default",20),relief='ridge', command=self.fun, width=27)
        self.b.place(x=550, y=380)
        self.b.bind('<Return>',self.enter)

        data_object = self.cur.execute('Select * from tickers')
        
        self.main_menu = Menu(self.scr)
        file_menu=Menu(self.main_menu,tearoff=0)
        history_menu=Menu(file_menu,tearoff=0)
        z=data_object.fetchall()
        if z != []:
            for i in z:
                history_menu.add_command(label=i[0], command = lambda :self.menu_fun(i[0]))
        file_menu.add_cascade(label="history",menu=history_menu)
        file_menu.add_command(label = 'exit', command = self.scr.destroy)
        self.main_menu.add_cascade(label="file",menu=file_menu)

        self.scr.config(menu=self.main_menu)
        self.scr.mainloop()

        

    def enter(self,event):
        self.fun()


    def menu_fun(self, string):
        self.e.insert(0, string)

    def fun(self):
        try:
            data=q.get(self.e.get(), auth_token='sC5Wo56ycV9DzzA_qg19')
            database_item = self.cur.execute("Select * from tickers where ticker = '{0}'".format(self.e.get()))
            if database_item.fetchall() == []:
                self.cur.execute("insert into tickers values('{0}')".format(self.e.get()))
                self.database.commit()
        except:
            messagebox.showerror('Message', "Can't get data")
            exit()
        data = data[['Adj_Open', 'Adj_High', 'Adj_Low', 'Adj_Close', 'Adj_Volume']]

        try:
            pct_ch = int(len(data)*(float(self.e1.get())/100))
        except:
            messagebox.showerror('Error', 'Please enter data limit between 1 to 100%\n (lesser the % greater the accuracy)')

        data['New_Close'] = data['Adj_Close'].shift(-pct_ch)
        x=data.drop('New_Close',1)
        x=scale(x)

        x1=x[:-pct_ch]
        x2=x[-pct_ch:]
        y=data.dropna().New_Close

        x_train, x_test, y_train, y_test = train_test_split(x1,y,test_size=0.3)
        try:
            alg=LinearRegression()
            alg.fit(x_train, y_train)
            score = alg.score(x_test, y_test)
        except:
            messagebox.showerror('Error', 'Please enter data limit between 1 to 100%\n (lesser the % greater the accuracy)')
        fore = alg.predict(x2)
        data['Forecast']=np.nan

        boolean = messagebox.askyesnocancel('Confirm', 'Accuracy is {0}%\n Do you wanna see graph ?'.format(score*100))
        if boolean:
            for i in fore:
                data.loc[data.iloc[-1].name+timedelta(days=1)] = [np.nan for i in range(6)]+[i]

            data['Adj_Close'].plot(c="g",label="Adj_close")
            data['Forecast'].plot(c="b",label="Predicted")
            plt.xlabel('Date')
            plt.ylabel('Close')
            plt.legend(loc='best')
            plt.show()
            self.scr.mainloop()
            
if __name__ == '__main__':
    LinearRegressionModel()
