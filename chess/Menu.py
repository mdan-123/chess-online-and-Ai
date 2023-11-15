import pygame
from buttons import Button, InputButton
import chessmain1
import sys




class Menu(): #menu class
    def __init__(self, surface, width , height, screen):
        self.background = pygame.transform.scale(pygame.image.load('graphics/background.png'), (width, height)) #loads the background image
        self.title = pygame.transform.scale(pygame.image.load('graphics/title.jpeg'), (250, 250)) #loads the title image
        self.surface = surface 
        self.width = width
        self.height = height
        self.screen = screen
        self.surface_width = 800
        self.surface_height = 800
        self.buttons = {}
        self.buttons['Start Server'] = Button(300,300,250,50,None, 'black', 50, 'Start Server', screen) #creates the start server button
        self.buttons['Join Server'] = Button(300,400,250,50,None, 'black', 50, 'Join Server', screen) #creates the join server button
        self.buttons['AI'] = Button(300,500,250,50,None, 'black', 50, 'AI', screen) #creates the AI button
        self.buttons['Exit'] = Button(300,600,250,50,None, 'black', 50, 'Exit' , screen) #creates the exit button

        self.redirect_functions = {"Start Server": self.redirect_start_server, #creates a dictionary of the redirect functions
                                   "Join Server": self.redirect_join_server,
                                   "AI": self.redirect_ai,
                                   "Exit": self.redirect_exit,}
    
        self.settings = None



    def render(self): #renders the menu
        self.surface.blit(self.background, (0, 0)) #blits the background
        self.surface.blit(self.title, (300,0)) #blits the title
        for button in self.buttons.values(): #for each button in the buttons dictionary
            button.draw()  #draws the button
            button.process() #processes the button
            if button.clicked: #if the button is clicked
                self.redirect_functions[button.text]() #redirects to the function in the dictionary
        pygame.display.flip() #updates the display



    def redirect_start_server(self): #redirects to the start server function
        createGameMenu = CreateGameMenu(self.surface,self.width,self.height,self.screen) #creates the create game menu
        createGameMenu.run() #runs the create game menu
    

    def redirect_join_server(self): #redirects to the join server function
        joingamemenu = JoinGameMenu(self.surface, self.width, self.height, self.screen) #creates the join game menu
        joingamemenu.run() #runs the join game menu
 
    def redirect_ai(self): #redirects to the ai function
        chessmain1.main(host = 0, port = 0, create_or_join = 0, play_online=False, play_ai= True)   #runs the chess game with ai

    def redirect_exit(self): #redirects to the exit function
        pygame.quit() #quits pygame
        sys.exit() #exits the program


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


    

class CreateGameMenu(Menu):
    def __init__(self, surface, width , height, screen):
        super().__init__(surface, width, height, screen) #calls the super class
        self.screen = screen 
        self.buttons = {} #creates a dictionary of buttons
        self.buttons['Port'] = InputButton(300, 200, 250, 50, None, 'black', 30, 'Enter Port:', screen)     #creates the port button
        self.buttons['IP'] = InputButton(300, 400, 250, 50, None, 'black', 30, 'Enter IP:', screen) #creates the ip button
        self.buttons['Create Game'] = Button(300, 600, 250, 50, None, 'black', 30, 'Create Game', screen) #creates the create game button
        self.redirect_functions['Create Game'] = self.create_game() #creates a dictionary of the redirect functions
 

    def render(self): #renders the menu
        self.surface.blit(self.background, (0, 0))
        for button in self.buttons.values():
            button.draw()
            button.process()
            if button.clicked:
                self.create_game()
        pygame.display.flip()

    def create_game(self): #creates the game
        while self.buttons['Port'].input_value and self.buttons['IP'].input_value != '':
            port = self.buttons['Port'].input_value
            host = self.buttons['IP'].input_value
            create_or_join = 'c'
            chessmain1.main(host, port, create_or_join, play_online= True, play_ai= False)
        
            
    


    def run(self): #runs the menu
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.render()



class JoinGameMenu(Menu): #joingamemenu class
    def __init__(self, surface, width , height, screen):
        super().__init__(surface, width, height, screen) #calls the super class
        self.buttons = {}
        self.buttons['Port'] = InputButton(300, 200, 250, 50, None, 'black', 30, 'Enter Port:', screen) #creates the port button
        self.buttons['IP'] = InputButton(300, 400, 250, 50, None, 'black', 30, 'Enter IP:', screen) #creates the ip button
        self.buttons['Join Game'] = Button(300, 600, 250, 50, None, 'black', 30, 'Join Game', screen)   #creates the join game button
        self.redirect_functions['Join Game'] = self.join_game #creates a dictionary of the redirect functions
    
    def join_game(self): #joins the game
        port = self.buttons['Port'].input_value  #gets the port input
        host = self.buttons['IP'].input_value #gets the ip input
        create_or_join = 'j'
        chessmain1.main(host, port, create_or_join, play_online= True, play_ai= False)  

        




    def render(self): #renders the menu
        self.surface.blit(self.background, (0, 0))
        for button in self.buttons.values():
            button.draw()
            button.process()
            if button.clicked:
                self.join_game()
        pygame.display.flip()


    def run(self): #runs the menu
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.render()




