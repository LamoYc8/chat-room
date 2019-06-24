import json
import socket
import selectors
import sys
import types

def main():
    # TODO When finish the project changing the host to ''
    host = '127.0.0.1' # standard loopback interface address
    port = 7324 # non-privileged ports are > 1023

    lssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lssock.bind((host, port))
    lssock.listen()
    lssock.setblocking(False)
    print('listerning on: ', (host, port))

    sel.register(lssock, selectors.EVENT_READ,data=None) 

    try:
        while True:
            # wait until some registered file objects become ready or the timeout expires
            events = sel.select(timeout=None) 
            for selkey, mask in events:
                if selkey.data is None:
                    accept_conn(selkey.fileobj)
                else:
                    if not selkey.data.nick_name or selkey.data.conn is False:
                        set_nickname(selkey, mask)
                    else:
                        service_conn(selkey, mask)
    except KeyboardInterrupt:
        print('Keyboard interrupt, exiting!')
    finally:
        for sock in socket_dict.values():
            sel.unregister(sock)
            sock.close()

        sel.close()
        print('Server is closing......')
        sys.exit(0)


def accept_conn(sock):
    conn, addr = sock.accept()
    # nick_name = conn.recv(1024) # Receive the unique nick_name from clients
    print('Accepted connection from ', addr)
    conn.setblocking(False)

    events = selectors.EVENT_READ|selectors.EVENT_WRITE
    sel.register(conn, events, data=types.SimpleNamespace(addr=addr, nick_name=b'', intb=list(), outb=b'', conn=False))
    # System messages use outb directly, others like tellOthers use intb list

def set_nickname(key, mask):
    sock = key.fileobj
    data = key.data

    try:
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                if _check_nickname(recv_data): 
                    data.nick_name = recv_data
                    socket_dict[data.nick_name] = sock # Appending to the dict of all the sockets
                    data.outb = b'Accepted'
                else:
                    data.outb = b'Rejected'
            else:
                print('Lost connection to: ', data.addr, ' and this user haven\'t logged in before.')
                sel.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('Sending checking result ', repr(data.outb),' to ', data.addr )
                sock.sendall(data.outb)
                data.outb = b''
                if data.nick_name:
                    data.conn = True
                    sys_msg('System message: ' + data.nick_name.decode('utf-8') +' enters the room!\n')
                    tellOthers(key, getClients(), include=True)
                    
    except ConnectionError:
        print('Lost connection: ', data.addr)
        sel.unregister(sock)
        sock.close()
    

def _check_nickname(nick_name):
    if nick_name in socket_dict.keys():
        return False
    else:
        return True

def service_conn(key, mask):
    try:
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                print('Received from ', data.addr, repr(recv_data))
                recv_data = json.loads(recv_data.decode('utf-8'))
                if recv_data['To'] == 'default':
                    tellOthers(key, json.dumps(recv_data).encode('utf-8'))
                else:
                    whisper(recv_data)
            else:
                print('Closing connection to ', data.nick_name.decode('utf-8'), data.addr)
                sel.unregister(sock)
                sock.close()
                socket_dict.pop(data.nick_name)
                sys_msg('System message: ' + data.nick_name.decode('utf-8') + ' logged out!\n' )
                tellOthers(key, getClients())

        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.intb:
                data.outb = data.intb.pop(0)
            if data.outb:
                sock.sendall(data.outb)
                data.outb = b''

    except ConnectionError as e:
        error_type, error_value, trace_back = sys.exc_info()
        print(data.nick_name.decode('utf-8'), ' ', error_value)
        sel.unregister(sock)
        sock.close()
        socket_dict.pop(data.nick_name)
        sys_msg('System message: ' + data.nick_name.decode('utf-8') + ' logged out!\n' )
        tellOthers(key, getClients())


def sys_msg(message):
    """
    Works for system messages so far, using outb directly
    """

    for k, v in socket_dict.items():
        try:
            sel.get_key(v).data.outb = message.encode('utf-8')
        except Exception as e:
            print('sys_msg got errors!')
            error_type, error_value, trace_back = sys.exc_info()
            print(error_value)

def tellOthers(selkey, message, include=False):
    """
    Using intb list to queue all the messages
    b'' or a list of online clients
    """
    if isinstance(message, list):
        message = json.dumps(message).encode('utf-8')
    
    if include:
        for k,v in socket_dict.items():
            sel.get_key(v).data.intb.append(message) 
    else:
        for k,v in socket_dict.items():
            if k != selkey.data.nick_name:
                sel.get_key(v).data.intb.append(message) 

def whisper(msg:dict):
    to = socket_dict.get(msg['To'].encode('utf-8'))
    sel.get_key(to).data.intb.append(json.dumps(msg).encode('utf-8'))

def getClients():
    onlines = []
    for key in socket_dict.keys():
        onlines.append(key.decode('utf-8'))

    return onlines

if __name__ == '__main__':
    sel = selectors.DefaultSelector()
    socket_dict = dict() # Storing all alive connections
    """
    {b'nick_name':sock_object}
    """
    main()