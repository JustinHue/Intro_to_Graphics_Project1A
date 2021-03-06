"""
    Author's name: Justin Hellsten
    Last Modified by: Justin Hellsten
    Date last Modified: Sun, August 11
    Program description:
                 Tile based side scroller where the player controlls a character called Ritz.
                 Collect coins and shoot various enemies in a platform tile side scroller.
                 
    Revision History: 0.9.0

        -> Added blood sprite.
        -> Blood goes everywhere when ritz dies
        -> Fixed issue on last life where death animation does not happen
        -> Added spike tile
        -> Player will die when colliding with spike tile
        -> Goombas no longer go idle
        -> ENemies now explode on death
        -> Enemies can now die from spikes
        -> Blood now dissappears faster
        -> Fixed issue where tile map does not render bottom and right most portions
        -> Fixed issue where ritz does not die if he falls out of bounds
        -> Added StartSceneMap class. This will be the background for the start scene
        -> Start scene is made out of tiles now, including the title "Ritz"
        -> Added ritz tile map base class for all tile maps to reduce code load.
        -> Added do events to my sprite object
        -> Reduce ritz jump speed
        -> Changing tile map object so entities are not bound to the map ***
        -> Making ritz level loader object
        -> Removed file loading for tile map object in game engine. (game engine util no longer required)
            Keep it for now so we don't crash anything.
        -> Created blood splatter object to hold blood objects in one package
        -> New modules: enemies, miscellaneous, graphics
        -> Fixed issue where blood splatter wasn't working anymore after puting it in graphics module
        -> Fixed blood splatter effect where it used to create square splatters. It should now
           be a circle blood splatter
        -> Change tile collision on the top so that delta x becomes 0. This makes the blood splatter look better.
           However this screws up the enemies AI. Enemy AI now must apply a new speed every update.
        -> Removed empty area around scene tile map to enclose the player into one screen
        -> Added instructions scene (after splash and before start scene)
"""
import pygame, gameEngine, random
import graphics
import resources

""" Scene Constants """
SCENE_SPLASH = 0
SCENE_INSTRUCTIONS = 1
SCENE_START = 2
SCENE_PLAY = 3
SCENE_END = 4


class RitzLevelLoader():
    MAP_TOKENS = '[tokens]'
    MAP_SIZE = '[size]'
    MAP_IMG = '[imgs]'
    MAP_IMGDIR = '[imgdir]'
    MAP_STARTLOCATION = '[startlocation]'
    MAP_ENTITIES = '[entities]'
    MAP_SECTIONS = [MAP_TOKENS, MAP_SIZE, MAP_IMG, MAP_IMGDIR, MAP_STARTLOCATION, MAP_ENTITIES]
    def __init__(self, datafile):
        f = open(resources.DATA_DIRECTORY + datafile)
        self.data = {'[tokens]':[], '[size]':0, '[imgs]':[], '[imgdir]':'', '[startlocation]':(0,0), '[entities]':[(0,0,0)]} 
        reading = ""
        
        for line in f.readlines():
            line = line.strip()
        
            for section in self.MAP_SECTIONS:
                if line == section: 
                    reading = line 
            if reading == line:
                continue
            
            if reading == self.MAP_TOKENS:
                tokens = line.split(',')
                self.data[self.MAP_TOKENS].append([])      
                for token in tokens:       
                    self.data[self.MAP_TOKENS][len(self.data[self.MAP_TOKENS])-1].append(int(token))            
            elif reading == self.MAP_SIZE:
                self.data[self.MAP_SIZE] = int(line)
            elif reading == self.MAP_IMG:
                self.data[self.MAP_IMG].append(line)
            elif reading == self.MAP_IMGDIR:
                self.data[self.MAP_IMGDIR] = line
            elif reading == self.MAP_STARTLOCATION:
                tokens = line.split(',')
                self.data[self.MAP_STARTLOCATION] = (int(tokens[0]), int(tokens[1]))
            elif reading == self.MAP_ENTITIES:
                tokens = line.split(',')
                self.data[self.MAP_ENTITIES].append([tokens[0], int(tokens[1]), int(tokens[2])])
                
        f.close()
        
    def getTokens(self):
        return self.data[self.MAP_TOKENS]
    
    def getTileSize(self):
        return self.data[self.MAP_SIZE]
    
    def getTileDirectory(self):
        return resources.GFX_DIRECTORY + self.data[self.MAP_IMGDIR]
    
    def getTileImages(self):
        return self.data[self.MAP_IMG]
    
    def getStartLocation(self):
        return self.data[self.MAP_STARTLOCATION]
    
    def getEntityInfo(self):
        return self.data[self.MAP_ENTITIES]
    
    
