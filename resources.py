'''
Created on Aug 8, 2013

@author: Justin Hellsten
'''

import pygame

DATA_DIRECTORY = "data/"
MFX_DIRECTORY = "mfx/"
SFX_DIRECOTRY = "sfx/"
GFX_DIRECTORY = "gfx/"

#Sound Constants
collectCoin = None
bulletCollision = None
ritzJump = None
ritzShoot = None

#Music Constants
MFX_SPLASHSCENE = MFX_DIRECTORY + "splash_scene_them.ogg"
MFX_INTRO_THEME = MFX_DIRECTORY + "intro_theme.ogg"
MFX_LEVEL_ONE_THEME = MFX_DIRECTORY + "t1.ogg"
MFX_GAME_OVER = MFX_DIRECTORY + "game_over.ogg"

#Graphic Constants
DOOR_IMAGE = None

#Text Constants
howToMoveCharacterText = ("Use A and D to ", "move your character")
howToShootText = ("Press SPACE bar ", "to shoot bullets")
howToJumpText = ("Press W to make ", "your character jump")
howToEnterDoorText = ("Press S when on ", "a door to enter")
PLAY_TEXT = ("Play", "")
EXIT_TEXT = ("Exit", "")
GAME_OVER_TEXT = ("Game Over", "")

def init():
    pygame.init()
    
    if pygame.mixer.get_init != None:  
        collectCoin = pygame.mixer.Sound("sfx/coin.ogg")
        bulletCollision = pygame.mixer.Sound("sfx/bullet_hit.ogg")
        ritzJump = pygame.mixer.Sound("sfx/ritz_jump.ogg")
        ritzShoot = pygame.mixer.Sound("sfx/ritz_bullet.ogg")

    DOOR_IMAGE = pygame.image.load("gfx/misc/door.png")
    
#Loads and plays a music theme
def playMusic(music = None, loops = -1, volume = 1.0):
    if music == None:
        pygame.mixer.music.set_volume(0)
    else:
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(loops)    
    
        