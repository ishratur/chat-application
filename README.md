# chat-application

#### To run the applicaton:
1. Go to the project directory
1. Run python3 server.py
1. Run python3 client.py

##### Some test case:

------------

##### Case 1: Chat between two clients in the same room
-  Run the server
- Open two terminals
- Run client 1: set an username and create a new room using (**$create room_name**)
- Run client 2: set an unsername and join the room created by client 1 using(**$join room_name**)
Can also view all the rooms by using(**$rooms**)

###### Expected result: Both the clients can succefully communicate with each other


------------
##### Case 2: Chat between three clients. Two in same room another client in different room
- Run the server
- Open three terminals and run the client
- Assign two clients in the same room and the thrid client in another room
- Send message from all the three terminals/clients

###### Expected result: Only the two clients in the same room can communicate with each other and the third client is in a different room so does not see the chat between the other two clients


------------
##### Case 3: Clients can switch between rooms created by himself or by other clients
- Run the server
- Run two clients
- Create new rooms for both the clients
- Switch rooms with each other using(**$switch room_name**)


------------

##### Case 4: Clients must close the connection gracefully (**Error Handling**)
- Run the server
- Run a client
- Type **Ctr+C** to aggressively disconnect

###### Expected result: Client connection will not get disconnected rather will be asked to use (**$q**) to diconnect gracefully.