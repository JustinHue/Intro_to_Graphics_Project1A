"""
    Author: Justin Hellsten
    Date: August 3rd
    Last Modified By: Justin Hellsten
    Description: Tile based side scroller where the player controlls
                 a character called Ritz.
                 
    Version: 
        0.4 
            -> Added sound effect for ritz bullet shot
            -> Added sound effect for ritz jump
            -> Add enemy locations in data file, and enemy type
            -> Added gomba enemies
            -> TileMap now a based class. Level one now
               derives from LevelOne class
            -> goomba AI goes back and forth. Will reverse direction when hitting wall or tile. Randomly
               goes either direction when created.
               
            
"""
import pygame, gameEngine, random

"""Enemy Sprites """
class Goomba(gameEngine.MySprite):
    
    IDLE_IMG_MAX = 3
    WALK_IMG_MAX = 3
    
    WALK_SPEED = 4
    
    def __init__(self, scene, center):
        gameEngine.MySprite.__init__(self, scene, "enemies/goomba_idle0.png")
        self.idleImages = []
        self.walkImages = []

        self.animationCounter = 0
        self.animationDelay = 1
        self.delayCounter = 0
        self.rect.center = center
        
        self.__loadImages()
        self.__setUp()
        
    def __loadImages(self):
        # Add idle images
        for i in range(self.IDLE_IMG_MAX):
            self.idleImages.append(pygame.image.load("gfx/enemies/goomba_idle{0}.png".format(i)))
        
        # Add Walk images
        for i in range(self.WALK_IMG_MAX):
            self.walkImages.append(pygame.image.load("gfx/enemies/goomba_walk{0}.png".format(i)))

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

                
            if self.animationCounter >=  maxImg:
                self.animationCounter = 0
                self.masterImage = animationImages[maxImg - 1]
            else:
                self.masterImage = animationImages[self.animationCounter]
                self.animationCounter += 1
   
            self.image = self.masterImage
            
    def __AI(self):
        #The AI for goombas is they move back and forth. They will not
        #fall in pits
        if self.horizontalFacing == self.FACE_LEFT:
            self.hflip()  
 
        #If goomba hits a wall (left or right) reverse direction
        if self.wallCollision == self.COLLIDE_LEFT:
            self.setDX(self.WALK_SPEED)
        elif self.wallCollision == self.COLLIDE_RIGHT:
            self.setDX(-self.WALK_SPEED)
            
        #If goomba hits tile (left or right) reverse direction
        for direction in self.collisionDirs:
            if direction == self.COLLIDE_RIGHT:
                self.setDX(self.WALK_SPEED)
            elif direction == self.COLLIDE_LEFT:
                self.setDX(-self.WALK_SPEED)
                
    def update(self):
        gameEngine.MySprite.update(self)
        self.__handleAnimation()
        self.__AI()
        
""" Ritz Bullet Sprite """
class RitzBullet(gameEngine.MySprite):
    
    SPEED = 25
    FADE_DELAY = 250
    
    def __init__(self, scene, facing, center):
        gameEngine.MySprite.__init__(self, scene, "ritzbullet.png")
        self.scene = scene
        self.facing = facing
        self.fadeCounter = 0
        self.rect.center = center
        self.__setUp()
        
    def __setUp(self):
        if self.facing == self.FACE_LEFT:
            self.setDX(-self.SPEED)
        if self.facing == self.FACE_RIGHT:
            self.setDX(self.SPEED)
        
    def __checkFadeStatus(self):
        if self.fadeCounter < self.FADE_DELAY:
            self.fadeCounter += 1
        else:
            self.kill()
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__checkFadeStatus()
        
""" Our hero avatar sprite """
class Ritz(gameEngine.MySprite):
    IDLE_IMG_MAX = 4
    WALK_IMG_MAX = 4
    FALLING_IMG_MAX = 2
    JUMPING_IMG_MAX = 2
    
    WALK_SPEED = 5
    JUMP_SPEED = -15
    
    def __init__(self, scene, center):
        gameEngine.MySprite.__init__(self, scene, "ritz/idle0.png")

        self.idleImages = []
        self.walkImages = []
        self.jumpingImages = []
        self.fallingImages = []

        self.animationCounter = 0
        self.animationDelay = 0
        self.delayCounter = 0
        self.shooting = False
        self.onGround = False
        self.rect.center = center
        
        self.__loadImages()
        self.__loadSounds()
        
    def __loadImages(self):
        # Add idle images
        for i in range(self.IDLE_IMG_MAX):
            self.idleImages.append(pygame.image.load("gfx/ritz/idle{0}.png".format(i)))
        
        # Add Walk images
        for i in range(self.WALK_IMG_MAX):
            self.walkImages.append(pygame.image.load("gfx/ritz/walk{0}.png".format(i)))
        
        # Add Falling images
        for i in range(self.FALLING_IMG_MAX):
            self.fallingImages.append(pygame.image.load("gfx/ritz/falling{0}.png".format(i)))
               
        # Add Jumping images
        for i in range(self.JUMPING_IMG_MAX):
            self.jumpingImages.append(pygame.image.load("gfx/ritz/jumping{0}.png".format(i)))
               
    def __loadSounds(self):
        self.sndJump = pygame.mixer.Sound("sfx/ritz_jump.ogg")
        self.sndShoot = pygame.mixer.Sound("sfx/ritz_bullet.ogg")
        
    def __handleAnimation(self):
        if self.delayCounter < self.animationDelay:
            self.delayCounter += 1
        else:
            maxImg = 0
            animationImages = []
            self.delayCounter = 0
            
            if self.jumping:
                maxImg = self.JUMPING_IMG_MAX
                animationImages = self.jumpingImages            
            elif self.falling:
                maxImg = self.FALLING_IMG_MAX
                animationImages = self.fallingImages
            elif self.idle:
                maxImg = self.IDLE_IMG_MAX
                animationImages = self.idleImages
            elif self.walking:
                maxImg = self.WALK_IMG_MAX
                animationImages = self.walkImages

                
            if self.animationCounter >=  maxImg:
                self.animationCounter = 0
                self.masterImage = animationImages[maxImg - 1]
            else:
                self.masterImage = animationImages[self.animationCounter]
                self.animationCounter += 1
   
            self.image = self.masterImage
            
            
    def __handleFalling(self):
        keys = pygame.key.get_pressed()

        if self.falling:
            self.onGround = False
        else:
            self.onGround = True
            
        if keys[pygame.K_w] and self.onGround:
            self.setDY(self.JUMP_SPEED)
            self.sndJump.play()
            
    def __handleShooting(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE]:
            self.shooting = True
        else:
            self.shooting = False
            
    def __handleWalking(self):
        keys = pygame.key.get_pressed()
        self.setDX(0)
        
        if keys[pygame.K_a]:
            self.setDX(-self.WALK_SPEED)
        if keys[pygame.K_d]: 
            self.setDX(self.WALK_SPEED)

        if self.horizontalFacing == self.FACE_LEFT:
            self.hflip()  
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__handleAnimation()
        self.__handleFalling()
        self.__handleWalking()
        self.__handleShooting()
        
            

            

