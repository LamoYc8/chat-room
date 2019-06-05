import socket
import sys
import selectors

def main():
    if len(sys.argv) != 3:
        print('usage:', sys.argv[0], '<host> <port>')
        sys.exit(1)
    """
    host: 127.0.0.1
    port: 7324
    """
    host, port = sys.argv[1:3]

    start_conn(host, int(port))

    # TODO 
    try:
        while True:
            events = sel.select(timeout=1)
            if events:
                for selkey, mask in events:
                    service_conn(selkey, mask)
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print('keyboard interrput, exiting!')
    finally:
        sel.close()

    

def start_conn(host, port):
    server_addr = (host, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ|selectors.EVENT_WRITE

    # TODO code checking
    sel.register(sock, events, service_conn) 

    kinput = input('prompt>') # allow clients to type input messages
    sock.sendall(kinput)
    data = sock.recv(1024)

    #print("Received " , repr(data)) # repr() a function used to transfer a object to a string

def service_conn(key, mask):
    sock = key.fileobj
    data = key.data

    # TODO mulitiple clients and messages queue issues here
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('Received from server: ', recv_data)
        if not recv_data:
            print('closing connection!')
            sel.unregister(sock)
            sel.close()

    if mask & selectors.EVENT_WRITE:
        pass
        



if __name__=='__main__':
    sel = selectors.DefaultSelector()
    main()

    