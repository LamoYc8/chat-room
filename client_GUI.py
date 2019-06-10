import tkinter as tk
from tkinter import ttk, messagebox
import client as c 
import sys


class login_view(object):

    def __init__(self):
        
        self.root = tk.Tk()

        self.root.geometry()
        self.root.title('Login')

        self.intro_lb = tk.Label(self.root, text='Please Enter a Nick Name:\n')
        self.intro_lb.grid(row=0, column=0, sticky=tk.E)

        self.nick_name_lb = tk.Label(self.root, text='Nick Name: \n', font='Arial -14', fg='black')
        self.nick_name_lb.grid(row=1, column=0, sticky=tk.W)

        self.nameE = tk.Entry(self.root)
        self.nameE.grid(row=1, column=1)

        self.conn_bt = ttk.Button(self.root, text='Connect',command=self.check_login)
        self.conn_bt.grid(columnspan=2, sticky=tk.W)

        self.quit_bt = ttk.Button(self.root, text='Exit', command=self.confirm_to_quit)
        self.quit_bt.grid(columnspan=2, sticky=tk.W)
        
        self.root.mainloop()


    def confirm_to_quit(self):
        if tk.messagebox.askokcancel('','Are you sure to exit?'):
            self.root.quit()

    def _get_nickname(self):
        return self.nameE.get()

    def check_login(self):
        # controller for login functionality
        nameE = self._get_nickname()

        client = c.Client()

        try:
            while True:
                result = client.set_name(nameE)
                if result is True or result is False:
                    break
            if result == True:
                self.root.destroy()
                chat_view(client)
            elif result == False:
                tk.messagebox.showerror('', 'This nick name is occupied, please try another one!')
                # pop up a alert message box that ask the user to reset a nick name

        except (ConnectionRefusedError, ConnectionError, ConnectionResetError) as e:
            error_type, error_value, trace_back = sys.exc_info()
            print(error_value)
            sys.exit(1)
            raise
        except KeyboardInterrupt:
            print('keyboard interrput, exiting!')
            client.sel.close()


class chat_view(object): 
    def __init__(self, client):
        self.client = client

        self.root = tk.Tk()

        self.root.geometry()
        self.root.title('Chat-Room')

        # view layout

    pass

if __name__=='__main__':
    login_view()
    


