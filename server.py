import select, socket, sys


BUFFER_SIZE = 4096
# Get the IP address of the local host automatically
IP = socket.gethostbyname(socket.gethostname())
PORT = 1234

QUIT = '$quit'
JOIN = "$join"
MANUAL = "$manual"
LIST = "$list"
USER_NAME = 'username:'
WELCOME_MESSAGE = "Hi, Plaese set your username:"
instructions = f'*See the instruction: {MANUAL}\n *View all the rooms: {LIST}\n *To join/create a room: {JOIN} room_name\n *To switch room: {JOIN} room_name\n *To quit: {QUIT}\n '

instructions = instructions.encode()
room_list = {} 
playerName_RoomName = {} 


def handle_msg(player, msg):
    
    command = msg.split()[0]

    if JOIN == command:
        same_room = False

        if len(msg.split()) >= 2: # error check
            room_name = msg.split()[1:]
            room_name = ' '.join(room_name)
            # -- changing room
            if player.name in playerName_RoomName:
                # print(f'room player: {self.room_player_map}')
                current_room = playerName_RoomName[player.name]
                if current_room == room_name:
                    player.socket.sendall(b'You are already in room: ' + room_name.encode())
                    same_room = True
                # -- Before switich to a new room, remove the player from the old room.
                else: # switch
                    old_room = current_room
                    room_list[old_room].remove_player(player)
            # -- Switich room
            if not same_room:
                # -- Create a new room if the room does not exist. Check if the same room exist or not
                
                if not room_name in room_list: # new room:
                    new_room = Room(room_name)
                    room_list[room_name] = new_room
                # -- now room exist i.e. either created or old room. 
                # -- add the new player, send welcome message, add in room-player map
                room_list[room_name].clients.append(player)
                room_list[room_name].welcome_new(player)
                playerName_RoomName[player.name] = room_name
        else:
            player.socket.sendall(instructions)



    else:

        # -- Player in a room, then broadcast the message to all players in the room
        if player.name in playerName_RoomName:
            room_list[playerName_RoomName[player.name]].broadcast(player, msg.encode())
        # -- Player is not in a room yet  
        else:
            msg = 'Please join/create a room \n' \
                + 'Use $list to see available rooms! \n' \
                + 'Use $join room name to join/create a room! \n'
            player.socket.sendall(msg.encode())

def remove_player(player):
    if player.name in playerName_RoomName:
        room_list[playerName_RoomName[player.name]].remove_player(player)
        del playerName_RoomName[player.name]
    print("Username " + player.name + " has left\n")



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

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + '\n'
        for player in self.clients:
            player.socket.sendall(msg.encode())
    
    def broadcast(self, from_player, msg):
        msg = from_player.name.encode() + b":" + msg
        for player in self.clients:
            player.socket.sendall(msg)

    def remove_player(self, player):
        self.clients.remove(player)
        leave_msg = player.name.encode() + b"has left the room\n"
        self.broadcast(player, leave_msg)

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
                    remove_player(current_socket)

                elif "username" in msg_command:
                    
                    USER_NAME = message.split()[1]
                    current_socket.name = USER_NAME
                    print(f'New guest {current_socket.name} joined')
                    current_socket.socket.sendall(instructions)

                elif msg_command == MANUAL:
                    current_socket.socket.sendall(instructions)

                elif msg_command == LIST:
                    
                    if len(room_list) > 0:
                        message = "Viewing all the rooms:\n"
                        for room in room_list:
                            num_players = str(len(room_list[room].clients))
                            message+= room + " has " + num_players + " player\n"
                        
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







