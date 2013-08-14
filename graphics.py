'''
Created on Aug 14, 2013

@author: justin
'''

import pygame, gameEngine, random, math

class BloodSplatter():
    def __init__(self, scene, number, center):
        bloodCount = 0
        self.bloods = []
        while bloodCount < number:       
            self.bloods.append(Blood(scene, center))     
            bloodCount += 1

    def getBloodGroup(self):
        bloodGroup = pygame.sprite.Group()
        for blood in self.bloods:
            bloodGroup.add(blood)
        return bloodGroup
    
class Blood(gameEngine.MySprite):
    KILL_DELAY_MIN = 200
    KILL_DELAY_MAX = 350
    SPEED_MAX = 15
    def __init__(self, scene, center):
        gameEngine.MySprite.__init__(self, scene, center, "")
        self.image = pygame.surface.Surface((2,2))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.killDelay = random.randint(self.KILL_DELAY_MIN, self.KILL_DELAY_MAX)
        self.killCounter = 0
        self.dir = random.randint(0, 360)
        self.speed = random.random() * self.SPEED_MAX
        
        theta = self.dir / 180.0 * math.pi
        self.dx = math.cos(theta) * self.speed
        self.dy = math.sin(theta) * self.speed
                
    def __AI(self):
        if self.killCounter == self.killDelay:
            self.kill()
            self.killCounter = 0
        else:
            self.killCounter += 1
        
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        
