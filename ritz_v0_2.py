"""
    Author: Justin Hellsten
    Date: August 3rd
    Last Modified By: Justin Hellsten
    Description: Tile based side scroller where the player controlls
                 a character called Ritz.
                 
    Version: 
        0.2 -> Fixed collision issues with tile and sprites
            -> removed physics class in sprite objects. 
            -> Falling state added. All sprites now fall
            -> Change tile textures, set to 16 size
            -> Added new sprite for ritz
            -> Added idle, moving, jumping, and falling images to ritz
            -> Added soundtrack for level one
            -> Ritz can now shoot bullets
            -> Now in full screen, escape terminates the program
            
"""
import pygame, gameEngine

""" Ritz Bullet Sprite """
class RitzBullet(gameEngine.MySprite):
    
    SPEED = 25
    
    def __init__(self, scene, facing, center):
        gameEngine.MySprite.__init__(self, scene, "ritzbullet.png")
        self.scene = scene
        self.facing = facing
        self.rect.center = center
        self.__setUp()
        
    def __setUp(self):
        if self.facing == self.FACE_LEFT:
            self.setDX(-self.SPEED)
        if self.facing == self.FACE_RIGHT:
            self.setDX(self.SPEED)
            
""" Our hero avatar sprite """
class Ritz(gameEngine.MySprite):
    IDLE_IMG_MAX = 4
    WALK_IMG_MAX = 4
    FALLING_IMG_MAX = 2
    JUMPING_IMG_MAX = 2
    
    WALK_SPEED = 5
    
    def __init__(self, scene):
        gameEngine.MySprite.__init__(self, scene, "ritz/idle0.png")

        self.idleImages = []
        self.walkImages = []
        self.jumpingImages = []
        self.fallingImages = []

        self.animationCounter = 0
        self.animationDelay = 0
        self.delayCounter = 0
        self.shooting = False
        
        self.__loadImages()
        
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

        if keys[pygame.K_w] and not self.jumping:
            self.jumping = True
            self.setDY(-15)
            
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

            

            

                
class GamePlayScene(gameEngine.Scene):
    def __init__(self, (width, height)):
        gameEngine.Scene.__init__(self, (width, height))
    
        #Load level one
        self.l1MapSprite = gameEngine.TileMap(self, "level1.dat")
        
        self.ritzSprite = Ritz(self)
        self.l1MapSprite.addSprite(self.ritzSprite)

        #Load music theme
        pygame.mixer.music.load("mfx/t1.ogg")
        pygame.mixer.music.play(-1)

        self.backgroundSprite = gameEngine.MySprite(self, "background.png")
        
        self.backgroundGroup = pygame.sprite.Group(self.backgroundSprite)
        self.l1MapSpriteGroup = pygame.sprite.Group(self.l1MapSprite)

        # Add level one sprites/groups
        self.addGroup(self.backgroundGroup)
        self.addGroup(self.l1MapSpriteGroup)
        
        
        self.currentLevel =  self.l1MapSprite
        
    def __checkKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.stop()
            
    def __handleMap(self):
        screenWidth = self.screen.get_width()
        screenHeight = self.screen.get_height()
        

        # Scroll map based on Ritz position
        self.currentLevel.setScrollPosition(self.ritzSprite.rect.x - screenWidth / 2, 
                                              self.ritzSprite.rect.y - screenHeight / 2)

    def __handleCollisions(self):
        #Handles the collisions between entities. Any collisions
        #with tiles are down in the tile map object.
        pass
    

    def doEvents(self, event):
        if event.type == pygame.KEYUP:
            if self.ritzSprite.shooting:
                self.l1MapSprite.addSprite(RitzBullet(self, self.ritzSprite.horizontalFacing,
                                                      self.ritzSprite.rect.center))
          
    def update(self):
        gameEngine.Scene.update(self)
        
        self.__checkKeys()
        self.__handleMap()
        self.__handleCollisions()
            
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
    