class RitzTileMap(gameEngine.TileMap):
    DEATH_DELAY = 120
    TRANPARENT_TILE = 0
    SPIKE_TILE = 20
    def __init__(self, scene, datafile): 
        gameEngine.TileMap.__init__(self, scene)
        """
            Misc. Init
        """
        self.playDeathTheme = False
        self.deathDelayCounter = 0        
        self.setBoundary(True, True, True, False)
        resources.playMusic(resources.mfxStartScene)
        
        """
            Load and pass data file information
        """
        self.ritzLevelLoader = RitzLevelLoader(datafile)
        self.loadTileImages(self.ritzLevelLoader.getTileDirectory(), self.ritzLevelLoader.getTileImages())
        self.setTileSize(self.ritzLevelLoader.getTileSize())
        self.setTiles(self.ritzLevelLoader.getTokens())

        """
            Load and add entities
        """
        self.ritzSprite = Ritz(self.scene, self, self.ritzLevelLoader.getStartLocation())
        self.enemiesGroup = pygame.sprite.Group()
        self.miscGroup = pygame.sprite.Group()

        for data in self.ritzLevelLoader.getEntityInfo():
            if data[0] == 'goomba':
                self.enemiesGroup.add(Goomba(self.scene, self, (data[1], data[2])))
            elif data[0] == 'coin':
                self.miscGroup.add(Coin(self.scene, self, (data[1], data[2])))
            elif data[0] == 'shyguy':
                self.enemiesGroup.add(ShyGuy(self.scene, self, (data[1], data[2])))
            elif data[0] == 'door':
                self.addSprite(Door(self.scene, self, (data[1], data[2])))
             
        self.addSprite(self.ritzSprite)   
        self.addGroup(self.enemiesGroup)
        self.addGroup(self.miscGroup)
        
    def reset(self):
        resources.playMusic(resources.mfxStartScene)
        self.ritzSprite = Ritz(self.scene, self, self.ritzLevelLoader.getStartLocation())
        self.addSprite(self.ritzSprite) 
        self.playDeathTheme = False 
        
    def __handleDeaths(self):
        """
            Ritz blood death splatter
        """
        if self.ritzSprite.isDead and not self.playDeathTheme:
            self.playDeathTheme = True
            self.playerDeath = True
            resources.playMusic(resources.mfxDeathTheme, 1)
            bloodSplatter = graphics.BloodSplatter(self.scene, 50, self.ritzSprite.rect.center)
            self.addGroup(bloodSplatter.getBloodGroup())
            self.ritzSprite.kill()
            
        if not self.ritzSprite.alive():
            self.deathDelayCounter += 1
            if self.deathDelayCounter == self.DEATH_DELAY:
                self.deathDelayCounter = 0
                self.reset()
                
    def update(self):
        gameEngine.TileMap.update(self)
        self.__handleDeaths()
        """
            Bound scroll to ritz's position
        """
        self.setScrollPosition(self.ritzSprite.rect.centerx - self.screen.get_width() / 2, 
                               self.ritzSprite.rect.centery - self.screen.get_height() / 2)
        
    def doEvents(self, event):
        if event.type == pygame.KEYUP:
            if self.ritzSprite.shooting:
                self.addSprite(RitzBullet(self.scene, self.ritzSprite.horizontalFacing,
                                          self.ritzSprite.rect.center))
                self.ritzSprite.sndShoot.play()
                


        
              
""" Score Counter """
#Displays the current score using normal font, color white.
class ScoreCounter(pygame.sprite.Sprite):
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
        
