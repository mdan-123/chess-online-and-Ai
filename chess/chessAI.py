import numpy as np
from chessEngine import Game 


class ChessAI: 
    DEPTH = 3 

    def __init__(self): 
        self.game = Game() # create a game object that will be used to simulate moves
        self.generated_move = False  # the move that the ai has generated set to false
        self.thinking = False # is the ai thinking set to false
        self.suicide = False 

    def __call__(self): 
        self.thinking = True 
        self.generated_move = self._ai_move() # set generated move to what the ai has said
        self.thinking = False 
        self.suicide = False

    def kill(self): #kill the ai
        self.suicide = True

    def _ai_move(self): #function for the ai to find the best move
        bestmove = None #set to None as it has not been found yet
        bestvalue = -9999 
        alpha = -100000 
        beta = 100000
        valid_moves = self.game.get_correct_moves() #get all the valid moves in the game
        for i, move in enumerate(valid_moves): # for all the moves 
            if self.suicide: 
                return
            alpha = -100000 #must be reset at the top end of the tree 
            beta = 100000
            print(f"{i+1}/{len(valid_moves)} {str(move)}", end=' ', flush=True)
            self.game.make_move(move) #makes the move
            current_state_value = -self._alphabeta(-beta, -alpha, self.DEPTH  - 1) #searches down the tree 
            if current_state_value > bestvalue: #compares the values given by the alphabeta function
                bestvalue = current_state_value
                bestmove = move
            if current_state_value > alpha:   
                alpha = current_state_value 
            self.game.reverse_move() #reverses the move
            print(bestmove, bestvalue)
        return bestmove

    def _alphabeta(self, alpha, beta, DEPTH):
        besttotal = -9999 
        if DEPTH == 0: #stop the recursion
            return self._quiet_move(alpha, beta)
        for move in self.game.get_correct_moves():
            self.game.make_move(move)            
            total = -self._alphabeta(-beta, -alpha, DEPTH - 1)
            self.game.reverse_move()            
            if total >= beta:
                return total
            if total > besttotal:
                besttotal = total
            if total> alpha:
                alpha = total
        return besttotal

    def _quiet_move(self, alpha, beta):
        #this is run when the depth is 0 and it used to stop the horizon effect
        current_state = self.current_state_of_board()
        if current_state >= beta:
            return beta
        if alpha < current_state:
            alpha = current_state
        for move in self.game.get_correct_moves() or []:
            if move.piece_taken != '__':
                self.game.make_move(move)
                total = -self._quiet_move(-beta, -alpha)
                self.game.reverse_move()
                if total >= beta:
                    return beta
                if total > alpha:
                    alpha = total

        return alpha
    
    def current_state_of_board(self):
        """ Return score representing the current player's position """
        evaluation = self.piece_score() + self._scoreBoard()
        if self.game.player_1 == True:
            return evaluation
        else:
            return -evaluation  

    def _scoreBoard(self):
        """
        Score the board. A positive score is good for white, a negative score is good for black. This takes into account what is going on in the current state of the board. Meaning it takes
        the current PSQT and totals them White will give a positive answer while black will try to negate that answer.
        """
        score = 0
        for i in range(8):
            for j in range(8):
                piece = self.game.panel[i][j]
                if piece != "__":
                    b_pawn = np.flip(self.game.pawn_table)
                    b_rook = np.flip(self.game.rook_table)
                    b_knight = np.flip(self.game.knight_table)
                    b_queen = np.flip(self.game.queen_table)
                    b_bishop = np.flip(self.game.bishop_table)
                    b_king = np.flip(self.game.king_table)
                    if piece[0] != 'b': 
                        if piece[1] == 'p':
                            score -= self.game.pawn_table[i][j]
                        elif piece[1] == 'r':
                            score -= self.game.rook_table[i][j]
                        elif piece[1] == 'h':
                            score -= self.game.knight_table[i][j]
                        elif piece[1] == 'q':
                            score -= self.game.queen_table[i][j]
                        elif piece[1] == 'B':
                            score -= self.game.bishop_table[i][j]
                        elif piece[1] == 'k':
                            score -= self.game.king_table[i][j]                              
                    elif piece[0] == "b":
                        if piece[1] == 'p':
                            score -= b_pawn[i][j]
                        elif piece[1] == 'r':
                            score -= b_rook[i][j]
                        elif piece[1] == 'h':
                            score -= b_knight[i][j]
                        elif piece[1] == 'q':
                            score -= b_queen[i][j]
                        elif piece[1] == 'B':
                            score -= b_bishop[i][j]
                        elif piece[1] == 'k':
                            score -= b_king[i][j]

        # print(score)
        return score

    def piece_score(self):
        """ Material points difference between white and back
        """
        pawn = 0
        rook = 0
        bishop = 0
        queen = 0
        knight = 0
        for i in range(8):
            for j in range(8):
                piece = self.game.panel[i][j]
                if piece != "__" and piece != 'k':
                    if piece == 'wp':
                        pawn += 1
                    elif piece == 'bp':
                        pawn -= 1

                    elif piece == 'wr':
                        rook += 1
                    elif piece == 'br':
                        rook -= 1
                        
                    elif piece == 'wB':
                        bishop += 1
                    elif piece == 'bB':
                        bishop -= 1
                    
                    elif piece == 'wh':
                        knight += 1
                    elif piece == 'bh':
                        knight -= 1
                    
                    elif piece == 'wq':
                        queen += 1
                    elif piece == 'bq':
                        queen -= 1

        piece_score = 100 * pawn + 320 * knight + 320 * bishop + 500 * rook + 900 * queen
        return piece_score
            
    

    

    