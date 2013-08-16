'''
Created on Aug 15, 2013

@author: justin
'''

import pygame, resources, miscellaneous, enemies, gameEngine, graphics


class RitzBullet(gameEngine.MySprite):
    
    SPEED = 20
    FADE_DELAY = 250
    DAMAGE = 10
    POINTS = 10
    
    def __init__(self, scene, ritzTileMap, scoreBoard, facing, center):
        gameEngine.MySprite.__init__(self, scene, center, "ritzbullet.png")
        self.facing = facing
        self.ritzTileMap = ritzTileMap
        self.scoreBoard = scoreBoard
        self.fadeCounter = 0

        if self.facing == self.FACE_LEFT:
            self.setDX(-self.SPEED)
        if self.facing == self.FACE_RIGHT:
            self.setDX(self.SPEED)
            
        self.sndCollision = pygame.mixer.Sound("sfx/bullet_hit.ogg")

        
    def __checkFadeStatus(self):
        if self.fadeCounter < self.FADE_DELAY:
            self.fadeCounter += 1
        else:
            self.kill()
            
    def __AI(self):
        enemiesHit = pygame.sprite.spritecollide(self, self.ritzTileMap.enemiesGroup, False)
        for enemy in enemiesHit:
            if self.speed != 0:
                enemy.deductHealth(self.DAMAGE)
                self.sndCollision.set_volume(0.5)
                self.sndCollision.play()
                if self.scoreBoard != None:
                    self.scoreBoard.addScore(self.POINTS)
                self.kill()
      
    def update(self):
        gameEngine.MySprite.update(self)
        self.__AI()
        self.__checkFadeStatus()
        

class Ritz(gameEngine.MySprite):
    IDLE_IMG_MAX = 4
    WALK_IMG_MAX = 4
    FALLING_IMG_MAX = 2
    JUMPING_IMG_MAX = 2
    
    WALK_SPEED = 5
    JUMP_SPEED = -10
    
    def __init__(self, scene, ritzTileMap, scoreBoard, center):
        gameEngine.MySprite.__init__(self, scene, center, "ritz/idle0.png")

        self.ritzTileMap = ritzTileMap
        self.scoreBoard = scoreBoard
        
        self.idleImages = []
        self.walkImages = []
        self.jumpingImages = []
        self.fallingImages = []

        self.animationCounter = 0
        self.animationDelay = 0
        self.delayCounter = 0
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
        self.sndDeath = pygame.mixer.Sound("sfx/death.ogg")
        self.sndJump.set_volume(0.05)
        self.sndShoot.set_volume(0.1)
        self.sndDeath.set_volume(0.3)
        
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

        for coin in pygame.sprite.spritecollide(self, self.ritzTileMap.miscGroup, False):
            coin.sndCoin.play()
            self.scoreBoard.addScore(coin.POINTS)
            coin.kill()
            
    def die(self):
        pygame.mixer.music.stop()
        self.sndDeath.play()
        bloodSplatter = graphics.BloodSplatter(self.scene, 50, self.rect.center)
        self.ritzTileMap.addGroup(bloodSplatter.getBloodGroup())
        self.kill()
            
    def update(self):
        gameEngine.MySprite.update(self)
        self.__handleAnimation()
        self.__handleFalling()
        self.__handleWalking()
        self.__handleCollision()
        
    def doEvents(self, event):
        gameEngine.MySprite.doEvents(self, event)
        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            if keys[pygame.K_SPACE]:
                self.ritzTileMap.addSprite(RitzBullet(self.scene, self.ritzTileMap, self.scoreBoard,
                                                      self.horizontalFacing, (self.rect.center)))
                self.sndShoot.play()

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
    TRANPARENT_TILE = 0
    SPIKE_TILE = 20
    def __init__(self, scene, datafile, noRitz = False): 
        gameEngine.TileMap.__init__(self, scene)
        """
            Misc. Init
        """
        self.setBoundary(True, True, True, False)

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
        self.ritzSprite = Ritz(self.scene, self, None, self.ritzLevelLoader.getStartLocation())
        self.enemiesGroup = pygame.sprite.Group()
        self.miscGroup = pygame.sprite.Group()

        for data in self.ritzLevelLoader.getEntityInfo():
            if data[0] == 'goomba':
                self.enemiesGroup.add(enemies.Goomba(self.scene, self, (data[1], data[2])))
            elif data[0] == 'coin':
                self.miscGroup.add(miscellaneous.Coin(self.scene, self, (data[1], data[2])))
            elif data[0] == 'shyguy':
                self.enemiesGroup.add(enemies.ShyGuy(self.scene, self, (data[1], data[2])))
            elif data[0] == 'door':
                self.addStaticGroup(pygame.sprite.Group(miscellaneous.LevelDoor(self.scene, self, (data[1], data[2]))))
             
        if not noRitz:
            self.addSprite(self.ritzSprite)   
        self.addGroup(self.enemiesGroup)
        self.addGroup(self.miscGroup)
        
class RitzMap(RitzTileMap):
    DEATH_DELAY = 100
    def __init__(self, scene, datafile):
        RitzTileMap.__init__(self, scene, datafile)
        """
            Set Defaults
        """
        self.playDeathTheme = False
        self.deathDelayCounter = 0
              
    def update(self):
        RitzTileMap.update(self)
        self.__handleDeaths()
        """
            Bound scroll to ritz's position
        """
        self.setScrollPosition(self.ritzSprite.rect.centerx - self.screen.get_width() / 2, 
                               self.ritzSprite.rect.centery - self.screen.get_height() / 2)
                
    def reset(self):
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
        self.ritzSprite = Ritz(self.scene, self, None, self.ritzLevelLoader.getStartLocation())
        self.addSprite(self.ritzSprite) 
        self.playDeathTheme = False 

        
    def __handleDeaths(self):
        """
            Ritz blood death splatter
        """ 
        if not self.ritzSprite.alive():
            self.deathDelayCounter += 1
            if self.deathDelayCounter == self.DEATH_DELAY:
                self.deathDelayCounter = 0
                self.reset()
                                                     
class RitzLevel(RitzMap):
    DEATH_DELAY = 100
    def __init__(self, scene, datafile):
        RitzMap.__init__(self, scene, datafile)
        """
            Create Top Layer
        """
        self.scoreBoard = miscellaneous.ScoreBoard((scene.width - 100, 25))
        self.livesBoard = miscellaneous.LifeCounter(scene, (50,40), self.ritzSprite)
 
        self.topLayerGroup = pygame.sprite.Group(self.scoreBoard, self.livesBoard)
        self.scene.addTopLayerGroup(self.topLayerGroup)
        self.ritzSprite.scoreBoard = self.scoreBoard
        
    def reset(self):
        RitzMap.reset(self)
        self.livesBoard.removeLife()
        self.ritzSprite.scoreBoard = self.scoreBoard
                           
