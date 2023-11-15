import copy


class Move():
    # maps key to values
    ranks_to_row = {'1': 7, '2': 6, '3': 5, '4': 4, #changes the format to that of a normal chess game. E.g. (7,1) is (b,1)
                    '5': 3, '6': 2, '7': 1, '8': 0}
    row_to_ranks = {v: k for k, v in ranks_to_row.items()}
    files_to_coloumn = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                        'e': 4, 'f': 5, 'g': 6, 'h': 7}
    coloumn_to_file = {v: k for k, v in files_to_coloumn.items()}

    def __init__(self, start_square, end_square, panel, is_enpassant=False, is_c_move=False):  #move class, this class handles the moves.
        self.beg_r = start_square[0] #start square is a tuple. e.g. (7,1). The first number would be the row
        self.beg_c = start_square[1] #2nd number would be the coloumn
        self.finish_r = end_square[0] #end square is a tuple. e.g. (7,1). The first number would be the row
        self.finish_c = end_square[1] #2nd number would be the coloumn
        self.piece_advanced = panel[self.beg_r][self.beg_c] #piece advanced is the piece that is being moved
        self.piece_taken = panel[self.finish_r][self.finish_c] #piece taken is the piece that is being taken
        self.is_p_p = False #is pawn promotion
        if (self.piece_advanced == 'wp' and self.finish_r == 0) or (self.piece_advanced == 'bp' and self.finish_r == 7):
            #if the piece is a pawn and it is on the 8th rank, then it is a pawn promotion
            self.is_p_p = True
        self.is_ep = is_enpassant #is enpassant
        if self.is_ep:
            #if it is enpassant, then the piece taken is the opposite colour of the piece that is being moved
            self.piece_taken = 'wp' if self.piece_advanced == 'bp' else 'bp'
        self.moveID = self.beg_r * 1000 + self.beg_c * 100 + self.finish_r * 10 + self.finish_c  #moveID is the ID of the move
        self.is_c_move = is_c_move #is castle move

    # overriding the move class
    def __eq__(self, other): #if the move is equal to another move
        if isinstance(other, Move): #if the other move is a move if self.moveID == 
            return self.moveID == other.moveID #return the moveID
        return False

    def get_chess_notation(self): 
        return f"{self.get_rank_file(self.beg_r, self.beg_c)} -> {self.get_rank_file(self.finish_r, self.finish_c)}" 

    def get_rank_file(self, row, coloumn):
        return self.coloumn_to_file[coloumn] + self.row_to_ranks[row] 

    def __str__(self):
        piece_name = {'p': 'pawn', 'h': 'knight', 'B': 'bishop', 'k': 'king', 'q': 'queen', 'r': 'rook'}
        return f"{piece_name[self.piece_advanced[1]]} {self.get_chess_notation()}"

    def serialize(self):
        # serialize move for sending via client
        # example: [44][45](c0)(p0) moves piece from (row 4, col 4) to (row 4, col 5), is not castle, not enpassant
        # example: [ab][cd](c1)(p0) moves piece from (row a, col b) to (row c, col d), is a castle move
        return f"[{self.beg_r}{self.beg_c}][{self.finish_r}{self.finish_c}](c{int(self.is_c_move)})(p{int(self.is_ep)})"

    @classmethod #class method
    def fromSerializedRepresentation(self, game, move_string): #from serialized representation
        """ convert serialized representation to a move object """ 
        start_square = (int(move_string[1]), int(move_string[2]))   #here we are converting the move string to a move object
        end_square = (int(move_string[5]), int(move_string[6])) #this is done by converting the string to a tuple
        is_c_move = move_string[10] == '1'  #is castle move
        is_enpassant = move_string[14] == '1' #is enpassant
        return Move(start_square, end_square, game.panel, is_enpassant, is_c_move) #return the move


