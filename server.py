import socket
import selectors
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
        sel.close()


def accept_conn(sock):
    conn, addr = sock.accept()
    # nick_name = conn.recv(1024) # Receive the unique nick_name from clients
    print('Accepted connection from ', addr)
    conn.setblocking(False)

    events = selectors.EVENT_READ|selectors.EVENT_WRITE
    sel.register(conn, events, data=types.SimpleNamespace(addr=addr, nick_name=b'', intb=list(), outb=b'', conn=False))
    # System messages use outb directly, others like broadcast and server_mes use intb list

def set_nickname(key, mask):
    sock = key.fileobj
    data = key.data

    # TODO 
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            if check_nickname(recv_data):
                data.nick_name = recv_data
                socket_dict[data.nick_name] = sock
                data.outb = b'Accepted'
            else:
                data.outb = b'Rejected'

        else:
            pass
            # print("Waiting for the user to set up a nick name.")
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('Sending checking result ', repr(data.outb),' to ', data.addr )
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            if data.nick_name:
                data.conn = True
                server_mes(key, '[System message:' + data.nick_name.decode('utf-8') +' entered!]')

            

def check_nickname(nick_name):
    nick_name.decode('utf-8')
    if nick_name in socket_dict.keys():
        return False
    else:
        return True

def service_conn(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('Receieved from ', data.addr, repr(recv_data))
            # TODO Distinct wishper and broadcast later
            broadcast(key,recv_data)
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.intb:
            data.outb = data.intb.pop(0)
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            

def server_mes(selkey, content):
    """
    Works for system messages so far, using outb directly
    """
    for k,v in socket_dict.items():
        if k != selkey.data.nick_name:
            try:
                sel.get_key(v).data.outb = bytes(content, 'utf-8')
            except:
                print('Error comes here!')

def broadcast(selkey, message):
    for k,v in socket_dict.items():
        if k != selkey.data.nick_name:
            sel.get_key(v).data.intb.append(message) # message is byte[]
    

if __name__ == '__main__':
    sel = selectors.DefaultSelector()
    socket_dict = dict() # Storing all alive connections
    """
    {nick_name:sock_object}
    """
    main()