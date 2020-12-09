import socket
import select
import sys


BUFFER = 4096
# Get the IP address of the local host automatically
IP = socket.gethostbyname(socket.gethostname())
PORT = 1234

WELCOME_MESSAGE = "Hi, Plaese set your username:"
QUIT = '$q'

# Initialize the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((IP, PORT))


print(f'Connected to the server {IP}')

socket_list = [sys.stdin, client_socket]

while True:
    try:
        read_sockets, _, _ = select.select(socket_list, [], [])
        for s in read_sockets:
            if s is client_socket: # incoming message 
                message = s.recv(BUFFER).decode()
                # Handling message coming from the server
                if not message:
                    print("No response from the server!!! Closing application")
                    sys.exit(2)
                    
                else:
                    if message == QUIT:
                        print("\nExited gracefully\nBye, Have a nice day")
                        sys.exit(0)
                    else:
                        # sys.stdout.write(msg.decode())
                        print(f'{message}')
                        if message == WELCOME_MESSAGE:
                            message = 'username: ' + input()
                            # /////
                            if "admin" in message:
                                password = input("password: ")
                                if str(password) == "123":
                                    print("admin granted...\n")

                            # ////
                            
                            client_socket.sendall(message.encode())
                            
                        # admin logic
                        elif "pass" in message:
                            password = input("password: ")
                            message = 'username '+'pass ' + str(password)
                            client_socket.sendall(message.encode())

                        print('>>', end = ' ', flush = True)
            # Handling client sending message to the server
            else:
                message = input()
                client_socket.sendall(message.encode())
    # If ctr+c presses, do not close the app. That breaks connection with other client and breaks the app
    #instead gracegully close the connection
    except KeyboardInterrupt:
        print(" Type $q to exit")

