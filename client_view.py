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
            
    def _getMsgType(self):
        return self.txtMsgType.get(1.0, tk.END)
        

    def send_message(self):
        sendMsg = self._getMsgType()
        if sendMsg == '\n':
            return

        patnMsg = 'You: '+ time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime()) + '\n '
        self.txtMsgList.config(state='normal')
        self.txtMsgList.insert(tk.END, patnMsg)
        self.txtMsgList.insert(tk.END, self.txtMsgType.get('1.0',tk.END))
        self.txtMsgList.config(state='disabled')
        self.txtMsgType.delete('1.0', tk.END)   

        self.client.data.outb.append(sendMsg)
        t_send_server = Thread(target= self.client.send, daemon= True)
        t_send_server.start()

    def receive_message(self):
        while True:
            time.sleep(0.5)
            if self.client.receive() == -1:
                break

            if self.client.data.intb:
                msg = self.client.data.intb.pop(0)

                patnMsg = 'From server: '+ time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime()) + '\n '
                self.txtMsgList.config(state='normal')
                self.txtMsgList.insert(tk.END, patnMsg)
                self.txtMsgList.insert(tk.END, msg.decode('utf-8'))
                self.txtMsgList.config(state='disabled')
            
    def p2p_message(self):
        pass

class dialog_view(object):
    def __init__(self, client):
        self.root = tk.Tk()
        
        



if __name__=='__main__':
    try:
        login_view()
    # client = c.Client()
    # chat_view(client)
    except KeyboardInterrupt:
        print('keyboard interrupt')
    finally:
        sys.exit(0)
    


