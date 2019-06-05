import socket
import selectors

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
            events = sel.select(timeout=None)
            for selkey, mask in events:
                if selkey.data is None:
                    accept_conn(selkey.fileobj)
                else:
                    service_conn(selkey, mask)
    except KeyboardInterrupt:
        print('Keyboard interrupt, exiting!')
    finally:
        sel.close()

def accept_conn(sock):
    pass


def service_conn(key, mask):
    pass


    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind((host, port))
    #     s.listen()
    #     conn,addr = s.accept()

    #     with conn:
    #         print('Connected by ', addr)
    #         while True:
    #             data = conn.recv(1024)
    #             if not data:
    #                 break
    #             conn.sendall(data)


if __name__ == '__main__':
    sel = selectors.DefaultSelector()
    main()