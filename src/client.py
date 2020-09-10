import select
import socket
import threading
import time
from queue import Queue
import subprocess

CLIENT_NAME = 'Auto Covid Survey Client'
HEADER_SIZE = 10
NUMBER_OF_THREADS = 3
JOB_NUMBER = [1, 2, 3]
job_queue = Queue()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
msg_queue = Queue()


def time_stamp():
    return str(time.strftime("%I:%M:%S %p"))


def log(msg):
    return f'l/{CLIENT_NAME}: {time_stamp()}: {msg}'


def err(msg):
    return f'e/{CLIENT_NAME}: {time_stamp()}: {msg}'


def cmd(msg):
    pass


def send_msg(client_socket, msg):
    msg = f'{len(msg):<{HEADER_SIZE}}' + msg
    client_socket.send(bytes(msg, 'utf-8'))


def send():
    global s
    connected = False
    while True:
        try:
            if not connected:
                s.getsockname()

            # Send messages to server here
            if not msg_queue.empty():
                for _ in range(msg_queue.qsize()):
                    send_msg(s, msg_queue.get())

        except socket.error:
            connected = False
            while not connected:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((socket.gethostname(), 5001))
                    connected = True
                    send_msg(s, f'n/{CLIENT_NAME}')
                    msg_queue.queue.clear()
                    print('Re-connected')
                except socket.error:
                    print('Disconnected. Trying to re-connect.')
                    time.sleep(5)
        time.sleep(1)


def listen():
    while True:
        ready = select.select([s], [], [], 1)
        msg_len = -1
        new_msg = True
        full_msg = ''
        while ready[0]:
            try:
                msg = s.recv(16)
                if new_msg:
                    msg_len = int(msg[:HEADER_SIZE])
                    new_msg = False
                full_msg += msg.decode('utf-8')
                if len(full_msg) - HEADER_SIZE == msg_len:
                    if 'server wave' not in full_msg:
                        print(full_msg[HEADER_SIZE:])
                    break
            except socket.error:
                # should be handled by ping thread
                break


def run_script():
    while True:
        msg_queue.put(log('Starting script'))
        proc = subprocess.Popen(['python', 'email-bot.py'], stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            msg_queue.put(log(line.rstrip().decode()))
        msg_queue.put(err('Script Ended'))


def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# do next job that is in the queue
def work():
    while True:
        x = job_queue.get()
        # 1st thread: send messages and keep connection
        if x == 1:
            send()
        # 2nd thread: listen for commands
        if x == 2:
            listen()
        # 3rd thread: keep track of process
        if x == 3:
            run_script()
        job_queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        job_queue.put(x)
    job_queue.join()


def main():
    create_workers()
    create_jobs()


if __name__ == '__main__':
    main()
