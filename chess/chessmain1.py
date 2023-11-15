import pygame
import chessEngine
from chessAI import ChessAI
from chessclient2 import ChessClient
import threading
import sys


global width #global variables
width = 800
global height
height = 800
#chess panel is 8 by 8
global Square_size
Square_size = height // 8
global fps
fps = 120
global images
images = {}






#main driver for the code. User input and updating graphics
def main(host, port, create_or_join ,play_online, play_ai): 
    assert bool(play_online) != bool(play_ai), "Either online or ai must be true"
    
    # if playing online, create a chess client and establish connection with peer before continuing
    if play_online:
        client = ChessClient() #create a chess client
        if create_or_join == 'c': #if creating a game
            port = int(port) #convert port to int
            host = host #convert host to string
            client.create_game(host = host, port=port) #create a game
        elif create_or_join == 'j':
            port = int(port) #convert port to int
            host = host #convert host to string
            client.join_game(host, port) #join a game
        assert client.connected_to_peer() #assert that we are connected to a peer

    # if playing ai, create chess ai ready to play
    else:
        ai = ChessAI() #create a chess ai


    music_on = True
    
    pygame.mixer.music.load('audio/song2.mp3') #loads the music, this is only for the menus and not the game
    pygame.mixer.music.play(loops=-1) #plays the music

    pygame.init() #initialises pygame
    screen = pygame.display.set_mode((width,height)) #sets the screen size
    clock = pygame.time.Clock() #sets the clock
    screen.fill(pygame.Color('white')) #sets the background colour
    game = chessEngine.Game() #creates a game
    
    valid_moves = game.get_correct_moves() #gets the valid moves
    made_move = False #FLAG variable for when a move is made
    load_images() #once, before the while loop
    need_to_animate  = False #flag variable for when we should need_to_animate a move
    running = True #sets running to true
    square_selected = () #no square is selected, keep track of the last click of the user (tuple: (row,col))
    playerClicked = [] #keep track of player clicks (two tuples[(6,4), (4,4)])
    game_over = False #flag variable for when the game is over
    move_undone = False #flag variable for when a move is undone


    global human_is_player1 #global variables
    human_is_player1 = play_ai or client.is_player_1 #if playing ai, then human is player 1
    human_is_player2 = play_online and client.is_player_2     #if playing online, then human is player 2

    def make_move_on_opponent_board(move): #makes a move on the opponent board
        if play_ai: #if playing ai
            ai.game.make_move(move) #make a move on the ai board
        else: #if playing online
            success = client.send_data(move.serialize()) #send the move to the opponent
            if not success: #if the move was not successful
                print("Couldn't send move!") #print that the move was not successful
                exit() #exit the program
        
    
    #draws all the graphics on the game 
    def draw_game(screen, game_state, valid_moves, square_selected): 
        draw_panel(screen) #draws the board
        highlight_squares(screen, game_state, valid_moves, square_selected, flipped=human_is_player2) #highlights the squares
        draw_pieces(screen, game_state.panel, flipped=human_is_player2) #pieces on top of the squares
    
    draw_game(screen,game, valid_moves, square_selected) #draws the game

    while running: #while running is true
        clock.tick(fps) #sets the clock
        pygame.display.flip() #updates the display
        humanturn = (game.player_1 and human_is_player1) or (game.player_2 and human_is_player2) #if it is the human's turn

        if pygame.mixer.music.get_busy() == False: #if the music is not playing
            pass 


        for event in pygame.event.get(): #gets the events
            match event.type: #matches the event type
                case pygame.QUIT: #if the user clicks the x
                    running = False #running is false
                    pygame.quit() #quits pygame
                    sys.exit()  #exits the program
                    #mouse handler 
                case pygame.MOUSEBUTTONDOWN: #if the user clicks the mouse
                    if not game_over and humanturn: #if the game is not over and it is the human's turn
                        location = pygame.mouse.get_pos() #x,y pos of the mouse
                        coloumn = location[0]//Square_size #gets the coloumn
                        row = location[1]//Square_size #gets the row
                        if human_is_player2: #if the human is player 2
                            coloumn = 8 - coloumn - 1 #flip the coloumn
                            row = 8 - row - 1 #flip the row
                        if square_selected == (row,coloumn): #the user clicked on the same square twice
                            square_selected = () #deselct
                            playerClicked = [] #clear the player clicks
                        else: #if the user clicked on a different square
                            square_selected = (row,coloumn) #select the square
                            playerClicked.append(square_selected) #append for both 1st and 2nd clicks
                        match len(playerClicked): #match the length of the player clicks
                            case 2: #after 2nd click
                                move = chessEngine.Move(playerClicked[0],playerClicked[1], game.panel) #create a move object based on player clicks
                                for i in range(len(valid_moves)): #for all the valid moves
                                    if move == valid_moves[i]: #if the move is valid
                                        game.make_move(valid_moves[i]) #make the move
                                        make_move_on_opponent_board(valid_moves[i]) #make the move on the opponent board
                                        made_move = True #a move has been made
                                        need_to_animate = True #we need to animate the move
                                        square_selected = () #reset user clicks
                                        playerClicked = [] #reset user clicks
                                if not made_move: #if a move has not been made
                                    playerClicked = [square_selected] #reset user clicks
                #key handler
                case pygame.KEYDOWN: #if the user presses a key
                    if play_ai: #if playing ai
                        match event.key: #match the key
                            case pygame.K_z: #if the user presses z
                                if ai.thinking: #if the ai is thinking
                                    ai.kill() #kill the ai
                                else: #if the ai is not thinking
                                    game.reverse_move() #reverse the move
                                    ai.game.reverse_move() 
                                game.reverse_move()
                                ai.game.reverse_move() 
                                made_move = True #a move has been made
                                need_to_animate =  False #we do not need to animate the move
                            case pygame.K_4: #if the user presses 4
                                if music_on==True: #if the music is on
                                    pygame.mixer.music.stop() #stop the music
                                    music_on = False #music is off
                                elif music_on==False: #if the music is off
                                    pygame.mixer.music.play(loops=-1) #play the music
                                    music_on = True #music is on
                            case pygame.K_r: #if the user presses r
                                    pygame.mixer.music.load('audio/song1.mp3') #loads the other song
                                    pygame.mixer.music.play(loops=-1)
                            case pygame.K_t:
                                    pygame.mixer.music.load('audio/song2.mp3') #loads the other song
                                    pygame.mixer.music.play(loops=-1)
                                
                                
                
        


        # opponent move
        if not game_over and not humanturn and not move_undone: #if the game is not over and it is not the human's turn and the move has not been undone
            if play_ai:  #if playing ai
                if ai.generated_move: #if the ai has generated a move
                    move = ai.generated_move #get the move
                    ai.generated_move = None #reset the move
                    game.make_move(move) #make the move
                    ai.game.make_move(move) #make the move on the ai board
                    made_move = True #a move has been made
                    need_to_animate = True #we need to animate the move 
                    print("Made move") #print made move
                elif not ai.thinking: #if the ai is not thinking
                    ai_thinking_thread = threading.Thread(target=ai) #create a thread for the ai
                    print("Thinking...") 
                    ai_thinking_thread.start() #start the thread
            else: #if not playing ai
                valid_moves = game.get_correct_moves() #get the valid moves
                valid_moves_serialized = [move.serialize() for move in valid_moves] #serialize the valid moves
                print(valid_moves_serialized) 
                move_string = client.get_data_from_peer(valid_moves_serialized) #get the move from the opponent
                print(move_string)
                if not move_string: #if the move is not valid
                    print("Didn't receive valid move!") #print didn't receive valid move
                    exit() #exit the program
                move = chessEngine.Move.fromSerializedRepresentation(game, move_string) #create a move object based on the move string
                game.make_move(move) #make the move
                made_move = True #a move has been made
                need_to_animate = True #we need to animate the move
          
        if made_move: #if a move has been made
            if need_to_animate: #if we need to animate the move
                animating_moves(game.record_for_move[-1], screen, game.panel, clock, flipped=human_is_player2, is_our_move=humanturn) #animate the move
            valid_moves = game.get_correct_moves() #get the valid moves
            made_move = False #reset made move
            need_to_animate = False #reset need to animate
            move_undone = False     
        
        draw_game(screen,game, valid_moves, square_selected) #draw the game
        
        match game.end: #match the end of the game
            case True: #if the game has ended
                font = pygame.font.Font(None, 50) #create a font
                colour = pygame.Color('blue') #create a colour
                match game.check_mate: #match the checkmate
                    case True: #if checkmate
                        if game.player_1: #if player 1
                            font_text = font.render('black wins by checkmate', True, colour) #create a font text
                            screen.blit(font_text, (200,370)) #draw the font text
                            end_game() #end the game
                        elif not game.player_1: #if player 2
                            font_text = font.render('white wins by checkmate', True, colour) #create a font text
                            screen.blit(font_text, (200,370)) #draw the font text
                            end_game() #end the game
                match game.stalemate: #match the stalemate
                    case True: #if stalemate
                        font_text = font.render('Stalemate has been reached', True, colour) #create a font text
                        screen.blit(font_text, (200,370)) #draw the font text
                        end_game() #end the game