""" Level Classes """
class LevelOne(gameEngine.TileMap):
    def __init(self, scene, datafile): 
        gameEngine.TileMap.__init__(self, scene, datafile)
        
    def init(self):
        gameEngine.TileMap.init(self)
        self.playDeathTheme = False 
        
        #Set map boundary detections
        self.setBoundary(True, True, True, False)
        
        #Create Ritz Sprite
        self.ritzSprite = Ritz(self.scene, (self.startx, self.starty))
        
        #Create enemy Sprites
        for data in self.enemyData:
            if data[0] == 'goomba':
                self.addSprite(Goomba(self.scene, (data[1], data[2])))
            
        #Add sprites to the map
        self.addSprite(self.ritzSprite)

        #Load music theme
        pygame.mixer.music.load("mfx/t1.ogg")
        pygame.mixer.music.play(-1)
        
    
    def __handleDeaths(self):
        #Check if ritz is dead
        if not self.ritzSprite.alive() and not self.playDeathTheme:
            self.playDeathTheme = True
            pygame.mixer.music.load("mfx/death.ogg")
            pygame.mixer.music.play()
            
    def update(self):
        #Update tile map. Call base class update function and
        #proceed with own update code. 
        gameEngine.TileMap.update(self)
        self.__handleDeaths()
        
        screenWidth = self.screen.get_width()
        screenHeight = self.screen.get_height()
                
        #Bound Scroll position to Ritz
        self.setScrollPosition(self.ritzSprite.rect.x - screenWidth / 2, 
                               self.ritzSprite.rect.y - screenHeight / 2)
        
    def doEvents(self, event):
        if event.type == pygame.KEYUP:
            if self.ritzSprite.shooting:
                self.addSprite(RitzBullet(self.scene, self.ritzSprite.horizontalFacing,
                                          self.ritzSprite.rect.center))
                self.ritzSprite.sndShoot.play()
                
class GamePlayScene(gameEngine.Scene):
    def __init__(self, (width, height)):
        gameEngine.Scene.__init__(self, (width, height))
        self.playDeathTheme = False
        self.physics = gameEngine.Physics()
                
        #Load level one
        self.levelOne = LevelOne(self, "level1.dat")

        self.backgroundSprite = gameEngine.MySprite(self, "background.png")
        
        self.backgroundGroup = pygame.sprite.Group(self.backgroundSprite)
        self.l1MapSpriteGroup = pygame.sprite.Group(self.levelOne)

        # Add level one sprites/groups
        self.addGroup(self.backgroundGroup)
        self.addGroup(self.l1MapSpriteGroup)
        
        
        self.currentLevel =  self.levelOne
        
    def __checkKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.stop()

    
    def doEvents(self, event):
        self.levelOne.doEvents(event)
        
    def update(self):
        gameEngine.Scene.update(self)
        
        self.__checkKeys()

        
class GameEndScene(gameEngine.Scene):
    def __init__(self, (width, height)):
        gameEngine.Scene.__init__(self, (width, height))
        
    def update(self):
        gameEngine.Scene.update(self)
    
    
    
class StartScene(gameEngine.Scene):
    def __init__(self, (width, height)):
        gameEngine.Scene.__init__(self, (width, height))
        
    def update(self):
        gameEngine.Scene.update(self)
        
    def doEvents(self, event):
        if event.type == pygame.KEYDOWN:
            self.stop()

                
def main():
    startScene = StartScene((800, 600))
    startScene.setCaption("Bouncer by Justin Hellsten - Start Scene")
    startScene.start()
    gamePlayScene = GamePlayScene((800, 600))
    gamePlayScene.setCaption("Bouncer by Justin Hellsten - Play Scene")
    gamePlayScene.start()
    
if __name__ == "__main__": main()
    
