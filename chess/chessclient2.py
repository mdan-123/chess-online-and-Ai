import socket
LISTEN_PORT = 8000

class ChessClient: 
    # only for player 1
    server_socket = None    # socket that server is running on
    # both player 1 and 2
    peer_socket = None      # socket to send/recieve data from peer (if not None, then we are connected)

    def connected_to_peer(self): # returns True if connected to peer
        return self.peer_socket is not None 

    @property # returns True if we are player 1
    def is_player_1(self):
        return self.server_socket is not None

    @property # returns True if we are player 2
    def is_player_2(self):
        return not self.is_player_1

    def create_game(self, host, port):
        """ Create a new game and start server thread, establish connection with peer """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
        self.server_socket.bind((host, port)) # bind to the port
        self.server_socket.listen(1) # wait for peer to connect
        print(f"Server started on {host}:{port}, awaiting connection...")
        self.peer_socket, (peer_host, peer_port) = self.server_socket.accept() # establish connection with peer
        print(peer_host, peer_port) 
        print(f"Connected to peer {peer_host}:{peer_port}")

    def join_game(self, host, port):
        """ Connect to peer to join an existing game
            Throws exception if peer is not listening
        """
        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
        self.peer_socket.connect((host, port)) # connect to peer
        print(f"Connected to server {host}:{port}")
 
    def get_data_from_peer(self, valid_responses): # returns data received from peer
        """ Wait for peer to send us a move
            Perform the move on the board
            Send peer success/failure message
            Returns bool indicating success/failure
        """

        while True: # loop until we receive a valid move
            try: # try to receive a valid move from the peer
                # receive data from the client (in this case, a move)
                print("Waiting for peer to send move...")
                data = None # data received from peer
                while not data: # loop until we receive data
                    data = self.peer_socket.recv(1024) # receive data from peer
                
                # convert the received data to a string
                data = data.decode() # decode the data
                print(f"Received data {data}") 
                
                if data not in valid_responses: # if the move is not valid, raise an exception
                    raise Exception("Invalid data")
                
                print("Sending success response to peer")
                response = "SUCCESS"
                self.peer_socket.sendall(response.encode()) # send success response to peer
                return data # return the move
            
            except Exception as e:
                message = f"Error occurred: {str(e)}"
                response = f"FAIL,{message}"
                self.peer_socket.sendall(response.encode()) # send failure response to peer
                return None

    def send_data(self, data): 
        """ Send move to peer, await response, return success/failure bool """

        self.peer_socket.sendall(data.encode()) # send data to peer
        print(f"Sending {data} to peer, awaiting success response...")
        
        # receive a response from the server
        data = None # data received from peer
        while not data: # loop until we receive data
            data = self.peer_socket.recv(1024) # receive data from peer
        response = data.decode() # decode the data

        # if the move was successful, print a success message and return True
        if response == "SUCCESS":  
            print("Recieved success message from peer")
            return True
        # if the move was not successful, print an error message and return False
        else:
            message = response.split(',')[1] # get the error message
            print("Recieved failure message from peer") 
            print(message)
            return False



