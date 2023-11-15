import pygame

objects = [] #list of all objects
input = [] #list of all input objects
class Button(): #button class
    def __init__(self, x, y, width, height, font, font_colour, font_size, text, screen):  
        self.x = x #sets the x variable to the x variable
        self.y = y #sets the y variable to the y variable
        self.width = width #sets the width variable to the width variable
        self.height = height #sets the height variable to the height variable
        self.clicked = False #sets the clicked variable to false
        self.font_size = font_size 
        self.font = pygame.font.Font(font, self.font_size)
        self.font_colour = pygame.Color(font_colour) 
        self.text = text
        self.screen = screen
        self.text_size = font_size
        self.buttonsurface = pygame.Surface((self.width, self.height))
        self.buttonrect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.buttonsurf = self.font.render(text, True, self.font_colour)
        objects.append(self)
        self.colours_for_button = self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }


    def process(self): #processes the button
        pos_of_mouse = pygame.mouse.get_pos() #gets the position of the mouse
        self.buttonsurface.fill(self.colours_for_button['normal']) #fills the button with the normal colour
        if self.buttonrect.collidepoint(pos_of_mouse): #if the mouse is over the button
            self.buttonsurface.fill(self.colours_for_button['hover']) #fills the button with the hover colour
            if pygame.mouse.get_pressed()[0]: #if the mouse is pressed
                self.buttonsurface.fill(self.colours_for_button['pressed']) #fills the button with the pressed colour
                self.clicked = True #sets the clicked variable to true
        self.render_text() #renders the text
        return None #returns none


    def render_text(self): #renders the text
        self.buttonsurface.blit(self.buttonsurf,[
            self.buttonrect.width/2 - self.buttonsurf.get_rect().width/2,
            self.buttonrect.height/2 - self.buttonsurf.get_rect().height/2]) #renders the text in the middle of the button
        self.screen.blit(self.buttonsurface, self.buttonrect) #blits the button to the screen


    def draw(self): #draws the button
        pygame.draw.rect(self.buttonsurface, (255,0,0), self.buttonrect) #draws the button
        if self.text != 0: #if the text is not 0
            self.render_text() #renders the text


class InputButton(Button): #input button class
    def __init__(self, x, y, width, height, font, font_colour, font_size, text, screen): #initialises the input button
        super().__init__(x, y, width, height, font, font_colour, font_size, text, screen) #calls the super class
        self.input_value = "" #sets the input value to nothing
        self.clicked = False #sets the clicked variable to false
        input.append(self) #adds the input button to the input list

    def process(self): #processes the input button
        mouse_pos = pygame.mouse.get_pos() #gets the position of the mouse
        self.buttonsurface.fill(self.colours_for_button['normal']) #fills the button with the normal colour
        if self.buttonrect.collidepoint(mouse_pos): #if the mouse is over the button
            self.buttonsurface.fill(self.colours_for_button['hover']) #fills the button with the hover colour
            if pygame.mouse.get_pressed()[0]: #if the mouse is pressed
                self.buttonsurface.fill(self.colours_for_button['pressed']) #fills the button with the pressed colour
                self.clicked = True #sets the clicked variable to true
                self.get_input() #gets the input
        self.render_text() #renders the text
        self.rendertext_abovebox() #renders the text above the box
        return self.input_value #returns the input value

    def get_input(self): #gets the input
        while self.clicked: #while the button is clicked
            mouse_pos = pygame.mouse.get_pos() #gets the position of the mouse
            for event in pygame.event.get(): #gets all the events
                if event.type==pygame.KEYDOWN: #if a key is pressed
                    if event.key == pygame.K_BACKSPACE: #if the key is backspace
                        self.input_value = self.input_value[:-1] #removes the last character
                    else:  #if the key is not backspace meaning the key is a letter
                        self.input_value += event.unicode #adds the letter to the input value
                elif not self.buttonrect.collidepoint(mouse_pos): #if mouse is not on button
                    if pygame.mouse.get_pressed()[0]: #if mouse is pressed
                        self.clicked = False #sets the clicked variable to false


    def draw(self): #draws the input button
        pygame.draw.rect(self.buttonsurface, (255,0,0), self.buttonrect) #draws the button
        self.rendertext_abovebox() #renders the text above the box
        self.render_text() #renders the text
         


    def rendertext_abovebox(self): #renders the text above the box
        _text = self.text   
        self.textsurface = self.font.render(_text, True, (255,255,255))     
        self.text_rect = pygame.Rect(self.x, self.y-100, self.width, self.height)   
        self.textsurface.blit(self.textsurface,[self.x, self.y - 100])
        self.screen.blit(self.textsurface, self.text_rect)

          

    def render_text(self): #renders the text
        _text = f"{self.input_value}"
        self.buttonsurf = self.font.render(_text, True, self.font_colour)
        self.buttonsurface.blit(self.buttonsurf,[ 
            self.buttonrect.width/2 - self.buttonsurf.get_rect().width/2,
            self.buttonrect.height/2 - self.buttonsurf.get_rect().height/2])
        self.screen.blit(self.buttonsurface, self.buttonrect)
        if self.clicked: #if the button is clicked
            pygame.display.update() #updates the display
            pygame.display.flip() #flips the display
       


