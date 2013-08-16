'''
Created on Aug 14, 2013

@author: justin
'''

import pygame, gameEngine, random, graphics


class ShyGuy(gameEngine.MySprite):
    
    IDLE_IMG_MAX = 3
    WALK_IMG_MAX = 3
    
    WALK_SPEED = 3
    JUMP_SPEED = -8
    
    MIN_IDLE_DELAY = 300
    MAX_IDLE_DELAY = 400
    IDLE_WAIT = 80
    HEALTH_MAX = 50
    
    def __init__(self, scene, ritzTileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "enemies/shyguy_idle0.png")        
        
        self.idleImages = []
        self.walkImages = []
        self.ritzTileMap = ritzTileMap
        
        self.animationCounter = 0
        self.animationDelay = 1
        self.delayCounter = 0
        self.health = self.HEALTH_MAX
        self.jump = False
        self.onGround = False
        self.falling = False
        
        self.__resetIdle()
        self.__loadImages()
        self.__setUp()
        
    def __loadImages(self):
        # Add idle images
        for i in range(self.IDLE_IMG_MAX):
            self.idleImages.append(pygame.image.load("gfx/enemies/shyguy_idle{0}.png".format(i)))
        
        # Add Walk images
        for i in range(self.WALK_IMG_MAX):
            self.walkImages.append(pygame.image.load("gfx/enemies/shyguy_walk{0}.png".format(i)))

    def __resetIdle(self):
        self.idleCounter = 0
        self.idleWaitCounter = 0
        self.originalDX = 0
        self.idleDelay = random.randint(self.MIN_IDLE_DELAY, self.MAX_IDLE_DELAY)
        
    def __setUp(self):
        randomMovement = random.randint(0, 1)
        if randomMovement == 0:
            randomMovement = -1

        self.setDX(randomMovement * self.WALK_SPEED)
        
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
            elif self.walking:
                maxImg = self.WALK_IMG_MAX
                animationImages = self.walkImages
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
            
    def __handleOrientation(self):
        #Set to the correct facing
        if self.horizontalFacing == self.FACE_LEFT:
            self.hflip()  
            
    def __AI(self):
        #The AI for shyguy is they move back and forth. They will
        #fall into pits. After a certain random delay they will stop
        #and stay idle.
        
        if self.falling:
            self.onGround = False
        else:
            self.onGround = True
            
        #Prepare to be idle
        if self.idleCounter == self.idleDelay:
            self.idleWaitCounter += 1
            if self.idleWaitCounter == self.IDLE_WAIT:
                self.idle = False
                self.walk = True
                self.setDX(self.originalDX)
                self.__resetIdle()
            elif not self.idle:
                self.idle = True
                self.originalDX = self.dx
                self.setDX(0)
        else:
            self.idleCounter += 1

            
        #If shyguy hits a wall (left or right) reverse direction
        if self.wallCollision == self.COLLIDE_LEFT:
            self.setDX(self.WALK_SPEED)
        elif self.wallCollision == self.COLLIDE_RIGHT:
            self.setDX(-self.WALK_SPEED)
            
        #If shyguy hits tile (left or right) reverse direction
        for direction in self.collisionDirs:
            if direction == self.COLLIDE_RIGHT:
                self.setDX(self.WALK_SPEED)
            elif direction == self.COLLIDE_LEFT:
                self.setDX(-self.WALK_SPEED)
                
        #Kill Ritz on collison
        if self.ritzTileMap.ritzSprite != None:
            if self.collidesWith(self.ritzTileMap.ritzSprite.rect):
                self.ritzTileMap.ritzSprite.isDead = True
            
        #Make shy guy jump if there is a tile infront
        if self.horizontalFacing == self.FACE_LEFT:
            adjacentDir = -2
            self.setDX(-self.WALK_SPEED)
        elif self.horizontalFacing == self.FACE_RIGHT:
            adjacentDir = 2
            self.setDX(self.WALK_SPEED)
    
        #Get tile index of shy guy
        (ixPosition, iyPosition) = self.ritzTileMap.getIndexAt(self.rect.centerx, self.rect.centery)
        adjacentTile = self.ritzTileMap.getTileAt(ixPosition + adjacentDir, iyPosition)
        checkAdjacentTile = self.ritzTileMap.isTileCollidable(adjacentTile)
        
        if checkAdjacentTile:
            self.jump = True
            
        if self.jump and self.onGround:
            self.setDY(self.JUMP_SPEED)
            self.jump = False
            self.onGround = False
        
    def deductHealth(self, amt):
        self.health -= amt
        if self.health <= 0:
            self.die()
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        self.__handleAnimation()
        self.__handleOrientation()
        
    def die(self):
        bloodSplatter = graphics.BloodSplatter(self.scene, 50, self.rect.center)
        self.ritzTileMap.addGroup(bloodSplatter.getBloodGroup())
        self.kill()
        
