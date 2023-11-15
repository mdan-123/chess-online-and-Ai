import pygame
import Menu
import sys

pygame.init() #initialises pygame
pygame.mixer.init() #initialises pygame mixer
pygame.mixer.music.load('audio/song1.mp3') #loads the music, this is only for the menus and not the game
pygame.mixer.music.play(loops=-1) #plays the music


screen = pygame.display.set_mode((800, 800)) #sets the screen size
surface = pygame.display.get_surface()
menu = Menu.Menu(surface, 1200, 1200, screen)

#this is the main loop that runs the game
running = True #sets running to true
while running: #while running is true
    for event in pygame.event.get(): #gets all events
        if event.type == pygame.QUIT: #if the event is quit
            pygame.quit() #quits pygame
            sys.exit() #exits the program
    menu.render() #renders the menu





