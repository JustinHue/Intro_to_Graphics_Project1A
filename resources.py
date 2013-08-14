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
mfxSplashScene = MFX_DIRECTORY + "splash_scene_them.ogg"
mfxStartScene = MFX_DIRECTORY + "intro_theme.ogg"
mfxDeathTheme = MFX_DIRECTORY + "death.ogg"

#Graphic Constants


def init():
    pygame.mixer.init()
    
    if pygame.mixer.get_init != None:  
        collectCoin = pygame.mixer.Sound("sfx/coin.ogg")
        bulletCollision = pygame.mixer.Sound("sfx/bullet_hit.ogg")
        ritzJump = pygame.mixer.Sound("sfx/ritz_jump.ogg")
        ritzShoot = pygame.mixer.Sound("sfx/ritz_bullet.ogg")

        
#Loads and plays a music theme
def playMusic(music, loops = -1):
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(loops)    
    
        