class Goomba(gameEngine.MySprite):
    
    IDLE_IMG_MAX = 3
    WALK_IMG_MAX = 3
    
    WALK_SPEED = 4
    
    MIN_IDLE_DELAY = 60
    MAX_IDLE_DELAY = 120
    IDLE_WAIT = 80
    HEALTH_MAX = 30
    
    def __init__(self, scene, ritzTileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "enemies/goomba_idle0.png")        
        
        self.idleImages = []
        self.walkImages = []
        self.ritzTileMap = ritzTileMap
        
        self.animationCounter = 0
        self.animationDelay = 1
        self.delayCounter = 0
        self.health = self.HEALTH_MAX
        
        self.__resetIdle()
        self.__loadImages()
        self.__setUp()
        
    def __loadImages(self):
        # Add idle images
        for i in range(self.IDLE_IMG_MAX):
            self.idleImages.append(pygame.image.load("gfx/enemies/goomba_idle{0}.png".format(i)))
        
        # Add Walk images
        for i in range(self.WALK_IMG_MAX):
            self.walkImages.append(pygame.image.load("gfx/enemies/goomba_walk{0}.png".format(i)))

    def __resetIdle(self):
        self.idleCounter = 0
        self.idleWaitCounter = 0
        self.originalDX = 0
        self.idleDelay = random.randint(self.MIN_IDLE_DELAY, self.MAX_IDLE_DELAY)
        
    def __setUp(self):
        randomMovement = random.randint(0, 1)
        if randomMovement == 0:
            randomMovement = -1

        self.setDX(randomMovement * self.WALK_SPEED)
        
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
            elif self.walking:
                maxImg = self.WALK_IMG_MAX
                animationImages = self.walkImages
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
            
    def __handleOrientation(self):
        #Set to the correct facing
        if self.horizontalFacing == self.FACE_LEFT:
            self.hflip()  
            self.setDX(-self.WALK_SPEED)
        else:
            self.setDX(self.WALK_SPEED)
            
    def __AI(self):
        #The AI for goombas is they move back and forth. They will
        #fall into pits. After a certain random delay they will stop
        #and stay idle.
        
        #If goomba hits tile (left or right) reverse direction
        for direction in self.collisionDirs:
            if direction == self.COLLIDE_RIGHT:
                self.setDX(self.WALK_SPEED)
            elif direction == self.COLLIDE_LEFT:
                self.setDX(-self.WALK_SPEED)
                  
        """      
        #Prepare to be idle
        if self.idleCounter == self.idleDelay:
            self.idleWaitCounter += 1
            if self.idleWaitCounter == self.IDLE_WAIT:
                self.idle = False
                self.walk = True
                self.setDX(self.originalDX)
                self.__resetIdle()
            elif not self.idle:
                self.idle = True
                self.originalDX = self.dx
                self.setDX(0)
        else:
            self.idleCounter += 1
        """
        
        #If goomba hits a wall (left or right) reverse direction
        if self.wallCollision == self.COLLIDE_LEFT:
            self.setDX(self.WALK_SPEED)
        elif self.wallCollision == self.COLLIDE_RIGHT:
            self.setDX(-self.WALK_SPEED)
            

                
        #Kill Ritz on collison
        if self.ritzTileMap.ritzSprite.alive():
            if self.collidesWith(self.ritzTileMap.ritzSprite.rect):
                self.ritzTileMap.ritzSprite.die()
                
                
    def deductHealth(self, amt):
        self.health -= amt
        if self.health <= 0:
            self.die()
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        self.__handleAnimation()
        self.__handleOrientation()
        
    def die(self):
        bloodSplatter = graphics.BloodSplatter(self.scene, 50, self.rect.center)
        self.ritzTileMap.addGroup(bloodSplatter.getBloodGroup())
        self.kill()
                