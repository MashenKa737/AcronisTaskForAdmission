import socket
import sys
import threading
import time

shared_arr = []
shared_arr_lock = threading.Lock()


def repeat_print():
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        shared_arr_lock.acquire()
        print(shared_arr)
        shared_arr_lock.release()
        time.sleep(1)


def server_run(single_connection, print_thread, server_address):
    single_connection.bind(server_address)
    print("Echoloop started!")
    print_thread.start()
    while True:
        datagram = single_connection.recv(1024)
        if datagram != "":
            print("Detected other echoloop with argument: %s" % datagram.decode('utf-8'))
            shared_arr_lock.acquire()
            shared_arr.append(datagram.decode('utf-8'))
            shared_arr_lock.release()


def client_run(single_connection, server_address, program_arg):
    single_connection.connect(server_address)
    single_connection.send(program_arg.encode('utf-8'))


if __name__ == '__main__':
    program_name = sys.argv[0]
    program_arg = sys.argv[1]
    shared_arr.append(program_arg)
    single_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print_thread = threading.Thread(target=repeat_print)
    server_address = ('localhost', 12345)
    try:
        server_run(single_connection, print_thread, server_address)
    except socket.error as err:
        error_code = err.args[0]
        error_string = err.args[1]
        print("Process already running (%d:%s )." % (error_code, error_string))
        client_run(single_connection, server_address, program_arg)
        print("finished!")
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        print_thread.do_run = False
        single_connection.close()
