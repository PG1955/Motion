import random
import signal
import socket
from threading import Thread, Event
from datetime import datetime, time
import ast
import time
import pickle
import logging
try:
    from systemd.journal import JournalHandler
except ModuleNotFoundError:
    pass

"""
v1.1   26/03/2024 Add a event to closedown the socket correctly.
v1.2   27/03/2024 Add signal to kill off the process.
v1.3   27/03/2024 Add Loging. 
"""
__author__ = "Peter Goodgame"
# __name__ = "motionStatus"
__version__ = "v1.3b"


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


class MotionStatus:

    def __init__(self, logger=logging.getLogger("motion")):
        self.killer = GracefulKiller()
        self.log = self.get_logger("motion")
        self.event = Event()
        self.PORT = 23125
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.REQUEST = b'Send status please'
        self.MONITORING = 0
        self.RECORDING = 1
        self.status = self.MONITORING
        self.status_start_time = datetime.now()
        self.duration = 0
        self.data = {"status": 0, "duration": 0}

    def set_status(self, status):
        self.status_start_time = datetime.now()
        self.status = status

    def calculate_time(self):
        return float(round(((datetime.now() - self.status_start_time).total_seconds() / 60), 1))

    def handle_client(self, client_socket):
        """Process a request for data.
        Sends a data dictionary to the requester."""
        request = client_socket.recv(1024)
        if request != self.REQUEST:
            print(f'Invalid request: {request}')

        # print(f"Received: {request}")
        self.data["status"] = self.status
        self.data["duration"] = self.calculate_time()
        serialized_dict = pickle.dumps(self.data)
        client_socket.send(serialized_dict)
        client_socket.close()
        self.log.info('Handled client finished')

    def start_server_thread(self):
        """Use this to run a socket server in the background."""
        # Start the socket server in a separate thread
        self.log.info(f'Start socket server thread.')
        server_thread = Thread(target=self.socket_server, args=(self.event,))
        server_thread.start()

    def socket_server(self, event: Event) -> None:
        # Create a socket server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.ADDR)
        server.settimeout(1)
        server.listen(1)
        self.log.info(f'Socket server is listening on {self.ADDR}')
        while not self.killer.kill_now:
            if self.event.is_set():
                self.log.info(f'Event is set, terminate the loop.')
                break
            try:
                print('Waiting to Accept')
                client, addr = server.accept()
            except socket.timeout:
                time.sleep(0.5)
                continue
            self.log.info(f"Accepted connection from {addr[0]}:{addr[1]}")
            # Timeout after one second.
            client.settimeout(1)
            self.log.info('Socket Handle Client')
            client_handler = Thread(target=self.handle_client, args=(client,))
            client_handler.start()
            if event.is_set():
                print('The socket_server thread was stopped by the Event.')
                self.log.info('The socket_server thread was stopped by the Event.')
                break

    def stop_server(self):
        self.log.info(f'Stop server Event has been called')
        self.event.set()

    def get_status(self):
        response = b' '
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(self.ADDR)  # Connect to the server (adjust IP and port if needed)
            client.send(self.REQUEST)  # Send a request to the server
            # response = ast.literal_eval(client.recv(1024).decode(self.FORMAT))  # Receive the ACK from the server
            response = pickle.loads(client.recv(1024))
            print(f"Received from server: {response}")
            client.close()
        except ConnectionRefusedError:
            print("Server is not running or unreachable.")
        finally:
            return response

    @staticmethod
    def get_logger(self):
        logger = logging.getLogger('motion')
        try:
            logger.addHandler(JournalHandler())
            logger.setLevel(logging.INFO)
        except ModuleNotFoundError:
            pass
        except NameError:
            pass
        return logger


def generate_random_numbers():
    while True:
        random_number = random.randint(1, 100)
        print(f"Generated random number: {random_number}")
        time.sleep(1)


def main():
    data = {}
    random_number = 0
    ms = MotionStatus()
    try:

        ms.start_server_thread()
        counter = 0
        while True:
            counter += 1
            random_number = random.randint(1, 100)
            # There is a 8% chance of recording being carried out..
            data = ms.get_status()
            if random_number < 8 and data["status"] == ms.MONITORING:
                ms.set_status(ms.RECORDING)
            elif random_number >= 8 and data["status"] == ms.RECORDING:
                ms.set_status(ms.MONITORING)
            time.sleep(2)
            if counter > 10:
                print("Socket server trigger stop event..")
                ms.stop_server()

    except KeyboardInterrupt:
        ms.stop_server()
        print("\nClient terminated by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
