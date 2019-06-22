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

        except (ConnectionRefusedError, ConnectionError, ConnectionResetError) as e:
            error_type, error_value, trace_back = sys.exc_info()
            print(error_value)
            tk.messagebox.showerror('Error',error_value)

class chat_view(object): 
    def __init__(self, client):
        self.client = client

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
            except (ConnectionError, Exception) as e:
                error_type, error_value, trace_back = sys.exc_info()
                print(error_value)
            
    def _getMsgContent(self):
        return self.txtMsgType.get(1.0, tk.INSERT)
        

    def send_message(self):
        if not self._getMsgContent():
            return

        patnMsg = 'You: '+ time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime()) + '\n '
        self.txtMsgList.config(state='normal')
        self.txtMsgList.insert(tk.END, patnMsg)
        self.txtMsgList.insert(tk.END, self.txtMsgType.get('1.0',tk.END))
        self.txtMsgList.config(state='disabled')
        # outb is a str list containing all of the user msgs
        self.client.data.outb.append(self.txtMsgType.get(1.0, tk.END))
        self.txtMsgType.delete('1.0', tk.END)   

        t_send_server = Thread(target= self.client.send, daemon= True)
        t_send_server.start()

    def receive_message(self):
        while True:
            time.sleep(0.1)
            if self.client.receive() == -1:
                break

            while self.client.data.intb:
                patnMsg = 'From server: '+ time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime()) + '\n '
                self.txtMsgList.config(state='normal')
                self.txtMsgList.insert(tk.END, patnMsg)

                msg = self.client.data.intb.pop(0).decode('utf-8')
                # msg = json.loads(self.client.data.intb.pop(0).decode('utf-8'))
                if isinstance(msg, str):
                    self.txtMsgList.insert(tk.END, msg + '\n')
                elif isinstance(msg, list):
                    self.txtMsgList.insert(tk.END, repr(msg) + '\n')
                    self.client.data.onlines = [one for one in msg if one != self.client.data.nick_name.decode('utf-8')]

                self.txtMsgList.config(state='disabled')

            # if self.client.data.intb:
            #     patnMsg = 'From server: '+ time.strftime("%Y-%m-%d %H:%M:%S",
            #                     time.localtime()) + '\n '
            #     self.txtMsgList.config(state='normal')
            #     self.txtMsgList.insert(tk.END, patnMsg)
            #     # TODO json loads here for online clients list
                
            #     msg = self.client.data.intb.pop(0).decode('utf-8')
            #     self.txtMsgList.insert(tk.END, msg+'\n')
                # b'System message: o enters the room!\n["o"]'
                # for i in msg:
                #     self.txtMsgList.insert(tk.END, i +'\n')
                #     print(i)
                #     if isinstance(i, list):
                #         self.client.data.onlines = [one for one in i if one != self.client.data.nick_name.decode('utf-8')]
                # self.txtMsgList.config(state='disabled')
            
    def p2p_message(self):
        dv = dialog_view(self, self.client)
        

class dialog_view(object):
    def __init__(self, parent, client):
        self.parent = parent
        self.client = client

        self.root = tk.Tk()
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

        if not self.find_one(to):
            tk.messagebox.showerror('Error', 'There is no such person, choice another one!')

        msg = self.m_E.get(1.0, tk.INSERT) # INSERT just including the last char, END including another '\n'
        self.m_E.delete(1.0, tk.INSERT)

        tellOne = {'To':to, 'From':self.client.data.nick_name.decode('utf-8'), 'M':msg}
        sendMsg = json.dumps(tellOne)

        self.client.outb.append(sendMsg.encode('utf-8'))

        patnMsg = 'You: ' + time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime()) + '\n '

        self.parent.txtMsgList.config(state='normal')
        self.parent.txtMsgList.insert(tk.END, patnMsg)
        self.parent.txtMsgList.insert(tk.END, 'To ' + to +': '+ msg)
        self.parent.txtMsgList.config(state='disabled')

        self.m_E.delete(1.0, tk.END)
        # TODO whispering
        # t_send_server = Thread(target= self.client.send, daemon= True)
        # t_send_server.start()

        print()

    def cancel(self):
        self.root.destroy()

    def find_one(self, name):
        if name in self.parent.client.data.onlines:
            return True

        return False

if __name__=='__main__':
    try:
        login_view()
        # client = c.Client()
        # chat_view(client)
    except KeyboardInterrupt:
        print('keyboard interrupt')
    finally:
        sys.exit(0)
    # dialog_view(client)
    