""" Life Counter"""
#Displays the number of lives the user currently has.
#If the number of lives decreases to zero than the alive
#flag is false. The life counter with an image of ritz times
#the number of lives
class LifeCounter(pygame.sprite.Sprite):
    NUM_OF_LIVES = 3
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.lives = self.NUM_OF_LIVES
        self.center = center
        self.ritzImage = pygame.image.load("gfx/ritz/idle0.png")

        self.__renderImage()
        
    def __renderImage(self):
        self.image = pygame.surface.Surface((self.lives * self.ritzImage.get_width(), 50), pygame.SRCALPHA)
        for life in range(self.lives):
            self.image.blit(self.ritzImage, (life * self.ritzImage.get_width(), 0))
        
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        
    def addLife(self):
        self.lives += 1
        self.__renderImage()
        
    def removeLife(self):
        self.lives -= 1
        self.__renderImage()
        
        

        
        
        
""" Door Sprite """
class Door(gameEngine.MySprite):
    def __init__(self, scene, center):
        gameEngine.MySprite.__init__(self, scene, center, "misc/door.png")

        self.scene = scene
        self.applyPhysics = False
        
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        
    def __AI(self):
        self.currentLevel = self.scene.currentLevel
        self.ritzSprite = self.currentLevel.ritzSprite
        if self.collidesWith(self.ritzSprite.rect):
            self.currentLevel.playerWon = True
                
"""Coin Sprite """
class Coin(gameEngine.MySprite):
    IDLE_IMG_MAX = 8
    POINTS = 25
    def __init__(self, scene, tileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "misc/coin0.png")
        self.idleImages = []
        self.tileMap = tileMap
        
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
        
          
""" Shy guy sprite """
class ShyGuy(gameEngine.MySprite):
    
    IDLE_IMG_MAX = 3
    WALK_IMG_MAX = 3
    
    WALK_SPEED = 3
    JUMP_SPEED = -8
    
    MIN_IDLE_DELAY = 300
    MAX_IDLE_DELAY = 400
    IDLE_WAIT = 80
    HEALTH_MAX = 50
    
    def __init__(self, scene, tileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "enemies/shyguy_idle0.png")        
        
        self.idleImages = []
        self.walkImages = []
        self.tileMap = tileMap
        
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
        if self.tileMap.ritzSprite != None:
            if self.collidesWith(self.tileMap.ritzSprite.rect):
                self.tileMap.ritzSprite.isDead = True
            
        #Make shy guy jump if there is a tile infront
        if self.horizontalFacing == self.FACE_LEFT:
            adjacentDir = -2
            self.setDX(-self.WALK_SPEED)
        elif self.horizontalFacing == self.FACE_RIGHT:
            adjacentDir = 2
            self.setDX(self.WALK_SPEED)
    
        #Get tile index of shy guy
        (ixPosition, iyPosition) = self.tileMap.getIndexAt(self.rect.centerx, self.rect.centery)
        adjacentTile = self.tileMap.getTileAt(ixPosition + adjacentDir, iyPosition)
        checkAdjacentTile = self.tileMap.isTileCollidable(adjacentTile)
        
        if checkAdjacentTile:
            self.jump = True
            
        if self.jump and self.onGround:
            self.setDY(self.JUMP_SPEED)
            self.jump = False
            self.onGround = False
        
    def deductHealth(self, amt):
        self.health -= amt
        if self.health <= 0:
            self.isDead = True
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        self.__handleAnimation()
        self.__handleOrientation()
        
                 