#highlight sqaure selected and moves for pieces selected



def end_game(): #end the game
    pygame.display.update()     
    pygame.display.flip()
    pygame.event.pump()
    pygame.time.delay(5 * 1000)
    pygame.quit()
    sys.exit()

def highlight_squares(screen, game, valid_moves, sqaure_selected, flipped): #add last move highlighted 
    # square_selected is coordinates of selected square on a white-player board
    if sqaure_selected != (): #if a square has been selected
        enemy_colour = 'b' if human_is_player1 else 'w' #get the enemy colour
        row = sqaure_selected[0] #get the row
        coloumn = sqaure_selected[1]    #get the coloumn
        if ((game.player_1 and game.panel[row][coloumn][0] == 'w') 
            or (game.player_2 and game.panel[row][coloumn][0] == 'b')): #square selected is a piece that can be movec
            # highlight selected square
            surf = pygame.Surface((Square_size,Square_size)) #create a surface
            surf.set_alpha(100) #transparency value
            surf.fill(pygame.Color('dark blue')) #fill the surface with a colour
            highlight_coloumn = coloumn if not flipped else 8 - coloumn - 1 #if flipped is true then flip the board
            highlight_row = row if not flipped else 8 - row - 1 #if flipped is true then flip the board
            co_ords = (highlight_coloumn*Square_size, highlight_row*Square_size) #get the coordinates
            screen.blit(surf, co_ords) #draw the surface on the screen
            # highlight moves from that square
            surf.fill(pygame.Color('orange')) #fill the surface with a colour
            for move in valid_moves: #for each move in the valid moves
                if move.beg_r == row and move.beg_c == coloumn: #if the move is the same as the selected square
                    # we need to draw on a black board if flipped=True
                    finish_c = move.finish_c if not flipped else 8 - move.finish_c - 1 
                    finish_r = move.finish_r if not flipped else 8 - move.finish_r - 1
                    co_ords = Square_size*finish_c, Square_size*finish_r #get the coordinates
                    end_piece = game.panel[finish_r][finish_c] if not flipped else game.panel[8 - finish_r - 1][8- finish_c- 1] #get the end piece
                    if end_piece[0] == enemy_colour: #if the end piece is the enemy colour
                        surf.fill(pygame.Color('red')) #fill the surface with a colour
                        screen.blit(surf, co_ords) #draw the surface on the screen
                    else:
                        surf.fill(pygame.Color('orange')) #fill the surface with a colour
                        screen.blit(surf, co_ords) #draw the surface on the screen



