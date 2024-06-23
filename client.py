import socket
import pickle
import threading
import time
import random

class Kot:
    def __init__(self, name):
        self.name = name

class Pies:
    def __init__(self, name):
        self.name = name

class Papuga:
    def __init__(self, name):
        self.name = name

class Client(threading.Thread):
    def __init__(self, client_id, request, host='localhost', port=65432):
        super().__init__()
        self.client_id = client_id
        self.request = request
        self.host = host
        self.port = port

    def run(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        status = self.connect()
        if status == "OK":
            time.sleep(random.uniform(0.1, 1.0))  # Random delay
            self.send_request(self.request)
        else:
            print(f"Client {self.client_id} exiting due to REFUSED connection status")
        self.close_connection()

    def connect(self):
        try:
            self.client_socket.send(pickle.dumps(self.client_id))
            response = self.client_socket.recv(1024)
            status = pickle.loads(response)
            print(f"Connection status: {status}")
            return status
        except Exception as e:
            print(f"Connection error: {e}")
            return "ERROR"

    def send_request(self, request):
        try:
            self.client_socket.send(pickle.dumps(request))
            response = self.client_socket.recv(1024)
            received_data = pickle.loads(response)
            if isinstance(received_data, list):
                print(f"Client {self.client_id} received collection:")
                for obj in received_data:
                    try:
                        print(vars(obj))
                    except TypeError:
                        print(f"Client {self.client_id} received an object of unexpected type")
            else:
                print(f"Client {self.client_id} received: {received_data}")
        except Exception as e:
            print(f"Request error: {e}")

    def close_connection(self):
        self.client_socket.close()

if __name__ == "__main__":
    requests = ['get_kot', 'get_pies', 'get_papuga']
    clients = [Client(client_id=i, request=random.choice(requests)) for i in range(1, 10)]  # Tworzenie większej liczby klientów

    for client in clients:
        client.start()

    for client in clients:
        client.join()