"""Enemy Sprites """
class Goomba(gameEngine.MySprite):
    
    IDLE_IMG_MAX = 3
    WALK_IMG_MAX = 3
    
    WALK_SPEED = 4
    
    MIN_IDLE_DELAY = 60
    MAX_IDLE_DELAY = 120
    IDLE_WAIT = 80
    HEALTH_MAX = 30
    
    def __init__(self, scene, tileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "enemies/goomba_idle0.png")        
        
        self.idleImages = []
        self.walkImages = []
        self.tileMap = tileMap
        
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
        
        #Prepare to be idle
        """
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
            
        #If goomba hits tile (left or right) reverse direction
        for direction in self.collisionDirs:
            if direction == self.COLLIDE_RIGHT:
                self.setDX(self.WALK_SPEED)
            elif direction == self.COLLIDE_LEFT:
                self.setDX(-self.WALK_SPEED)
                
        #Kill Ritz on collison
        if self.tileMap.ritzSprite != None:
            if self.collidesWith(self.tileMap.ritzSprite.rect):
                self.tileMap.ritzSprite.isDead = True
                
    def deductHealth(self, amt):
        self.health -= amt
        if self.health <= 0:
            self.isDead = True
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        self.__handleAnimation()
        self.__handleOrientation()
        
        
""" Ritz Bullet Sprite """
class RitzBullet(gameEngine.MySprite):
    
    SPEED = 20
    FADE_DELAY = 250
    DAMAGE = 10
    POINTS = 10
    
    def __init__(self, scene, facing, center):
        gameEngine.MySprite.__init__(self, scene, center, "ritzbullet.png")
        self.scene = scene
        self.facing = facing
        self.fadeCounter = 0
        self.__setUp()
        self.__loadSounds()
        
    def __loadSounds(self):
        self.sndCollision = pygame.mixer.Sound("sfx/bullet_hit.ogg")
        
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
            
    def __AI(self):
        #Ai of bullet checks for collisions with other entities, and
        #damages them. On collision the object will be destroyed.
        self.scoreBoard = self.scene.scoreCounterSprite
        enemiesHit = pygame.sprite.spritecollide(self, self.tileMap.enemiesGroup, False)
        for enemy in enemiesHit:
            #The speed of the bullet must be moving, otherwise bullets on ground
            #will kill enemies.
            if self.speed != 0:
                enemy.deductHealth(self.DAMAGE)
                self.sndCollision.play()
                self.scoreBoard.addScore(10)
                self.kill()
            


            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        self.__checkFadeStatus()
        
""" Our hero avatar sprite """
class Ritz(gameEngine.MySprite):
    IDLE_IMG_MAX = 4
    WALK_IMG_MAX = 4
    FALLING_IMG_MAX = 2
    JUMPING_IMG_MAX = 2
    
    WALK_SPEED = 5
    JUMP_SPEED = -10
    
    def __init__(self, scene, tileMap, center):
        gameEngine.MySprite.__init__(self, scene, center, "ritz/idle0.png")

        self.tileMap = tileMap
        
        self.idleImages = []
        self.walkImages = []
        self.jumpingImages = []
        self.fallingImages = []

        self.animationCounter = 0
        self.animationDelay = 0
        self.delayCounter = 0
        self.shooting = False
        self.onGround = False
        self.falling = True
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
            
    def __handleCollision(self):
        tileMap = self.tileMap
        miscGroup = tileMap.miscGroup
        scoreBoard = self.scene.scoreCounterSprite
        
        for coin in pygame.sprite.spritecollide(self, miscGroup, False):
            coin.sndCoin.play()
            scoreBoard.addScore(coin.POINTS)
            coin.kill()
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__handleAnimation()
        self.__handleFalling()
        self.__handleWalking()
        self.__handleShooting()
        self.__handleCollision()
            

            

                
""" Level Classes """
class LevelOne(gameEngine.TileMap):
    
    DEATH_DELAY = 100
    
    def __init__(self, scene, datafile): 
        gameEngine.TileMap.__init__(self, scene, datafile)
        
    def init(self):
        gameEngine.TileMap.init(self)
        self.playDeathTheme = False 
        self.deathDelayCounter = 0
        self.playerDeath = False
        self.playerWon = False
        
        #Set map boundary detections
        self.setBoundary(True, True, True, False)
        
        #Create Ritz Sprite
        self.ritzSprite = Ritz(self.scene, self, (self.startx, self.starty))
        
        #Create other entitiy sprites
        self.enemiesGroup = pygame.sprite.Group()
        self.coinGroup = pygame.sprite.Group()
        self.doorGroup = pygame.sprite.Group()
        for data in self.entityData:
            if data[0] == 'goomba':
                self.enemiesGroup.add(Goomba(self.scene, self, (data[1], data[2])))
            elif data[0] == 'coin':
                self.coinGroup.add(Coin(self.scene, self, (data[1], data[2])))
            elif data[0] == 'shyguy':
                self.enemiesGroup.add(ShyGuy(self.scene, self, (data[1], data[2])))
            elif data[0] == 'door':
                self.doorGroup.add(Door(self.scene, (data[1], data[2])))
                
        self.addGroup(self.enemiesGroup)
        self.addGroup(self.doorGroup)
        self.addGroup(self.coinGroup)
        #Add sprites to the map
        self.addSprite(self.ritzSprite)

        #Load music theme
        pygame.mixer.music.load("mfx/t1.ogg")
        pygame.mixer.music.play(-1)
        
    
    def __handleDeaths(self):
        self.playerDeath = False
        #Check if ritz is dead and play death theme
        if self.ritzSprite.isDead and not self.playDeathTheme:
            self.playDeathTheme = True
            self.playerDeath = True
            pygame.mixer.music.load("mfx/death.ogg")
            pygame.mixer.music.play()
            #Poor blood everywhere
            for bloodCount in range(0, 50):
                self.addSprite(Blood(self.scene, (self.ritzSprite.rect.center)))
            self.ritzSprite.kill()
            
        #Create delay on death, then reset level
        if not self.ritzSprite.alive():
            self.deathDelayCounter += 1
            if self.deathDelayCounter == self.DEATH_DELAY:
                self.deathDelayCounter = 0
                self.reset()
                
        #Check if any other sprites are dead
        for enemy in self.enemiesGroup.sprites():
            if enemy.isDead:
                for bloodCount in range(0, 20):
                    self.addSprite(Blood(self.scene, (enemy.rect.center)))
                enemy.kill()
          
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
                
class LevelTwo(gameEngine.TileMap):
    
    DEATH_DELAY = 100
    
    def __init__(self, scene, datafile): 
        gameEngine.TileMap.__init__(self, scene, datafile)
        
    def init(self):
        gameEngine.TileMap.init(self)
        self.playDeathTheme = False 
        self.deathDelayCounter = 0
        self.playerDeath = False
        self.playerWon = False
        
        #Set map boundary detections
        self.setBoundary(True, True, True, False)
        
        #Create Ritz Sprite
        self.ritzSprite = Ritz(self.scene, self, (self.startx, self.starty))
        
        #Create other entitiy sprites
        self.enemiesGroup = pygame.sprite.Group()
        self.coinGroup = pygame.sprite.Group()
        self.doorGroup = pygame.sprite.Group()
        for data in self.entityData:
            if data[0] == 'goomba':
                self.enemiesGroup.add(Goomba(self.scene, self, (data[1], data[2])))
            elif data[0] == 'coin':
                self.coinGroup.add(Coin(self.scene, self, (data[1], data[2])))
            elif data[0] == 'shyguy':
                self.enemiesGroup.add(ShyGuy(self.scene, self, (data[1], data[2])))
            elif data[0] == 'door':
                self.doorGroup.add(Door(self.scene, (data[1], data[2])))
                
        self.addGroup(self.enemiesGroup)
        self.addGroup(self.doorGroup)
        self.addGroup(self.coinGroup)
        #Add sprites to the map
        self.addSprite(self.ritzSprite)

        #Load music theme
        pygame.mixer.music.load("mfx/t1.ogg")
        pygame.mixer.music.play(-1)
        
    
    def __handleDeaths(self):
        self.playerDeath = False
        #Check if ritz is dead and play death theme
        if self.ritzSprite.isDead and not self.playDeathTheme:
            self.playDeathTheme = True
            self.playerDeath = True
            pygame.mixer.music.load("mfx/death.ogg")
            pygame.mixer.music.play()
            #Poor blood everywhere
            for bloodCount in range(0, 50):
                self.addSprite(Blood(self.scene, (self.ritzSprite.rect.center)))
            self.ritzSprite.kill()
            
        #Create delay on death, then reset level
        if not self.ritzSprite.alive():
            self.deathDelayCounter += 1
            if self.deathDelayCounter == self.DEATH_DELAY:
                self.deathDelayCounter = 0
                self.reset()
                
        #Check if any other sprites are dead
        for enemy in self.enemiesGroup.sprites():
            if enemy.isDead:
                for bloodCount in range(0, 20):
                    self.addSprite(Blood(self.scene, (enemy.rect.center)))
                enemy.kill()
                
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
                
                
class LevelThree(gameEngine.TileMap):
    
    DEATH_DELAY = 100
    
    def __init__(self, scene, datafile): 
        gameEngine.TileMap.__init__(self, scene, datafile)
        
    def init(self):
        gameEngine.TileMap.init(self)
        self.playDeathTheme = False 
        self.deathDelayCounter = 0
        self.playerDeath = False
        self.playerWon = False
        
        #Set map boundary detections
        self.setBoundary(True, True, True, False)
        
        #Create Ritz Sprite
        self.ritzSprite = Ritz(self.scene, self, (self.startx, self.starty))
        
        #Create other entitiy sprites
        self.enemiesGroup = pygame.sprite.Group()
        self.coinGroup = pygame.sprite.Group()
        self.doorGroup = pygame.sprite.Group()
        for data in self.entityData:
            if data[0] == 'goomba':
                self.enemiesGroup.add(Goomba(self.scene, self, (data[1], data[2])))
            elif data[0] == 'coin':
                self.coinGroup.add(Coin(self.scene, self, (data[1], data[2])))
            elif data[0] == 'shyguy':
                self.enemiesGroup.add(ShyGuy(self.scene, self, (data[1], data[2])))
            elif data[0] == 'door':
                self.doorGroup.add(Door(self.scene, (data[1], data[2])))
                
        self.addGroup(self.enemiesGroup)
        self.addGroup(self.doorGroup)
        self.addGroup(self.coinGroup)
        #Add sprites to the map
        self.addSprite(self.ritzSprite)

        #Load music theme
        pygame.mixer.music.load("mfx/t1.ogg")
        pygame.mixer.music.play(-1)
        
    
    def __handleDeaths(self):
        self.playerDeath = False
        #Check if ritz is dead and play death theme
        if not self.ritzSprite.alive() and not self.playDeathTheme:
            self.playDeathTheme = True
            self.playerDeath = True
            pygame.mixer.music.load("mfx/death.ogg")
            pygame.mixer.music.play()
        
        #Create delay on death, then reset level
        if not self.ritzSprite.alive():
            self.deathDelayCounter += 1
            if self.deathDelayCounter == self.DEATH_DELAY:
                self.deathDelayCounter = 0
                self.reset()
                
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
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.playDeathTheme = False
        self.physics = gameEngine.Physics()
                
        #Load level one
        self.levelOne = LevelOne(self, "level.dat")
        self.levelTwo = LevelTwo(self, "level2.dat")
        self.levelThree = LevelThree(self, "level3.dat")
        
        self.__setLevel(self.levelOne)

  
    def __checkKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pass
    
    def __setLevel(self, level):
        self.currentLevel = level
        
        self.backgroundSprite = gameEngine.MySprite(self, (self.screen.get_width() / 2, self.screen.get_height() / 2), "169721-super-mario-super-mario.png.jpeg")
        self.backgroundSprite.image.fill((0, 0, 0))
        self.lifeCounterSprite = LifeCounter((45, 35))
        self.scoreCounterSprite = ScoreCounter((self.screen.get_width() - 150, 20))
        
        self.backgroundGroup = pygame.sprite.Group(self.backgroundSprite)
        self.l1MapSpriteGroup = pygame.sprite.Group(self.currentLevel)
        self.topLayerGroup = pygame.sprite.Group(self.lifeCounterSprite, self.scoreCounterSprite)
        
        # Add level one sprites/groups
        self.addGroup(self.backgroundGroup)
        self.addGroup(self.l1MapSpriteGroup)
        self.addGroup(self.topLayerGroup)
        
    def __changeLevel(self, level):
        self.l1MapSpriteGroup.remove(self.currentLevel)
        self.l1MapSpriteGroup.add(level)
        self.currentLevel = level
        
    def __trackGame(self):
        #This is called automatically from update(). This is
        #important because this allows information to be transferred between scenes.
        #Also to track game for internal purposes.
        self.gameScore = self.scoreCounterSprite.score
        if self.currentLevel.playerDeath:
            self.lifeCounterSprite.removeLife()
        elif self.currentLevel.playerWon:
            if self.currentLevel == self.levelOne:
                self.__changeLevel(self.levelTwo)
            elif self.currentLevel == self.levelTwo:
                self.__changeLevel(self.levelThree)
        
        if self.lifeCounterSprite.lives == 0 and self.currentLevel.deathDelayCounter == 0:
            self.stop()
                 
    def doEvents(self, event):
        self.currentLevel.doEvents(event)
        
    def update(self):
        gameEngine.Scene.update(self)
        self.__trackGame()
        self.__checkKeys()

        
class GameEndScene(gameEngine.Scene):
    def __init__(self, gameScore, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.gameScore = gameScore
        
        screenWidth = self.screen.get_width()
        screenHeight = self.screen.get_height()
        
        #Start intro theme
        pygame.mixer.music.load("mfx/defeat_theme.ogg")
        pygame.mixer.music.play(-1)
        
        #Create fonts sprites
        self.deathScoreSprite = gameEngine.MyFontSprite("You died! Score: {0}".format(self.gameScore), 20, 
                                                         (screenWidth / 2 - 20, 200), (255,255,255))
        
        self.continueSprite = gameEngine.MyFontSprite("Press any key to continue", 32,
                                                    (screenWidth / 2, screenHeight - 100), (255,255,255))
        
        self.backgroundSprite = gameEngine.MySprite(self, (screenWidth / 2, screenHeight / 2), "background.png")
        
        #Create groups for scene
        self.backgroundGroup = pygame.sprite.Group(self.backgroundSprite)
        self.fontGroup = pygame.sprite.Group(self.deathScoreSprite, self.continueSprite)
        
        
        #Add groups to scene
        self.addGroup(self.backgroundGroup)
        self.addGroup(self.fontGroup)
                
    def doEvents(self, event):
        if event.type == pygame.KEYDOWN:
            self.stop()
            
    
class StartScene(gameEngine.Scene):
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.startSceneMap = RitzTileMap(self, "start.dat")
        """
            Misc. Init
        """        
        self.scoreCounterSprite = None     
        self.setStopBounds(self.STOP_NEVER)

        """
            Create and add sprite groups
        """
        self.backgroundGroup = pygame.sprite.Group(self.startSceneMap)
        self.addGroup(self.backgroundGroup)

class InstructionsScene(gameEngine.Scene):
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.instructionSceneMap = RitzTileMap(self, "instructions.dat")
        
        """
            Misc. Init
        """        
        self.scoreCounterSprite = None     
        self.setStopBounds(self.STOP_NEVER)

        """
            Create and add sprite groups
        """
        self.backgroundGroup = pygame.sprite.Group(self.instructionSceneMap)
        self.addGroup(self.backgroundGroup)
        
class SplashScene(gameEngine.Scene):
    SPLASH_DEPLAY = 120
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        """
            Misc. Init
        """
        self.splashCount = 0
        resources.playMusic(resources.mfxSplashScene, 1)
        
        """
            Create and add sprite groups
        """
        self.backgroundSprite = gameEngine.MySprite(self, (self.width / 2, self.height / 2), "splashscreen.png")
        self.backgroundGroup = pygame.sprite.Group(self.backgroundSprite)
        self.addGroup(self.backgroundGroup)

        
    def update(self):
        gameEngine.Scene.update(self)
        self.__countDown()
        
    """
        Splash scene delay handler
    """
    def __countDown(self):
        if self.splashCount == self.SPLASH_DEPLAY:
            self.splashCount = 0
            self.stop()
        else:
            self.splashCount += 1


"""
    The life of our program. Runs the game scenes sequentially.
    Follows the order: Splash Scene, Start Scene, Play Scene, End Scene.          
