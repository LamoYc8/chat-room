import json
import sys
import time
from threading import Thread

from tkinter import ttk, messagebox
import tkinter as tk

import client as c 

class login_view(object):

    def __init__(self):
        
        self.client = None
        self.root = tk.Tk()
        self.root.geometry()
        self.root.title('Login')

        self.intro_lb = tk.Label(self.root, text='Please Enter a Nick Name:\n')
        self.intro_lb.grid(row=0, columnspan=2, sticky=tk.W)

        self.nick_name_lb = tk.Label(self.root, text='Nick Name:', font='Arial -14', fg='black')
        self.nick_name_lb.grid(row=1, sticky=tk.W)

        self.nameE = tk.Entry(self.root)
        self.nameE.grid(row=1, column=1)
        self.nameE.bind('<KeyPress-Return>', self._loginevent)

        self.conn_bt = ttk.Button(self.root, text='Connect',command=self.check_login)
        self.conn_bt.grid(columnspan=2, sticky=tk.W)

        self.quit_bt = ttk.Button(self.root, text='Exit', command=self.confirm_to_quit)
        self.quit_bt.grid(columnspan=2, sticky=tk.W)
        
        self.root.mainloop()


    def confirm_to_quit(self):
        if tk.messagebox.askokcancel('','Are you sure to exit?'):
            self.root.destroy()
            if self.client:
                try:
                    self.client.disconnect()
                except (ConnectionError,Exception) as e:
                    error_type, error_value, trace_back = sys.exc_info()
                    print(error_value)
                finally:
                    sys.exit(0)
                
    def _loginevent(self, event):
        if event.keysym == 'Return':
            self.check_login()    

    def _get_nickname(self):
        return self.nameE.get()

    def check_login(self):
        # controller for login functionality
        name = self._get_nickname()
        if not name:
            tk.messagebox.showwarning('Alert','Please type a nick name to continue!')
            return

        # Initiate the socket connection here for the very first time
        if self.client is None:
            self.client = c.Client()

        try:
            while True:
                result = self.client.set_name(name)
                if result is True or result is False:
                    break
            if result is True:
                self.root.destroy()
                chat_view(self.client)
            elif result is False:
                tk.messagebox.showerror('', 'This nick name is occupied, please try another one!')
                # pop up a alert message box that ask the user to reset a nick name

        except ConnectionRefusedError:
            error_type, error_value, trace_back = sys.exc_info()
            tk.messagebox.showerror(error_value, 'The server doesn\'t existed!\nPlease ask technicians for help')
            self.client = None
        except ConnectionResetError:
            error_type, error_value, trace_back = sys.exc_info()
            tk.messagebox.showerror(error_value, 'Lost connection to the server!\nPlease login again!')
            self.client = None

