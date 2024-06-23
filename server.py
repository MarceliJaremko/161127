import socket
import threading
import pickle
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


class Server:
    MAX_CLIENTS = 5  # Maksymalna liczba obsługiwanych klientów jednocześnie

    def __init__(self, host='localhost', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.MAX_CLIENTS)
        self.objects = self.initialize_objects()
        self.active_clients = set()
        print(f"Server started on {self.host}:{self.port}")

    def initialize_objects(self):
        objects = {}
        for i in range(1, 5):
            objects[f'kot_{i}'] = Kot(name=f"Kot {i}")
            objects[f'pies_{i}'] = Pies(name=f"Pies {i}")
            objects[f'papuga_{i}'] = Papuga(name=f"Papuga {i}")
        return objects

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024)
            client_id = pickle.loads(data)

            if len(self.active_clients) >= self.MAX_CLIENTS:
                client_socket.send(pickle.dumps("REFUSED"))
                print(f"Client {client_id} connection refused")
            else:
                self.active_clients.add(client_id)
                client_socket.send(pickle.dumps("OK"))
                print(f"Client {client_id} connected")

                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    request = pickle.loads(data)
                    time.sleep(random.uniform(0.1, 1.0))  # Random delay
                    response = self.process_request(request, client_id)
                    client_socket.send(pickle.dumps(response))

                self.active_clients.remove(client_id)
                print(f"Client {client_id} disconnected")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def process_request(self, request, client_id):
        if request.startswith('get_'):
            class_name = request.split('_')[1].lower()
            collection = [obj for key, obj in self.objects.items() if key.startswith(class_name)]
            if collection:
                print(f"Sending {len(collection)} objects of type {class_name} to client {client_id}")
                return collection
            else:
                print(f"No objects of type {class_name} found for client {client_id}. Sending dummy object.")
                return [Kot(name="Dummy Kot")] if class_name == 'kot' else [
                    Pies(name="Dummy Pies")] if class_name == 'pies' else [Papuga(name="Dummy Papuga")]
        else:
            if request in self.objects:
                obj = self.objects[request]
                return f"Found {obj.__class__.__name__}: {vars(obj)}"
            else:
                return "Object not found"

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()


if __name__ == "__main__":
    server = Server()
    server.start()