"""
def main():
    resources.init()

    sceneFlow = SCENE_SPLASH
    programExit = False

    while not programExit:
        if sceneFlow == SCENE_SPLASH:
            splashScene = SplashScene((800, 600), "Ritz by Justin Hellsten - Splash")
            splashScene.start()
            programExit = splashScene.exit
        elif sceneFlow == SCENE_INSTRUCTIONS:
            instructionScene = InstructionsScene((800, 600), "Ritz by Justin Hellsten - Instructions")
            instructionScene.start()
            programExit = instructionScene.exit
        elif sceneFlow == SCENE_START:
            startScene = StartScene((800, 600), "Ritz by Justin Hellsten - Start")
            startScene.start()
            programExit = startScene.exit
        elif sceneFlow == SCENE_PLAY:
            gamePlayScene = GamePlayScene((800, 600), "Ritz by Justin Hellsten - Play")
            gamePlayScene.start()
            programExit = gamePlayScene.exit
        elif sceneFlow == SCENE_END:
            endGameScene = GameEndScene(gamePlayScene.gameScore, (800, 600), "Ritz by Justin Hellsten - End")
            endGameScene.start()
            programExit = endGameScene.exit

        sceneFlow += 1
        if sceneFlow > SCENE_END:
            sceneFlow = 0

if __name__ == "__main__": main()
    
