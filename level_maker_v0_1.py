'''
Created on Aug 11, 2013

@author: Justin Hellsten
'''


import pygame

pygame.init()

def __checkInput():
    keys = pygame.key.get_pressed()
    
def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Level Maker - Ritz")
    background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    screen.blit(background, (0, 0))
    keepGoing = True
    clock = pygame.time.Clock()
    
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
        

                
            pygame.display.flip()
    
if __name__ == "__main__": main()

