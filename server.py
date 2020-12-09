import select, socket, sys


BUFFER_SIZE = 4096
# Get the IP address of the local host automatically
IP = socket.gethostbyname(socket.gethostname())
PORT = 1234

QUIT = '$q'
JOIN = "$join"
MANUAL = "$manual"
LIST = "$rooms"
CREATE = "$create"
SWITCH = "$switch"
USER_NAME = 'username:'
admin_password = 123
WELCOME_MESSAGE = "Hi, Plaese set your username:"
instructions = f'*See the instruction: {MANUAL}\n *View all the rooms: {LIST}\n *To join a room: {JOIN} room_name\n *To create a new room: {CREATE} room_name\n *To switch room: {SWITCH} room_name\n *To quit: {QUIT}\n '

instructions = instructions.encode()
room_list = {} 
playerName_RoomName = {} 

userName_Socket = {}


def handle_msg(client_sock, msg):
    
    command = msg.split()[0]

    if command == JOIN or command == SWITCH or command == CREATE:
        same_room = False

        if len(msg.split()) >= 2: # error check
            room_name = msg.split()[1:]
            room_name = ' '.join(room_name)
            # -- changing room
            if client_sock.name in playerName_RoomName:
                # print(f'room player: {self.room_player_map}')
                current_room = playerName_RoomName[client_sock.name]
                if current_room == room_name:
                    client_sock.socket.sendall(('You are already in room: ' + room_name).encode())
                    same_room = True
                # -- Before switich to a new room, remove the player from the old room.
                else: # switch
                    old_room = current_room
                    room_list[old_room].exit_client(client_sock)
            # -- Switich room
            if not same_room:
                # -- Create a new room if the room does not exist. Check if the same room exist or not
                
                if not room_name in room_list: # new room:
                    new_room = Room(room_name)
                    room_list[room_name] = new_room
                # -- now room exist i.e. either created or old room. 
                # -- add the new player, send welcome message, add in room-player map
                room_list[room_name].clients.append(client_sock)
                room_list[room_name].welcome_new(client_sock)
                playerName_RoomName[client_sock.name] = room_name
        else:
            client_sock.socket.sendall(instructions)



    else:

        # -- Player in a room, then broadcast the message to all players in the room
        if client_sock.name in playerName_RoomName:
            room_list[playerName_RoomName[client_sock.name]].broadcast(client_sock, msg.encode())
        # -- Player is not in a room yet  
        else:
            msg = 'Please join/create a room \n' \
                + 'Use $rooms to see available rooms! \n' \
                + 'Use $join room name to join a room! \n'
            client_sock.socket.sendall(msg.encode())

def exit_client(client_sock):
    if client_sock.name in playerName_RoomName:
        room_list[playerName_RoomName[client_sock.name]].exit_client(client_sock)
        del playerName_RoomName[client_sock.name]
    print("Username " + client_sock.name + " has left\n")




class Client:
    def __init__(self, socket):
        socket.setblocking(0)
        self.socket = socket
        self.name = "guest"
        
    def fileno(self):
        return self.socket.fileno()



class Room:
    def __init__(self, name):
        self.clients = [] 
        self.name = name

    def welcome_new(self, client_sock):
        msg = self.name + " welcomes: " + client_sock.name + '\n'
        for cleint in self.clients:
            cleint.socket.sendall(msg.encode())
    
    def broadcast(self, client_sock, msg):
        msg = client_sock.name.encode() + b":" + msg
        for cleint in self.clients:
            cleint.socket.sendall(msg)

    def exit_client(self, cleint):
        self.clients.remove(cleint)
        leave_msg = cleint.name + " has left the room\n"
        self.broadcast(cleint, leave_msg.encode())

# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.setblocking(0)
server_socket.bind((IP,PORT))
server_socket.listen()
print(f'Server Listening at {IP} on port {PORT}')

# List of all the connected sockets
connected_sockets = [server_socket]


while True:
    '''
    - UNIX system call to automatically get all the sockets from
      connected_sockets that are ready to be read.
    - Needed for hadling multiple clients
    '''
    read_sockets, _,exception_sockets = select.select(connected_sockets,[],[])
    for current_socket in read_sockets:
        # checking if its a new connection
        if current_socket == server_socket:
            new_client_socket, client_address = current_socket.accept()
            new_client = Client(new_client_socket)
            connected_sockets.append(new_client)
            new_client.socket.sendall(WELCOME_MESSAGE.encode())

        else:
            # existing socket receiving some data
            message = current_socket.socket.recv(BUFFER_SIZE)
            
            # For Admin
            
            if message:
                message = message.decode()
                print(current_socket.name + " sent: " + message)
                msg_command = message.split()[0]

                
                if msg_command == QUIT:
                    current_socket.socket.sendall(QUIT.encode())
                    exit_client(current_socket)

                elif "username" in msg_command:
                    
                    USER_NAME = message.split()[1]
                    current_socket.name = USER_NAME

                    print(f'New guest {current_socket.name} joined')
                    current_socket.socket.sendall(instructions)
                    userName_Socket[current_socket.name] = current_socket.socket
                    # print(userName_Socket)
                    
                


                elif msg_command == MANUAL:
                    current_socket.socket.sendall(instructions)



                elif msg_command == LIST:
                    
                    if len(room_list) > 0:
                        message = "Viewing all the rooms:\n"
                        for room in room_list:
                            num_players = str(len(room_list[room].clients))
                            message+= room + " has " + num_players + " client\n"
                        
                    else:
                        message = "No room to show"

                    current_socket.socket.sendall(message.encode())
    
                else:
                    handle_msg(current_socket,message)



                    
            else:
                current_socket.socket.close()
                connected_sockets.remove(current_socket)
    
    for err_socket in exception_sockets:
        err_socket.close()
        connected_sockets.remove(err_socket)







