import json
import selectors
import socket
import sys
import types


class Client (object):
    
    def __init__(self):

        self.sel = selectors.DefaultSelector()
        server_addr = ('127.0.0.1', 7324)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(server_addr)
        events = selectors.EVENT_READ|selectors.EVENT_WRITE

        self.data = types.SimpleNamespace(nick_name=b'', conn=False, intb=list(), outb=list(), onlines=None)
        self.sel.register(self.sock, events, data=self.data)

    def _pick_socket(self):
        # return (selkey, mask) or None
        while True:
            events = self.sel.select(timeout=1)
            if events:
                for selk, mask in events:
                    return selk, mask
            if not self.sel.get_map():
                break

        
    def set_name(self, nick_name):
        selk, mask = self._pick_socket()
        sock = selk.fileobj
        data = selk.data

        try:
            if mask & selectors.EVENT_READ:
                recv_data = sock.recv(1024)
                if recv_data == b"Accepted":
                    # print('Received from server: ', repr(recv_data), " your connection ", data.nick_name,"Let's chatting!")
                    data.conn = True
                    return True
                elif recv_data == b'Rejected':
                    # print('This nick name is occupied, please try another one!')
                    data.nick_name = b''
                    return False

            if mask & selectors.EVENT_WRITE:
                if not data.nick_name:
                    data.nick_name = bytes(nick_name,'utf-8')
                    sock.sendall(data.nick_name)
        except ConnectionError:
            raise     


    def disconnect(self):
        # broadcasting to others
        try:
            print('Ending connection to the server.')
            self.sel.unregister(self.sock)
            # self.sock.shutdown(2)
            self.sock.close()
        except ConnectionError:
            raise
        finally:
            self.sel.close()

# receive and send can be combined together
    def receive_send(self):
        if self._pick_socket() is None:
            return -1

        key, mask = self._pick_socket()

        sock = key.fileobj
        data = key.data

        try:
            if mask & selectors.EVENT_READ:
                recv_data = sock.recv(1024)
                if recv_data:
                    recv_data = recv_data.split(b'\n')
                    for item in recv_data:
                        if item:
                            data.intb.append(item)
                else:
                    raise ConnectionResetError

            if mask & selectors.EVENT_WRITE:
                if data.outb:
                    sent = bytes(data.outb.pop(0), 'utf-8')
                    sock.sendall(sent)

        except (ConnectionResetError, BrokenPipeError):
            raise
        

    def send(self):
        key, mask = self._pick_socket()

        sock = key.fileobj
        data = key.data

        try:
            if mask & selectors.EVENT_WRITE:
                if data.outb:
                    sent = bytes(data.outb.pop(0), 'utf-8')
                    sock.sendall(sent)
        except (ConnectionError, ConnectionResetError):
            raise
        


if __name__=='__main__':
    """
    host: 127.0.0.1
    port: 7324
    """
    host, port = '127.0.0.1', 7324

    sel = selectors.DefaultSelector()
    

    