#draws the squares
def draw_panel(screen): #draws the board
    global colours 
    colours = [pygame.Color('white'), pygame.Color('light grey')] #create a list of colours
    for row in range(8):  #for each row
        for coloumn in range(8): #for each coloumn
            colour = colours[((row+coloumn)%2)] #get the colour
            rect = pygame.Rect(coloumn*Square_size, row*Square_size, Square_size, Square_size) #create a rectangle
            pygame.draw.rect(screen , colour , rect) #draw the rectangle



#draws the pieces on the panel
def draw_pieces(screen, panel, flipped):
    for row in range(8): #for each row
        for coloumn in range(8): #for each coloumn
            piece = panel[row][coloumn] if not flipped else panel[8-row-1][8-coloumn-1] #get the piece
            if piece != '__': #not empty 
                rect = pygame.Rect(coloumn *Square_size, row*Square_size, Square_size, Square_size)
                screen.blit(images[piece], rect) #draw the piece on the screen


#animating moves

def animating_moves(move: chessEngine.Move, screen, panel, clock, flipped, is_our_move):
    global colours
    beg_r = 8 - move.beg_r - 1 if flipped else move.beg_r #if flipped is true then flip the board
    beg_c = 8 - move.beg_c - 1 if flipped else move.beg_c #if flipped is true then flip the board
    finish_r = 8 - move.finish_r - 1 if flipped else move.finish_r #if flipped is true then flip the board
    finish_c = 8 - move.finish_c - 1 if flipped else move.finish_c #if flipped is true then flip the board
    how_many_rows_moved = finish_r - beg_r #how many rows moved
    how_many_coloumns_moved = finish_c - beg_c #how many coloumns moved
    frames_per_square = 5 #frames per square
    frame_count = ((abs(how_many_rows_moved) + abs(how_many_coloumns_moved)) * frames_per_square) + 1 #frame count
    for frame in range(frame_count): #for each frame
        row = beg_r + how_many_rows_moved* frame/frame_count #get the row
        coloumn = beg_c + how_many_coloumns_moved*frame/frame_count #get the coloumn
        draw_panel(screen) #draw the board
        draw_pieces(screen, panel, flipped=flipped) #draw the pieces
        #the piece moved will alr be at end square so we need to erase that
        colour = colours[((finish_r + finish_c)%2)] #get the colour
        end_square = pygame.Rect(finish_c* Square_size, finish_r*Square_size, Square_size, Square_size) #create a rectangle
        pygame.draw.rect(screen,colour, end_square) #draw the rectangle
        #draw captured piece back
        if move.piece_taken != '__': #if the piece taken is not empty
            if move.is_ep: #if the move is en passant
                enpassant_row = finish_r + (1 if is_our_move else - 1) #get the enpassant row
                square_piece_was_taken_from = pygame.Rect(finish_c* Square_size, enpassant_row*Square_size, Square_size, Square_size) #create a rectangle
            else:
                square_piece_was_taken_from = end_square #create a rectangle 
            screen.blit(images[move.piece_taken], square_piece_was_taken_from) #draw the piece on the screen
        #drawing moving piece
        rect = pygame.Rect(coloumn * Square_size, row* Square_size, Square_size,Square_size) #create a rectangle
        screen.blit(images[move.piece_advanced], rect) #draw the piece on the screen
        pygame.display.flip() 
        clock.tick(60)


#Initalize a global dictionary of images. Called once
def load_images():
    pieces = ['bB','bk','bh','bp','bq','br','wB','wk','wh','wp','wq','wr'] #create a list of pieces
    for piece in pieces: #for each piece
        images[piece] = pygame.transform.scale(pygame.image.load('graphics/' + piece + '.png'), (Square_size,Square_size)) #load the image and scale it