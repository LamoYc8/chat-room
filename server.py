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
    # print('Welcome ',nick_name, ", Let's start chatting!") # TODO broadcasting later
    conn.setblocking(False)

    events = selectors.EVENT_READ|selectors.EVENT_WRITE
    sel.register(conn, events, data=types.SimpleNamespace(addr=addr, nick_name=b'', intb=b'', outb=b'', conn=False))


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
            sock.sendall(data.outb)
            data.outb = b''
            if data.nick_name:
                data.conn = True
            

def check_nickname(nick_name):
    nick_name.decode('utf-8')
    if nick_name in socket_dict.keys():
        return False
    else:
        return True


def service_conn(key, mask):
    sock = key.fileobj
    data = key.data

    # TODO
    pass


if __name__ == '__main__':
    sel = selectors.DefaultSelector()
    socket_dict = dict()
    main()