class Game():
    def __init__(self):
        
        # panel is an 8x8 2d list, each element of the list has two characters
        # first character represents colour of the piece
        # second character represents the type of the piece
        # '__' is an empty space
        self.panel = [
            ['br', 'bh', 'bB', 'bq', 'bk', 'bB', 'bh', 'br',],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp',],
            ['__', '__', '__', '__', '__', '__', '__', '__', ],
            ['__', '__', '__', '__', '__', '__', '__', '__'],
            ['__', '__', '__', '__', '__', '__', '__', '__', ],
            ['__', '__', '__', '__', '__', '__', '__', '__',],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp',],
            ['wr', 'wh', 'wB', 'wq', 'wk', 'wB', 'wh', 'wr',]
        ]

        
        #PSQT tables for each piece
        self.pawn_table =[ 
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
            [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0], 
            [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0], 
            [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5,], 
            [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
            [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
            [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        self.knight_table =[
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
            [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
            [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
            [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
            [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
            [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
            [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]]

        self.bishop_table =[
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
            [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
            [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
            [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]]

        self.rook_table =[
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]]

        self.queen_table =[
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
            [-1.0, 0.0, 1.0, 1.0, 1.0, 0.5, 0.5, -1.0],
            [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
            [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]]

        self.king_table =[
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
            [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
            [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
            [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]]


        self.player_1 = True # white
        self.record_for_move = [] # record for move log 
        self.location_of_wk = (7, 4) # location of white king
        self.location_of_bk = (0, 4) # location of black king
        self.check_mate = False # check mate
        self.stalemate = False  # stalemate
        self.ep_possible = ()  # x y of where en passant is possible
        self.live_castle_possible = castle_possible(True, True, True, True)     # live castle possible
        self.record_for_castle_move = [castle_possible(self.live_castle_possible.wks, self.live_castle_possible.bks,self.live_castle_possible.wqs, self.live_castle_possible.bqs)] # record for castle move log
        self.ready = False 
        self.end = False

    @property # getter
    #this function returns the current player
    def player_2(self): # black
        return not self.player_1 # opposite of player_1

    def connected(self):
        self.ready =  True
        return self.ready
    
    def win(self):
        if self.check_mate == True:
            return self.win
    
    def tie(self):
        if self.stalemate == True:
            return self.tie

    # takes a move as a parameter and executes it ()
    def make_move(self, move: Move): # move is a Move object
        self.panel[move.beg_r][move.beg_c] = '__' # remove the piece from the beginning
        self.panel[move.finish_r][move.finish_c] = move.piece_advanced # move the piece to the end
        self.record_for_move.append(move)  # log the move
        self.player_1 = not self.player_1  # swap the player

        # update king location
        match move.piece_advanced: #compare the piece advanced with the two kings if true update the location of the king
            case 'wk':
                self.location_of_wk = (move.finish_r, move.finish_c) #update the location of the white king
            case 'bk':
                self.location_of_bk = (move.finish_r, move.finish_c) #update the location of the black king

        ##if move.is_p_p: # if the move is a pawn promotion
        #    match move.piece_advanced: #see if the piece advanced is a white or black pawn
        #        case 'wp':
        #            self.panel[move.finish_r][move.finish_c] = 'wq' #if it is a white pawn then change it to a white queen
        #        case 'bp':
        #            self.panel[move.finish_r][move.finish_c] == 'bq' #if it is a black pawn then change it to a black queen


        if move.is_p_p:
            self.panel[move.finish_r][move.finish_c] = move.piece_advanced[0] + "q"



        # en passant move
        if move.is_ep: #if the move is an en passant move
            self.panel[move.beg_r][move.finish_c] = '__' #remove the pawn that was captured

        # update enpassant possible
        if move.piece_advanced[1] == 'p' and abs(move.beg_r - move.finish_r) == 2:  # only on 2 sqaure pawn advances
            self.ep_possible = ((move.beg_r + move.finish_r) // 2 , move.beg_c) #after the (move.beg_r + move.finish_ r) it needs //2
        else:
            self.ep_possible = ()   
            

        # castle move
        if move.is_c_move: #if the move is a castle move
            if move.finish_c - move.beg_c == 2:# kingside castle move
                if move.finish_c - 1 >=0 and move.finish_c+1 <8: #make sure the move is within the board
                    self.panel[move.finish_r][move.finish_c - 1] = self.panel[move.finish_r][move.finish_c + 1]  # moves the rook
                    self.panel[move.finish_r][move.finish_c + 1] = '__' #removes the rook from the original position
            else:  # queen side castle move
                if move.finish_c - 2 >=0 and move.finish_c+1 <8: #make sure the move is within the board
                    self.panel[move.finish_r][move.finish_c + 1] = self.panel[move.finish_r][move.finish_c - 2]  # moves the rook
                    self.panel[move.finish_r][move.finish_c - 2] = '__' #removes the rook from the original position

                # update castling rights - it changes when the king or rook moves
        self.amend_castle_possible(move)
        self.record_for_castle_move.append(castle_possible(self.live_castle_possible.wks, self.live_castle_possible.bks,
                                                    self.live_castle_possible.wqs, self.live_castle_possible.bqs))

    # undo function
    def reverse_move(self):
        if len(self.record_for_move) != 0:  # make sure it is not a 0
            move = self.record_for_move.pop() # removes the last move from the list
            self.panel[move.beg_r][move.beg_c] = move.piece_advanced # moves the piece back to the original position
            self.panel[move.finish_r][move.finish_c] = move.piece_taken # moves the piece back to the original position
            self.player_1 = not self.player_1 # swap the player
            # updates kings position
            match move.piece_advanced:
                case 'wk': #if the piece advanced is a white king
                    self.location_of_wk = (move.beg_r, move.beg_c) #update the location of the white king to where it was before the move
                case 'bk': #if the piece advanced is a black king
                    self.location_of_bk = (move.beg_r, move.beg_c) #update the location of the black king to where it was before the move
            # undo en passant
            if move.is_ep:  # if the move is an en passant move
                self.panel[move.finish_r][move.finish_c] = '__'     # at the end square there was no piece hence why it is __
                self.panel[move.beg_r][move.finish_c] = move.piece_taken # just below the end square there was a piece
                self.ep_possible = (move.finish_r, move.finish_c) #reset the value of the en passant possible
            # undo 2 square pawn advance
            if move.piece_advanced[1] == 'p' and abs(move.beg_r - move.finish_r) == 2: # only on 2 sqaure pawn advances
                self.ep_possible = ()

            # undo castling rights
            self.record_for_castle_move.pop()  # remove the last castle rights
            castle_possible = copy.deepcopy(self.record_for_castle_move[-1])   # get the last castle rights
            self.live_castle_possible = castle_possible # update the live castle rights


            # undo castle move
            if move.is_c_move:
                if move.finish_c - move.beg_c == 2: # kingside castle move
                    if move.finish_c + 1 < 8 and move.finish_c -1 >=0: # make sure the move is within the board
                        self.panel[move.finish_r][move.finish_c + 1] = self.panel[move.finish_r][move.finish_c - 1] # moves the rook back to where it was before the move
                        self.panel[move.finish_r][move.finish_c - 1] = '__'     # removes the rook from the position it was moved to 
                else:
                    if move.finish_c + 1 < 8 and move.finish_c -2 >=0:  # queen side
                        self.panel[move.finish_r][move.finish_c - 2] = self.panel[move.finish_r][move.finish_c + 1] # moves the rook back to where it was before the move
                        self.panel[move.finish_r][move.finish_c + 1] = '__'    # removes the rook from the position it was moved to

    # update the castle rights when a piece moves
    def amend_castle_possible(self, move):
        match move.piece_advanced:
            case 'wk':  # if the piece advanced is a white king
                self.live_castle_possible.wks = False # white king side castle is no longer possible
                self.live_castle_possible.wqs = False # white queen side castle is no longer possible
            case 'bk':  # if the piece advanced is a black king
                self.live_castle_possible.bks = False  # black king side castle is no longer possible
                self.live_castle_possible.bqs = False  # black queen side castle is no longer possible
            case 'wr': # if the piece advanced is a white rook
                if move.beg_r == 7: # if the rook is on the 7th rank
                    match move.beg_c: # if the rook is on the 0th or 7th file
                        case 0:    # left rook
                            self.live_castle_possible.wqs = False # white queen side castle is no longer possible
                        case 7:   # right rook
                            self.live_castle_possible.wks = False # white king side castle is no longer possible
            case 'br': # if the piece advanced is a black rook
                if move.beg_r == 0: # if the rook is on the 0th rank
                    match move.beg_c: # if the rook is on the 0th or 7th file
                        case 0:     # left rook
                            self.live_castle_possible.bqs = False # black queen side castle is no longer possible
                        case 7:   # right rook
                            self.live_castle_possible.bks = False # black king side castle is no longer possible

        #if rook is captured
        match move.piece_taken: # if the piece taken is a rook
            case 'wr': # if the piece taken is a white rook
                if move.finish_r ==7:   # if the rook is on the 7th rank
                    match move.finish_c: # if the rook is on the 0th or 7th file
                        case 0:   # left rook
                            self.live_castle_possible.wqs = False # white queen side castle is no longer possible
                        case 7:  # right rook
                            self.live_castle_possible.wks = False # white king side castle is no longer possible
            case 'br': # if the piece taken is a black rook
                if move.finish_r == 0: # if the rook is on the 0th rank
                    match move.finish_c: # if the rook is on the 0th or 7th file
                        case 0: # left rook
                            self.live_castle_possible.bqs = False # black queen side castle is no longer possible
                        case 7: # right rook
                            self.live_castle_possible.bks = False # black king side castle is no longer possible
                    




    def get_correct_moves(self): # returns a list of all the correct moves
        temp_ep_possible = self.ep_possible  # store the value of the en passant possible
        temp_castle_possible = castle_possible(self.live_castle_possible.wks, self.live_castle_possible.bks,self.live_castle_possible.wqs, self.live_castle_possible.bqs) # store the value of the castle possible
        # generate all possible moves
        moves = self.acquire_every_move() # get all the possible moves
        if self.player_1: # if it is white's turn
            self.acquire_c_moves(self.location_of_wk[0], self.location_of_wk[1], moves) # get all the possible castling moves
        else:
            self.acquire_c_moves(self.location_of_bk[0], self.location_of_bk[1], moves)

        for i in range(len(moves) - 1, -1, -1): # for every move
            self.make_move(moves[i])    
            # generate all opponent's move 
            self.player_1 = not self.player_1  # switch the player as it gets switched when the move is made
            if self.in_check(): # if the king is in check
                moves.remove(moves[i])  # if they attack the king then it is not a valid move
            self.player_1 = not self.player_1 # switch the player back
            self.reverse_move() # reverse the move
            self.checker_maker(moves) # check to see if an ending scenario has been reached


        self.ep_possible = temp_ep_possible # need to keep this constant
        self.live_castle_possible = temp_castle_possible  # need to keep this constant
        return moves # return the list of all the correct moves



    '''this function checks to see if the king is in check and returns true if it is and false if it is not after we use this function to check if the king is in check we switch the player back
    see if we have reached an ending scenario and then return the list of all the correct moves'''

    # determine if the current player is in check
    def in_check(self): # returns true if the current player is in check
        if self.player_1: # if it is white's turn
            self.player_1 = not self.player_1 # switch the player
            opp_moves = self.acquire_every_move() # get all the opponents possible moves
            for move in opp_moves: # for each move
                if move.finish_r == self.location_of_wk[0] and move.finish_c == self.location_of_wk[1]: # if the move ends on the king
                    self.player_1 = not self.player_1 # switch the player back
                    return True # return true
            self.player_1 = not self.player_1 # switch the player back
            return False # return false if the king is not in check
        else: # if it is black's turn
            self.player_1 = not self.player_1  # switch the player
            opp_moves = self.acquire_every_move() # get all the opponents possible moves
            for move in opp_moves: # for each move
                if move.finish_r == self.location_of_bk[0] and move.finish_c == self.location_of_bk[1]: # if the move ends on the king
                    self.player_1 = not self.player_1 # switch the player back
                    return True # return true
            self.player_1 = not self.player_1 # switch the player back
            return False # return false if the king is not in check
     




    def checker_maker(self, moves): # checks to see if an ending scenario has been reached
        if len(moves)==0: # if there are no moves
  
            if self.in_check(): # if the king is in check

                if self.player_1: # if it is white's turn
                    self.win = True    #set the win to true
                    self.check_mate = True # set the check mate to true
                    self.end =  True # set the end to true , we need to keep in mind that if it is whites turn and there are no moves and the king is in check tuhen it is a check mate for black 
                    return self.win, self.check_mate, self.end # return the values
                else: # if it is black's turn
                    self.check_mate = True # set the check mate to true 
                    self.win = True     # set the win to true
                    self.end = True 
                    return self.win, self.check_mate, self.end
            else: #stalemate as no piece is in check
                self.stalemate = True #sets stalemate to true
                self.tie = True
                self.end = True
                return self.stalemate, self.tie, self.end 
        return self.stalemate, self.tie, self.end #return the values



    def acquire_every_move(self): #acquire all the psuedo-legal moves without taking into account if the kings are in check or not
        moves = [] #moves = to an empty list
        for row in range(8):  #8x8 board
            for coloumn in range(8):  
                turn = self.panel[row][coloumn][0] #get the turn
                if (turn == 'w' and self.player_1) or (turn == 'b' and not self.player_1): #if it is the current players turn
                    piece = self.panel[row][coloumn][1] #get the piece
                    if piece[0] == 'p': #if the piece is a pawn
                        self.acquire_p_moves(row, coloumn, moves) #get all the possible pawn moves
                    elif piece[0] == 'r': #if the piece is a rook
                        self.get_rook_moves(row,coloumn,moves) #get all the possible rook moves
                    elif piece[0] == 'B': #if the piece is a bishop
                        self.get_bishop_moves(row,coloumn,moves) #get all the possible bishop moves
                    elif piece[0] == 'k': #if the piece is a king
                        self.get_king_moves(row,coloumn,moves) #get all the possible king moves
                    elif piece[0] == 'h': #if the piece is a knight
                        self.get_knight_moves(row,coloumn,moves) #get all the possible knight moves
                    elif piece[0] == 'q':   #if the piece is a queen
                        self.get_queen_moves(row,coloumn,moves) #get all the possible queen moves
                    
        return moves #return the list of all the possible moves

    # get pawn moves
    def acquire_p_moves(self, row, coloumn, moves):
        if self.player_1:  #check if it is white's turn
            if row > 0 and self.panel[row - 1][coloumn] == '__':  # 1 square move and check if it is a valid square and it is on the board
                moves.append(Move((row, coloumn), (row - 1, coloumn), self.panel)) #append the move to the list of moves
                if row == 6 and self.panel[row - 2][coloumn] == '__':  # 2 square move if it is a valid square and it is on the board
                    moves.append(Move((row, coloumn), (row - 2, coloumn), self.panel)) #append the move to the list of moves
            if coloumn - 1 >= 0:  # captures to the left 
                if row > 0 and self.panel[row - 1][coloumn - 1][0] == 'b': # enemy piece to capture and check if it is a valid square and it is the board
                    moves.append(Move((row, coloumn), (row - 1, coloumn - 1), self.panel)) #append the move to the list of moves
                elif (row - 1, coloumn - 1) == self.ep_possible and row-1>=0 and coloumn -1 >=0:  # en passant capture if it is a valid square and it is on the board
                    moves.append(Move((row, coloumn), (row - 1, coloumn - 1), self.panel, is_enpassant=True)) #append the move to the list of moves
            if coloumn + 1 <= 7:    # captures to the right
                if self.panel[row - 1][coloumn + 1][0] == 'b':  # enemy piece to capture and check if it is a valid square and it is the board
                    moves.append(Move((row, coloumn), (row - 1, coloumn + 1), self.panel)) #append the move to the list of moves
                elif (row - 1, coloumn + 1) == self.ep_possible:  # en passant capture if it is a valid square
                    moves.append(Move((row, coloumn), (row - 1, coloumn + 1), self.panel, is_enpassant=True)) #append the move to the list of moves

        else:  # black's pawn moves as it is black's turn
            if row + 1 < len(self.panel) and self.panel[row + 1][coloumn] == '__': # 1 square move and check if it is a valid square and it is on the board
                moves.append(Move((row, coloumn), (row + 1, coloumn), self.panel)) #append the move to the list of moves
                if row == 1 and self.panel[row + 2][coloumn] == '__':  # 2 square move if it is a valid square and it is on the board
                    moves.append(Move((row, coloumn), (row + 2, coloumn), self.panel)) #append the move to the list of moves
            if coloumn + 1 <= 7:  # captures to the right
                if row + 1 < len(self.panel) and self.panel[row + 1][coloumn + 1][0] == 'w': # enemy piece to capture and check if it is a valid square and it is the board
                    moves.append(Move((row, coloumn), (row + 1, coloumn + 1), self.panel)) #append the move to the list of moves
                elif (row + 1, coloumn + 1) == self.ep_possible and row+1< 8 and coloumn+1< 8:  # en passant capture if it is a valid square and it is on the board
                    moves.append(Move((row, coloumn), (row + 1, coloumn + 1), self.panel, is_enpassant=True)) #append the move to the list of moves
            if coloumn - 1 >= 0:  # captures to the left (could write this as len(self.panel) and this in later)
                if row+ 1 < len(self.panel) and self.panel[row + 1][coloumn - 1][0] == 'w':  # enemy piece to capture and check if it is a valid square and it is the board
                    moves.append(Move((row, coloumn), (row + 1, coloumn - 1), self.panel)) #append the move to the list of moves
                elif (row + 1, coloumn - 1) == self.ep_possible:  # en passant capture if it is a valid square
                    moves.append(Move((row, coloumn), (row + 1, coloumn - 1), self.panel, is_enpassant=True)) #append the move to the list of moves


    def get_rook_moves(self, row, coloumn, moves): # get all the possible rook moves
        left = right = up = down = 1 #set the left, right, up and down variables to 1 (offset essentially)
        e = 'b' if self.player_1 else 'w' #set the enemy piece to black if it is white's turn and vice versa
        # Left of the Rook 
        stop = False #set the stop variable to false
        while coloumn - left >= 0 and not stop: #while the coloumn - left is greater than or equal to 0 and stop is false (while the square is on the board and the rook can move further)
            end_piece = self.panel[row][coloumn - left] #set the end_piece variable to the piece at the square to the left of the rook
            # when the square to the left is empty
            if end_piece == '__': 
                moves.append(Move((row, coloumn), (row, coloumn - left), self.panel)) #append the move to the list of moves
                left += 1 #increment the left variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row, coloumn - left), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else: #if the square contains a friendly piece
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)

        stop = False #set the stop variable to false as we are checking the squares to the right of the rook
        while coloumn + right < 8 and not stop: #while the coloumn + right is less than 8 and stop is false (while the square is on the board and the rook can move further)
            end_piece = self.panel[row][coloumn + right] #set the end_piece variable to the piece at the square to the right of the rook
            # when the square to the left is empty
            if end_piece == '__': 
                moves.append(Move((row, coloumn), (row, coloumn+ right), self.panel)) #append the move to the list of moves
                right += 1 #increment the right variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e: 
                moves.append(Move((row, coloumn), (row, coloumn + right), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else: #if the square contains a friendly piece
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)

        stop = False #set the stop variable to false as we are checking the squares above the rook
        while row - up >= 0 and not stop: #while the row - up is greater than or equal to 0 and stop is false (while the square is on the board and the rook can move further)
            end_piece = self.panel[row - up][coloumn] #set the end_piece variable to the piece at the square above the rook
            # when the square to the left is empty
            if end_piece == '__': 
                moves.append(Move((row, coloumn), (row - up, coloumn), self.panel)) #append the move to the list of moves
                up += 1 #increment the up variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row - up,coloumn), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else:
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)

        stop = False #set the stop variable to false as we are checking the squares below the rook
        while row + down < 8 and not stop:  #while the row + down is less than 8 and stop is false (while the square is on the board and the rook can move further)
            end_piece = self.panel[row + down][coloumn] #set the end_piece variable to the piece at the square below the rook
            # when the square to the left is empty
            if end_piece == '__': 
                moves.append(Move((row, coloumn), (row + down, coloumn), self.panel)) #append the move to the list of moves
                down += 1 #increment the down variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row + down,coloumn), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else:
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)

        


            


    def get_bishop_moves(self, row, coloumn, moves): # get all the possible bishop moves
        left = right = up = down = 1 #set the left, right, up and down variables to 1 (offset essentially)
        e = 'b' if self.player_1 else 'w' #set the enemy piece to black if it is white's turn and vice versa    
        stop = False #set the stop variable to false as we are checking the diagonal squares to the top left of the bishop
        while coloumn - left >= 0 and row - up >= 0 and not stop: #while the coloumn - left is greater than or equal to 0 and the row - up is greater than or equal to 0 and stop is false (while the square is on the board and the bishop can move further)
            end_piece = self.panel[row- up][coloumn - left] #set the end_piece variable to the piece at the square to the top left of the bishop
            # when the square to the left is empty
            if end_piece == '__':
                moves.append(Move((row, coloumn), (row - up, coloumn - left), self.panel)) #append the move to the list of moves
                left += 1 #increment the left variable by 1
                up +=1 #increment the up variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row - up, coloumn - left), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else:
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)


        left = 1 #set the left variable to 1 as it was changed in the previous loop
        stop = False #set the stop variable to false as we are checking the diagonal squares to the bottom left of the bishop
        while coloumn - left >= 0 and row + down < 8 and not stop: #while the coloumn - left is greater than or equal to 0 and the row + down is less than 8 and stop is false (while the square is on the board and the bishop can move further)
            end_piece = self.panel[row+ down][coloumn -left] #set the end_piece variable to the piece at the square to the bottom left of the bishop
            # when the square to the left is empty
            if end_piece == '__':
                moves.append(Move((row, coloumn), (row+ down, coloumn - left), self.panel)) #append the move to the list of moves
                left += 1 #increment the left variable by 1
                down +=1 #increment the down variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row+ down, coloumn- left), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else:
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces) 

        up = 1 #set the up variable to 1 as it was changed in the previous loop
        stop = False #set the stop variable to false as we are checking the diagonal squares to the top right of the bishop
        while row - up >= 0 and coloumn + right < 8 and not stop:  #while the row - up is greater than or equal to 0 and the coloumn + right is less than 8 and stop is false (while the square is on the board and the bishop can move further)
            end_piece = self.panel[row - up][coloumn+ right] #set the end_piece variable to the piece at the square to the top right of the bishop
            # when the square to the left is empty
            if end_piece == '__': 
                moves.append(Move((row, coloumn), (row - up, coloumn+ right), self.panel)) #append the move to the list of moves
                up +=1 #increment the up variable by 1
                right +=1 #increment the right variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row - up,coloumn+right), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else:
                stop = True     #set the stop variable to true as you cannot move further (you cannot jump over pieces)


        down = right = 1 #set the down and right variables to 1 as they were changed in the previous loop
        stop = False #set the stop variable to false as we are checking the diagonal squares to the bottom right of the bishop
        while row + down < 8 and coloumn + right < 8 and not stop:
            end_piece = self.panel[row + down][coloumn+ right] #set the end_piece variable to the piece at the square to the bottom right of the bishop
            # when the square to the left is empty
            if end_piece == '__':
                moves.append(Move((row, coloumn), (row + down, coloumn+ right), self.panel)) #append the move to the list of moves
                down +=1 #increment the down variable by 1
                right +=1 #increment the right variable by 1
            # when the square contains an opposing piece
            elif end_piece[0] == e:
                moves.append(Move((row, coloumn), (row + down,coloumn+right), self.panel)) #append the move to the list of moves
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)
            else:
                stop = True #set the stop variable to true as you cannot move further (you cannot jump over pieces)








    def get_knight_moves(self, row, coloumn, moves): #function to get the possible moves for a knight
        ally_colour = 'w' if self.player_1 else 'b' #set the ally_colour variable to 'w' if the player is white and 'b' if the player is black
        if row + 2 < 8 and coloumn - 1 >= 0: #if the row + 2 is less than 8 and the coloumn - 1 is greater than or equal to 0
            end_piece = self.panel[row+2][coloumn-1] #set the end_piece variable to the piece at the square to the bottom left of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row+2, coloumn-1), self.panel)) #append the move to the list of moves
        if row - 2 >= 0 and coloumn - 1 >=0: #if the row - 2 is greater than or equal to 0 and the coloumn - 1 is greater than or equal to 0
            end_piece = self.panel[row-2][coloumn-2] #set the end_piece variable to the piece at the square to the top left of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row-2, coloumn-1), self.panel)) #append the move to the list of moves
        if coloumn + 1 < 8 and row -2 >= 0: #if the coloumn + 1 is less than 8 and the row - 2 is greater than or equal to 0
            end_piece = self.panel[row-2][coloumn+1] #set the end_piece variable to the piece at the square to the top right of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row-2, coloumn+1), self.panel)) #append the move to the list of moves
        if coloumn - 2 >= 0 and row-1 >=0: #if the coloumn - 2 is greater than or equal to 0 and the row - 1 is greater than or equal to 0
            end_piece = self.panel[row-1][coloumn-2]    #set the end_piece variable to the piece at the square to the top left of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row-1, coloumn-2), self.panel)) #append the move to the list of moves
        if coloumn +2 < 8 and row -1 >= 0:  #if the coloumn + 2 is less than 8 and the row - 1 is greater than or equal to 0
            end_piece = self.panel[row-1][coloumn+2] #set the end_piece variable to the piece at the square to the top right of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row-1, coloumn+2), self.panel)) #append the move to the list of moves
        if coloumn - 2 >= 0 and row + 1 < 8: #if the coloumn - 2 is greater than or equal to 0 and the row + 1 is less than 8
            end_piece = self.panel[row+1][coloumn-2] #set the end_piece variable to the piece at the square to the bottom left of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row+1, coloumn-2), self.panel)) #append the move to the list of moves
        if row + 1 < 8 and coloumn + 2 < 8: #if the row + 1 is less than 8 and the coloumn + 2 is less than 8
            end_piece = self.panel[row+1][coloumn+2] #set the end_piece variable to the piece at the square to the bottom right of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row+1, coloumn+2), self.panel)) #append the move to the list of moves
        if row + 2  < 8 and coloumn + 1 < 8: #if the row + 2 is less than 8 and the coloumn + 1 is less than 8
            end_piece = self.panel[row+2][coloumn+1] #set the end_piece variable to the piece at the square to the bottom right of the knight
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the knight
                moves.append(Move((row, coloumn), (row+2, coloumn+1), self.panel)) #append the move to the list of moves
        


    def get_queen_moves(self, row, coloumn, moves): #function to get the queen moves
        self.get_rook_moves(row, coloumn, moves) #get the rook moves
        self.get_bishop_moves(row, coloumn, moves) #get the bishop moves
        # queen moves are the same as the rook and bishop moves combined

    def get_king_moves(self, row, coloumn, moves):  #function to get the king moves
        ally_colour = 'w' if self.player_1 else 'b' #set the ally_colour variable to the colour of the player
        down = right = left = up = 1 #set the down, right, left and up variables to 1 (offsets)
        if row + down < 8: #if the row + down is less than 8
            end_piece = self.panel[row+down][coloumn] #set the end_piece variable to the piece at the square below the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row+down, coloumn), self.panel)) #append the move to the list of moves
        if row - up >= 0: #if the row - up is greater than or equal to 0
            end_piece = self.panel[row-up][coloumn] #set the end_piece variable to the piece at the square above the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row-up, coloumn), self.panel)) #append the move to the list of moves
        if coloumn + right < 8: #if the coloumn + right is less than 8
            end_piece = self.panel[row][coloumn+right] #set the end_piece variable to the piece at the square to the right of the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row, coloumn+right), self.panel)) #append the move to the list of moves
        if coloumn - left >= 0: #if the coloumn - left is greater than or equal to 0
            end_piece = self.panel[row][coloumn-left] #set the end_piece variable to the piece at the square to the left of the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row, coloumn-left), self.panel)) #append the move to the list of moves
        if coloumn - left >= 0 and row - up >= 0: #if the coloumn - left is greater than or equal to 0 and the row - up is greater than or equal to 0
            end_piece = self.panel[row-up][coloumn-left] #set the end_piece variable to the piece at the square to the top left of the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row-up, coloumn-left), self.panel)) #append the move to the list of moves
        if coloumn - left >= 0 and row + down < 8:  #if the coloumn - left is greater than or equal to 0 and the row + down is less than 8
            end_piece = self.panel[row+down][coloumn-left] #set the end_piece variable to the piece at the square to the bottom left of the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row+down, coloumn-left), self.panel)) #append the move to the list of moves
        if row - up >= 0 and coloumn + right < 8: #if the row - up is greater than or equal to 0 and the coloumn + right is less than 8
            end_piece = self.panel[row-up][coloumn+right] #set the end_piece variable to the piece at the square to the top right of the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row-up, coloumn+right), self.panel)) #append the move to the list of moves
        if row + down < 8 and coloumn + right < 8: #if the row + down is less than 8 and the coloumn + right is less than 8
            end_piece = self.panel[row+down][coloumn+right] #set the end_piece variable to the piece at the square to the bottom right of the king
            if end_piece[0] != ally_colour: #if the piece is not the same colour as the king
                moves.append(Move((row, coloumn), (row+down, coloumn+right), self.panel)) #append the move to the list of moves

        


    def acquire_c_moves(self, row, coloumn, moves): #function to get the castle moves
        if self.player_1: #if it is the white player
            self.player_1 = not self.player_1 #sswitch the player
            opp_moves = self.acquire_every_move() #get the opponents moves
            for move in opp_moves: #for every move in the opponents moves
                if move.finish_r == row and move.finish_c == coloumn: #if the move ends on the same square as the king
                    self.player_1 = not self.player_1 #switch the player
                    return #return
            self.player_1 = not self.player_1 #switch the player
            # cant castle when in check therefore no need to check if we can castle or not
        if (self.player_1 and self.live_castle_possible.wks) or ( 
                not self.player_1 and self.live_castle_possible.bks): #if it is the white player and the white king side castle is possible or if it is the black player and the black king side castle is possible
            self.get_king_side_castle_moves(row, coloumn, moves)
        if (self.player_1 and self.live_castle_possible.wqs) or (
                not self.player_1 and self.live_castle_possible.bqs): #if it is the white player and the white queen side castle is possible or if it is the black player and the black queen side castle is possible
            self.get_queen_side_castle_moves(row, coloumn, moves)

    def get_king_side_castle_moves(self, row, coloumn, moves): #function to get the king side castle moves
        castling_sqaures_in_check = False #set the castling_sqaures_in_check variable to False as we have not checked if the castling squares are in check
        if row>=0 and coloumn +2 <8 and coloumn +1<= 8: #if the row is less than or equal to 0 and the coloumn + 2 is less than or equal to 7
            if self.panel[row][coloumn + 1] == '__' and self.panel[row][coloumn + 2] == '__': #we can only castle if  the square to the right of the king is empty and the square 2 to the right of the king is empty
                self.player_1 = not self.player_1 #switch the player
                opp_moves = self.acquire_every_move() #get the opponents moves
                for move in opp_moves: #for every move in the opponents moves
                    if (move.finish_r == row and move.finish_c == coloumn+1) or (move.finish_r ==  row and move.finish_c == coloumn+2): #if the move ends on the square to the right of the king or the square 2 to the right of the king
                        self.player_1 = not self.player_1 #switch the player
                        castling_sqaures_in_check = True #set the castling_sqaures_in_check variable to True as the castling squares are in check
                        return castling_sqaures_in_check #return the castling_sqaures_in_check variable
                self.player_1 = not self.player_1 #switch the player
                if castling_sqaures_in_check == True: #if the castling_sqaures_in_check variable is True
                    return #return as we cant castle
                elif castling_sqaures_in_check == False: #if the castling_sqaures_in_check variable is False
                    moves.append(Move((row, coloumn), (row, coloumn + 2), self.panel, is_c_move=True)) #append the move to the list of moves


    def get_queen_side_castle_moves(self, row, coloumn, moves): #function to get the queen side castle moves
        castling_sqaures_in_check = False  #set the castling_sqaures_in_check variable to False as we have not checked if the castling squares are in check
        if row >=0 and coloumn - 1 >=0 and coloumn - 2>=0 :
            if self.panel[row][coloumn - 1] == '__' and self.panel[row][coloumn - 2] == '__' and self.panel[row][coloumn - 3] == '__': #we can only castle if  the square to the left of the king is empty and the square 2 to the left of the king is empty and the square 3 to the left of the king is empty
                self.player_1 = not self.player_1 #switch the player
                opp_moves = self.acquire_every_move() #get the opponents moves
                for move in opp_moves: #for every move in the opponents moves
                    if (move.finish_r == row and move.finish_c == coloumn-1) or (move.finish_r ==  row and move.finish_c == coloumn-2): #if the move ends on the square to the left of the king or the square 2 to the left of the king
                        self.player_1 = not self.player_1 #switch the player
                        castling_sqaures_in_check = True #set the castling_sqaures_in_check variable to True as the castling squares are in check
                        return castling_sqaures_in_check #return the castling_sqaures_in_check variable
                self.player_1 = not self.player_1 #switch the player
                if castling_sqaures_in_check == True: #if the castling_sqaures_in_check variable is True
                    return #return as we cant castle
                elif castling_sqaures_in_check == False: #if the castling_sqaures_in_check variable is False
                    moves.append(Move((row, coloumn), (row, coloumn -2), self.panel, is_c_move=True)) #append the move to the list of moves




class castle_possible(object): #class to store the castle possible variables
    def __init__(self, wks, bks, wqs, bqs): #initialise the class
        self.wks = wks  #white king side castle possible
        self.bks = bks #black king side castle possible
        self.wqs = wqs #white queen side castle possible
        self.bqs = bqs #black queen side castle possible




