'''
Created on Aug 14, 2013

@author: justin
'''

import pygame, gameEngine, pygame.gfxdraw, resources

class Door(gameEngine.MyBasicSprite):
    def __init__(self, ritzMap, center):
        gameEngine.MyBasicSprite.__init__(self, center, pygame.image.load("gfx/misc/door.png"))
        self.ritzMap = ritzMap
        self.enter = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.ritzSprite = self.ritzMap.ritzSprite
        if pygame.rect.Rect.colliderect(self.rect, self.ritzSprite.rect) and keys[pygame.K_s]:
            self.enter = True

class LevelDoor(Door):
    def __init__(self, scene, ritzLevel, center):
        Door.__init__(self, ritzLevel, center)
        self.scene = scene
        
    def update(self):
        Door.update(self)
        if self.enter:
            self.scene.nextLevel()
        
class InstructionsDoor(Door):
    def __init__(self, scene, ritzMap, center):
        Door.__init__(self, ritzMap, center)
        self.scene = scene
        
    def update(self):
        Door.update(self)
        if self.enter:
            self.scene.stop()
            
class PlaySceneDoor(Door):
    def __init__(self, scene, ritzMap, center):
        Door.__init__(self, ritzMap, center)
        self.scene = scene
        
    def update(self):
        Door.update(self)
        if self.enter:
            self.scene.stop()
             
class ExitSceneDoor(Door):
    def __init__(self, scene, ritzMap, center):
        Door.__init__(self, ritzMap, center)
        self.scene = scene
        
    def update(self):
        Door.update(self)
        if self.enter:
            self.scene.terminate()
                         

class Coin(gameEngine.MySprite):
    IDLE_IMG_MAX = 8
    POINTS = 25
    def __init__(self, scene, ritzTileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "misc/coin0.png")
        self.idleImages = []
        self.ritzTileMap = ritzTileMap
        
        self.animationCounter = 0
        self.animationDelay = 1
        self.delayCounter = 0
        self.center = center
        self.applyPhysics = False
        
        self.__loadImages()
        self.__loadSounds()
        
    def __loadImages(self):
        # Add idle images
        for i in range(self.IDLE_IMG_MAX):
            self.idleImages.append(pygame.image.load("gfx/misc/coin{0}.png".format(i)))

    def __loadSounds(self):
        self.sndCoin = pygame.mixer.Sound("sfx/coin.ogg")
        
    def __handleAnimation(self):
        if self.delayCounter < self.animationDelay:
            self.delayCounter += 1
        else:
            maxImg = 0
            animationImages = []
            self.delayCounter = 0
            
            if self.idle:
                maxImg = self.IDLE_IMG_MAX
                animationImages = self.idleImages
            else:
                #Use idle as default if none of these attributes are set.
                #Just in case, you should also have one of these flags set.
                maxImg = self.IDLE_IMG_MAX
                animationImages = self.idleImages
                
            if self.animationCounter >=  maxImg:
                self.animationCounter = 0
                self.masterImage = animationImages[maxImg - 1]
            else:
                self.masterImage = animationImages[self.animationCounter]
                self.animationCounter += 1
   
            self.image = self.masterImage
            self.rect = self.image.get_rect()
            self.rect.center = self.orginalCenter
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__handleAnimation()
        

class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.score = 0
        self.center = center
        self.image = pygame.surface.Surface((500, 50), pygame.SRCALPHA)
        
        self.__renderImage()

    def __renderImage(self):
        self.font = pygame.font.SysFont("None", 32)
        self.image = self.font.render("Score: {0}".format(self.score), 1, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        
    def addScore(self, score):
        self.score += score
        self.__renderImage()
        
    def getScore(self):
        return self.score
    
        
    def doEvents(self, event):
        pass

    
""" Life Counter"""
#Displays the number of lives the user currently has.
#If the number of lives decreases to zero than the alive
#flag is false. The life counter with an image of ritz times
#the number of lives
class LifeCounter(pygame.sprite.Sprite):
    NUM_OF_LIVES = 3
    def __init__(self, scene, center, ritzSprite):
        pygame.sprite.Sprite.__init__(self)
        self.ritzSprite = ritzSprite
        self.lives = self.NUM_OF_LIVES
        self.center = center
        self.scene = scene
        self.ritzImage = pygame.image.load("gfx/ritz/idle0.png")

        self.__renderImage()
        
    def __renderImage(self):
        self.image = pygame.surface.Surface((self.lives * self.ritzImage.get_width(), 50), pygame.SRCALPHA)
        for life in range(self.lives):
            self.image.blit(self.ritzImage, (life * self.ritzImage.get_width(), 0))
        
        self.rect = self.image.get_rect()
        self.rect.center = self.center

        
    def removeLife(self):
        self.lives -= 1
        if self.lives <= 0:
            self.scene.stop()
        else:
            self.__renderImage()
        
    def doEvents(self, event):
        pass
    
class GraveStone(gameEngine.MyBasicSprite):
    FONT_NAME = None
    FONT_SIZE = 12
    FONT_WEIGHT = True
    FONT_ITALIC = False
    FONT_COLOR = (25, 25, 25)   
    def __init__(self, center):
        gameEngine.MyBasicSprite.__init__(self, center, pygame.image.load("gfx/misc/gravestone.png"))
        """
            Render font
        """
        self.font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE, self.FONT_WEIGHT, self.FONT_ITALIC)
        self.fontImage = self.font.render("RIP", True, self.FONT_COLOR)
        fontSize = self.font.size("RIP")
        self.image.blit(self.fontImage, (self.rect.width / 2 - fontSize[0] / 2, 
                                         self.rect.height / 2 - fontSize[1] / 2))
        
        
class ButtonSprite(gameEngine.MyBasicSprite):
    FILL_COLOR = (25,25,25)
    BORDER_COLOR = (255,255,255)
    FONT_NAME = None
    FONT_SIZE = 16
    FONT_WEIGHT = True
    FONT_ITALIC = False
    FONT_COLOR = (255, 255, 255)    
    def __init__(self, center, (width, height), text):
        gameEngine.MyBasicSprite.__init__(self, center, pygame.surface.Surface((width, height), pygame.SRCALPHA))
        self.image.fill(self.FILL_COLOR)
        """
            Render border
        """
        pygame.gfxdraw.hline(self.image, 0, self.rect.width, 0, self.BORDER_COLOR)
        pygame.gfxdraw.hline(self.image, 0, self.rect.width, self.rect.height - 1, self.BORDER_COLOR)
        pygame.gfxdraw.vline(self.image, 0, 0, self.rect.height, self.BORDER_COLOR)
        pygame.gfxdraw.vline(self.image, self.rect.width - 1, 0, self.rect.height, self.BORDER_COLOR)
                    
        """
            Render font
        """
        self.font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE, self.FONT_WEIGHT, self.FONT_ITALIC)
        self.fontImage = self.font.render(text, True, self.FONT_COLOR)
        fontSize = self.font.size(text)
        self.image.blit(self.fontImage, (self.rect.width / 2 - fontSize[0] / 2, 
                                         self.rect.height / 2 - fontSize[1] / 2))
        
        
        
class RectangleButtonSprite(ButtonSprite):
    def __init__(self, center, (width, height), text):
        ButtonSprite.__init__(self, center, (width, height), text)
    
class SquareButtonSprite(ButtonSprite):
    def __init__(self, center, text, size = 25):
        ButtonSprite.__init__(self, center, (size, size), text)
 