class chat_view(object): 
    def __init__(self, client):
        self.client = client
        self.dv = None # child dialog window

        self.root = tk.Tk()
        w_width = 640
        w_height = 400
        sc_width = self.root.winfo_screenwidth()
        sc_height = self.root.winfo_screenheight()

        x = sc_width//2 - w_width//2
        y = sc_height//2 - w_height//2

        # self.root.geometry('{}x{}+{}+{}'.format(w_width, w_height, x, y))
        self.root.title('Chat-Room')
        self.root.resizable(0,0)
        
        
        scrollbar = tk.Scrollbar(self.root, width=20)
        # Don't allow to edit the message text widge
        self.txtMsgList = tk.Text(self.root, width=70, height=15, yscrollcommand=scrollbar.set, state='disabled')
        scrollbar.config(command=self.txtMsgList.yview)
        scrollbar.grid(column=0)

        self.txtMsgType = tk.Text(self.root, width=70, height=8, wrap=tk.WORD)
        # self.txtMsgType.bind('<KeyPress-Return>', self._sendevent)

        out_bt = ttk.Button(self.root, text='Logout', command= self.log_out)
        sendmess_bt = ttk.Button(self.root, text='Send', command=self.send_message)
        p2p_bt = ttk.Button(self.root, text='Dialog', command=self.p2p_message)
        
        self.txtMsgList.grid(row=0, column=0, rowspan=5,sticky=tk.W, padx=2, pady=3)
        self.txtMsgType.grid(row=5, column=0, rowspan=3,sticky=tk.W, padx=2, pady=2)

        out_bt.grid(row=0,column=2, sticky=tk.N)
        sendmess_bt.grid(row=5, column=2, sticky=tk.S)
        p2p_bt.grid(row=6, column=2, sticky=tk.S)

        t_res_ser = Thread(target=self.receive_message, daemon=True) # New thread to receive msg from server
        t_res_ser.start()

        self.root.mainloop()

    def _sendevent(self, event):
        if event.keysym == 'Return':
            self.send_message()

    def log_out(self):
        if tk.messagebox.askokcancel('', 'Do you want to log out?'):
            self.root.destroy()
            try:
                self.client.disconnect()
            except ConnectionError:
                error_type, error_value, trace_back = sys.exc_info()
                print(error_value)
            finally:
                sys.exit(0)
                
            
    def _getMsgContent(self):
        return self.txtMsgType.get(1.0, tk.INSERT)
        

    def send_message(self):
        if not self._getMsgContent():
            tk.messagebox.showwarning('','Message box can\'t be empty!')
            return

        send_m_dict = {'To':'default', 
                       'From':self.client.data.nick_name.decode('utf-8'), 
                       'M':self.txtMsgType.get(1.0, tk.INSERT)}
        self.client.data.outb.append(json.dumps(send_m_dict))

        patnMsg = 'You: '+ time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime()) + '\n'
        self.txtMsgList.config(state='normal')
        self.txtMsgList.insert(tk.END, patnMsg)
        self.txtMsgList.insert(tk.END, self.txtMsgType.get('1.0',tk.END))
        self.txtMsgList.config(state='disabled')
        self.txtMsgType.delete('1.0', tk.END) 
        

    def receive_message(self):
        while True:
            time.sleep(0.1)

            try:
                if self.client.receive_send() == -1:
                    break
            except ConnectionResetError:
                error_type, error_value, trace_back = sys.exc_info()
                print(error_value)
                if tk.messagebox.showerror(error_value, 'Disconnected, please reconnect again!'):
                    self.root.destroy()
                    self.client.disconnect()
                     

            if self.client.data.intb:
                patnMsg = 'From server: '+ time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime()) + '\n'
                self.txtMsgList.config(state='normal')
                self.txtMsgList.insert(tk.END, patnMsg)

                while self.client.data.intb:
                    msg = self.client.data.intb.pop(0).decode('utf-8')
                    if 'System message:' in msg:
                        self.txtMsgList.insert(tk.END, msg + '\n')
                    else:
                        msg = json.loads(msg)
                        if isinstance(msg, dict): # incoming message from other clients
                            if msg['To'] == 'default':
                                msg = '{} said: {}'.format(msg['From'], msg['M'])
                            else:
                                msg = '{} whispered to you: {}'.format(msg['From'], msg['M'])
                            self.txtMsgList.insert(tk.END, msg + '\n')

                        elif isinstance(msg, list):
                            # Update the online-client list
                            self.txtMsgList.insert(tk.END, 'Online clients: ' + repr(msg) + '\n')
                            self.client.data.onlines = [one for one in msg if one != self.client.data.nick_name.decode('utf-8')]

                self.txtMsgList.config(state='disabled')

            
    def p2p_message(self):
        self.dv = dialog_view(self.root, self.client, self)

class dialog_view(tk.Toplevel):
    def __init__(self, parent, client, cls):
        self.parent = parent
        self.client = client
        self.cls = cls

        self.root = tk.Toplevel(self.parent)
        self.root.title('Whispering...')
        self.root.resizable(0,0)

        to_lb = tk.Label(self.root, text='To: ', fg='black')
        m_lb = tk.Label(self.root, text='Message: ', fg='black')
        to_lb.grid(row=0, column=0, sticky=tk.W)
        m_lb.grid(row=1, column=0, sticky=tk.W)

        self.to_E = tk.Entry(self.root)
        self.to_E.grid(row=0, column=1)

        self.m_E = tk.Text(self.root, width=25, height=5, pady=5)
        self.m_E.grid(row=1, column=1,rowspan=2)

        send_bt = ttk.Button(self.root, text='Send', command=self.send)
        send_bt.grid(column=0)

        cancel_bt = ttk.Button(self.root, text='Cancel', command=self.cancel)
        cancel_bt.grid(column=0)

        self.root.mainloop()
        
    def send(self):
        if not self.to_E.get():
            tk.messagebox.showwarning('Warning', 'Please choice an object!')
            return

        if not self.m_E.get(1.0, tk.INSERT):
            tk.messagebox.showwarning('Warning',
                'Please fill out the message part!')
            return 

        to = self.to_E.get()

        if to == self.client.data.nick_name.decode('utf-8'):
            tk.messagebox.showerror('Error', 'Can\'t whisper to yourself!')
            return
        elif not self.find_one(to):
            tk.messagebox.showerror('Error', 'There is no such person, choice another one!')
            return
            
        msg = self.m_E.get(1.0, tk.INSERT) # INSERT just including the last char, END including another '\n'
        self.m_E.delete(1.0, tk.INSERT)

        tellOne = {'To':to, 'From':self.client.data.nick_name.decode('utf-8'), 'M':msg}
        self.client.data.outb.append(json.dumps(tellOne))

        patnMsg = 'You: ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime()) + '\n'

        self.cls.txtMsgList.config(state='normal')
        self.cls.txtMsgList.insert(tk.END, patnMsg)
        self.cls.txtMsgList.insert(tk.END, 'Whispered to ' + to +': '+ msg + '\n')
        self.cls.txtMsgList.config(state='disabled')


    def cancel(self):
        self.root.destroy()

    def find_one(self, name):
        if name in self.cls.client.data.onlines:
            return True

        return False

if __name__=='__main__':
    try:
        login_view()
        
    except KeyboardInterrupt:
        print('keyboard interrupt')
    finally:
        sys.exit(0)
    


