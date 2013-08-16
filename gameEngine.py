'''
Created on Aug 1, 2013

@author: justin hellsten
'''

#Import and initialize
import pygame, math, gameEngineUtil
pygame.init()
    
class Physics():
    # This class holds information about the physics of the game engine.
    # All sprites adhere to this class is one way or another.
    # The game engine will create a physics object behind the scenes,
    # but if you wish to customize your own physics by all means use this class.
    def __init__(self):
        # Default Constants
        self.GRAVITY = 0.75
        
class Boundary():
    # This class holds more information about boundaries checks
    def __init__(self, leftBound, topBound, rightBound, bottomBound):
        self.leftBound = leftBound
        self.topBound = topBound
        self.rightBound = rightBound
        self.bottomBound = bottomBound
    
    
class TileMap(pygame.sprite.Sprite):
    
    DOOM_BOUNDARY_LIMIT = 50
    
    def __init__(self, scene):
        pygame.sprite.Sprite.__init__(self)
        self.scene = scene
        self.screen = self.scene.screen
        self.image = pygame.surface.Surface((0,0))
        self.rect = self.image.get_rect()
        
        self.tileImages = []
        self.groups = []
        self.staticGroups = []
        
        self.scrollx = 0
        self.scrolly = 0
        
        self.boundary = Boundary(False, False, False, False)
        
        
    def loadTileImages(self, directory, tileFiles):
        for tileFile in tileFiles:
            self.tileImages.append(pygame.image.load(directory + tileFile))
              
    def setTileSize(self, size):
        self.tilesize = size
                                            
    def addGroup(self, group):
        self.groups.append(group)
            
    def addStaticGroup(self, group):
        self.staticGroups.append(group)
        
    def setTiles(self, tokens):
        self.tiles = tokens
        

    
        

    def __renderMap(self):
        screenWidth = self.screen.get_width()
        screenHeight = self.screen.get_height()
        
        tilesPerRow = screenWidth / self.tilesize + 1
        tilesPerColumn = screenHeight / self.tilesize + 1
        
        firstTileIX = self.scrollx / self.tilesize
        firstTileIY = self.scrolly / self.tilesize
        tileOffSetX = firstTileIX * self.tilesize - self.scrollx
        tileOffSetY = firstTileIY * self.tilesize - self.scrolly
        originalOffSetX = tileOffSetX
        
        self.image = pygame.surface.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        
        # Draw the tiles to image
        for tileY in range(firstTileIY, firstTileIY + tilesPerColumn):
            for tileX in range(firstTileIX, firstTileIX + tilesPerRow):
                self.image.blit(self.tileImages[self.tiles[tileY][tileX]], (tileOffSetX, tileOffSetY), 
                                pygame.rect.Rect((0,0), (self.tilesize, self.tilesize)))
                tileOffSetX += self.tilesize

            tileOffSetX = originalOffSetX
            tileOffSetY += self.tilesize
  
        self.rect = self.image.get_rect()
        
    def __renderGroups(self):
        # Rendering sprites/entities in a tile map is different than
        # the traditional rendering in pygame. We must render based 
        # on the current scroll positions of the map. All entities are
        # relative to this position. All entities figuratively moved
        # in virtual space but are rendered correctly to the screen here.
        screenWidth = self.screen.get_width()
        screenHeight = self.screen.get_height()
        for staticGroup in self.staticGroups:
            for sprite in staticGroup.sprites():
                # if the entitity is visible on the screen, draw it
                if sprite.rect.right > self.scrollx and \
                    sprite.rect.left < self.scrollx + screenWidth and \
                    sprite.rect.bottom > self.scrolly and \
                    sprite.rect.top < self.scrolly + screenHeight:
                        self.image.blit(sprite.image, (sprite.rect.left - self.scrollx, 
                                        sprite.rect.top - self.scrolly))
                                
        for group in self.groups:
            for sprite in group.sprites():
                # if the entitity is visible on the screen, draw it
                if sprite.rect.right > self.scrollx and \
                    sprite.rect.left < self.scrollx + screenWidth and \
                    sprite.rect.bottom > self.scrolly and \
                    sprite.rect.top < self.scrolly + screenHeight:
                        self.image.blit(sprite.image, (sprite.rect.left - self.scrollx, 
                                        sprite.rect.top - self.scrolly))
                    
                    
    def __checkGroupBounds(self):
        # Checks the boundary/tile collisions of all groups.
        # Boundary collisions are left, top, right bottom walls of the map.
        # By current designs any object will be prohibited from leaving the boundaries.
        # Tile collisions is true for any object which is in contact with a non transparent
        # tile. Objects can pass through transparent tiles.

        mapWidth, mapHeight = self.getSize()

        for group in self.groups:
            for sprite in group.sprites():

                # Check wall boundaries
                if sprite.rect.left < 0 and self.boundary.leftBound:
                    sprite.rect.left = 0
                    sprite.dx = 0
                    sprite.wallCollision = sprite.COLLIDE_LEFT
                if sprite.rect.right > mapWidth and self.boundary.rightBound:
                    sprite.rect.right = mapWidth
                    sprite.dx = 0
                    sprite.wallCollision = sprite.COLLIDE_RIGHT
                if sprite.rect.top < 0 and self.boundary.topBound:
                    sprite.rect.top = 0
                    sprite.dy = 0
                    sprite.wallCollision = sprite.COLLIDE_TOP
                if sprite.rect.bottom > mapHeight and self.boundary.bottomBound:
                    sprite.rect.bottom = mapHeight
                    sprite.dy = 0
                    sprite.wallCollision = sprite.COLLIDE_BOTTOM
                    
                #Check boundary of doom
                if sprite.rect.left < -self.DOOM_BOUNDARY_LIMIT or \
                sprite.rect.right > mapWidth + self.DOOM_BOUNDARY_LIMIT or \
                sprite.rect.top < -self.DOOM_BOUNDARY_LIMIT or \
                sprite.rect.bottom > mapHeight + self.DOOM_BOUNDARY_LIMIT:
                    try:
                        sprite.die()
                    except:
                        pass
                    
                # Check tile collisions
                topIndex = int(sprite.rect.top) / self.tilesize
                bottomIndex = int(sprite.rect.bottom) / self.tilesize + 1
                leftIndex = int(sprite.rect.left) / self.tilesize
                rightIndex = int(sprite.rect.right) / self.tilesize + 1

                allTransparent = True
                sprite.collisionDirs = []
                
                for iy in range(topIndex , bottomIndex):
                    for ix in range(leftIndex, rightIndex):
                        # Get index size of map. Used for out of bounds checking.
                        (indexWidth, indexHeight) = self.getIndexSize()
                        if ix < indexWidth and iy < indexHeight and \
                        self.tiles[iy][ix] != self.TRANPARENT_TILE:
                            performCollisionCheck = True
                        else:
                            performCollisionCheck = False
                            
                        if performCollisionCheck:
                            #If tile is a spike kill the sprite
                            if self.tiles[iy][ix] == self.SPIKE_TILE:
                                try:
                                    sprite.die()
                                except:
                                    pass     
                                         
                             
                            
                            allTransparent = False
                            tilePosition = (ix * self.tilesize, iy * self.tilesize)
                            # Get last location
                            
                            collisionDirs = sprite.collisionDirection((tilePosition[0], tilePosition[1], 
                                                                                   self.tilesize, self.tilesize))
                            sprite.collisionDirs.extend(collisionDirs)
                            sprite.collisionDirs = list(set(sprite.collisionDirs))
                            
                            for direction in collisionDirs:
                                if direction == sprite.COLLIDE_TOP:
                                    sprite.rect.bottom = tilePosition[1] 
                                    sprite.setDY(0)
                                    sprite.setDX(0)
                                    sprite.falling = False
                                elif direction == sprite.COLLIDE_BOTTOM:
                                    sprite.rect.top = tilePosition[1] + self.tilesize
                                    sprite.setDY(0)
                                elif direction == sprite.COLLIDE_LEFT:
                                    sprite.rect.right = tilePosition[0]
                                    sprite.setDX(0)
                                elif direction == sprite.COLLIDE_RIGHT:
                                    sprite.rect.left = tilePosition[0] + self.tilesize
                                    sprite.setDX(0)

                if allTransparent:
                    sprite.falling = True

                    
    def __checkBounds(self):
        # Checks and adjusts the scroll position so it stays
        # in the bounds of the map.
        screen = self.scene.screen
        screenWidth = screen.get_width()
        screenHeight = screen.get_height()
        mapWidth, mapHeight = self.getSize()

        if self.scrollx < 0:
            self.scrollx = 0
        if self.scrollx > mapWidth - screenWidth:
            self.scrollx = mapWidth - screenWidth
        if self.scrolly < 0:
            self.scrolly = 0
        if self.scrolly > mapHeight - screenHeight:
            self.scrolly = mapHeight - screenHeight
            
            
    def reset(self):
        self.groups = []
        self.init()
        

        
    def grabGroups(self):
        #Returns the tile maps entities (group)
        return self.groups
    
    def addSprite(self, sprite):
        # Create group for sprite, then pass into groups
        self.groups.append(pygame.sprite.Group(sprite))
        
    def setScrollPosition(self, xAmt, yAmt):
        # Sets the scroll positions. This dictates
        # how the tile map is rendered to the screen.
        # All entities inside the TileMap sprite are
        # shifted accordingly to scroll values.
        self.scrollx = xAmt
        self.scrolly = yAmt
        self.__checkBounds()
        
                
    def setBoundary(self, leftBound, topBound, rightBound, bottomBound):
        self.boundary.leftBound = leftBound
        self.boundary.topBound = topBound
        self.boundary.rightBound = rightBound
        self.boundary.bottomBound = bottomBound
        
    def getSize(self):
        # Returns a tuple (map width, map height).
        # Remove the buffer tiles around the right and bottom edges.
        return ((len(self.tiles[0]) - 1) * self.tilesize, len(self.tiles) * self.tilesize)
                    
    def getIndexSize(self):
        # Returns a tuple (index width, index height).
        # The index values of the map are returned.
        return (len(self.tiles[0]), len(self.tiles))
        
    def getTileAt(self, ix, iy):
        return self.tiles[iy][ix]
    
    def isTileCollidable(self, tile):
        if tile == self.TRANPARENT_TILE:
            return False
        else:
            return True
        
    def getIndexAt(self, x, y):
        return (int(x / self.tilesize), int(y / self.tilesize))
    
    def init(self):
        #Used to initialize map. Feel free to override and 
        #customize your map intialization using this method
        pass
                    
    def update(self):
        #Updates the following: events, group collision detection,
        #and render adjustment based on group. When overriden
        #the base class update method must be called.

        for group in self.groups:
            group.update()     

        for staticGroup in self.staticGroups:
            staticGroup.update()
            
        self.__checkGroupBounds()
        self.__renderMap()
        self.__renderGroups()

    def doEvents(self, event):
        for group in self.groups:
            for sprite in group:
                sprite.doEvents(event)
        for staticGroup in self.staticGroups:
            for staticSprite in staticGroup:
                staticSprite.doEvents(event)
        
    
class MySprite(pygame.sprite.Sprite):
    # My sprite is a temporary name...
    # This sprite will replace super sprite. You can
    # apply physics to the sprite as long as the physics
    # class has been set through setPhysics method.
    
    # Collision Directions
    COLLIDE_LEFT = 0
    COLLIDE_TOP = 1
    COLLIDE_RIGHT = 2
    COLLIDE_BOTTOM = 3
    COLLIDE_NONE = -1
    
    # Facing Constants
    FACE_UP = 0
    FACE_RIGHT = 1
    FACE_DOWN = 2
    FACE_LEFT = 3
    
    def __init__(self, scene, center, imageName = ""):
        pygame.sprite.Sprite.__init__(self)
        if imageName == "":
            self.masterImage = pygame.surface.Surface((0, 0), pygame.SRCALPHA)
        else:
            self.masterImage = pygame.image.load(gameEngineUtil.DIR_GFX + imageName)
        self.scene = scene
        self.image = self.masterImage
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.orginalCenter = center
        
        self.dx = 0
        self.dy = 0
        self.dir = 0
        self.speed = 0
        self.collisionDirs = []
        self.wallCollision = self.COLLIDE_NONE
        self.touchingWall = False
        self.applyPhysics = True
        
        self.falling = False
        self.jumping = False
        self.idle = False
        self.walking = False
        self.horizontalFacing = self.FACE_RIGHT
        self.isDead = False
       
    def __applyFlags(self):
        physics = self.scene.physics
        
        # If the sprite is falling, apply gravity and set 
        # walking, idle flags to false
        if self.falling and self.applyPhysics:
            self.addDY(physics.GRAVITY)
            self.walking = False
            self.idle = False

        # If dx ix not zero than the sprite is horizontally.
        # Thus if moving but not falling, walking is true
        if self.dx != 0 and not self.falling:
            self.walking = True
            self.idle = False
        else:
            self.walking = False
            self.idle = True
  
    def __calcPosition(self):
        # Applies dx, dy to x, y
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        
    def __updateVector(self):
        #calculate new speed and angle based on dx, dy
        #call this any time you change dx or dy
        
        self.speed = math.sqrt((self.dx * self.dx) + (self.dy * self.dy))
        
        dy = self.dy * -1
        dx = self.dx
        
        radians = math.atan2(dy, dx)
        self.dir = radians / math.pi * 180
        
        dxSign = cmp(self.dx, 0)
        dySign = cmp(self.dy, 0)
        if dxSign < 0:
            self.horizontalFacing = self.FACE_LEFT
        elif dxSign > 0:
            self.horizontalFacing = self.FACE_RIGHT

        if dySign < 0:
            self.jumping = True
        elif dySign > 0:
            self.jumping = False
        
    def hflip(self):
        # Flips the image of the sprite horizontally
        self.image = pygame.transform.flip(self.masterImage, True, False)
        
    def vflip(self):
        # Flips the image of the sprite vertically
        self.image = pygame.transform.flip(self.masterImage, False, True)
        
    def addForce(self, amt, angle):
        """ apply amt of thrust in angle.
            change speed and dir accordingly
            add a force straight down to simulate gravity
            in rotation direction to simulate spacecraft thrust
            in dir direction to accelerate forward
            at an angle for retro-rockets, etc.
        """

        #calculate dx dy based on angle
        radians = angle * math.pi / 180
        dx = amt * math.cos(radians)
        dy = amt * math.sin(radians) * -1
        
        self.dx += dx
        self.dy += dy
        self.__updateVector()
        
    def setDX(self, dx):
        """ changes dx value and updates vector """
        self.dx = dx
        self.__updateVector()
    
    def addDX(self, amt):
        """ adds amt to dx, updates vector """
        self.dx += amt
        self.__updateVector()
        
    def setDY(self, dy):
        """ changes dy value and updates vector """
        self.dy = dy
        self.__updateVector()

    def addDY(self, amt):
        """ adds amt to dy and updates vector """
        self.dy += amt
        self.__updateVector()
        
            
    def setSpeed(self, speed): 
        self.speed = speed
        self.__updateVector()
        
    def collidesWith(self, target):
        """ boolean function. Returns True if the sprite
            is currently colliding with the target rect,
        """
        collision = False
        if self.rect.colliderect(target):
            collision = True
        return collision
    
    def collisionDirection(self, (rectLeft, rectTop, width, height)):
        # Returns the collision direction. 
        # This method will call collideWith automatically. Check is 
        # based on last position of sprite.
        targetRect = pygame.rect.Rect((rectLeft, rectTop), (width, height))
        collisionList = []
        if self.collidesWith(targetRect):
            # Find direction of collisions and return them in a list.
            # We reverse increment our position until we find which side we
            # collided with. LEFT, TOP, RIGHT, BOTTOM.
            
            # Get last and current positions. Make sure the values are integers
            tempPosition = (int(self.rect.left), int(self.rect.top), 
                            int(self.rect.right), int(self.rect.bottom))
            lastPosition = (int(self.rect.left - self.dx), int(self.rect.top - self.dy),
                            int(self.rect.right - self.dx), int(self.rect.bottom - self.dy))
            
            # Get the sign of deltas so we know which way to increment
            signDY = cmp(int(self.dy), 0) * -1
            signDX = cmp(int(self.dx), 0) * -1

            # Check left right collision
            if signDX != 0:
                        
                for leftPosition in range(tempPosition[0], lastPosition[0] + 1, signDX):
                    if leftPosition == targetRect.right:
                        collisionList.append(self.COLLIDE_RIGHT)
                        
                for rightPosition in range(tempPosition[2], lastPosition[2] - 1, signDX):
                    if rightPosition == targetRect.left:
                        collisionList.append(self.COLLIDE_LEFT)
                        
            # Check top bottom collision
            if signDY != 0:               
                        
                for topPosition in range(tempPosition[1], lastPosition[1] + 1, signDY):
                    if topPosition == targetRect.bottom:
                        collisionList.append(self.COLLIDE_BOTTOM)

                for bottomPosition in range(tempPosition[3], lastPosition[3] - 1, signDY):
                    if bottomPosition == targetRect.top:
                        collisionList.append(self.COLLIDE_TOP)



        return collisionList
    
    def update(self):
        self.__applyFlags()
        self.__calcPosition()

    def doEvents(self, event):
        pass
    

class MyFontSprite(pygame.sprite.Sprite):
    def __init__(self, scene, (center), (width, height), text, size = 16, color = (255, 255, 255)):
        pygame.sprite.Sprite.__init__(self)
        self.scene = scene
        self.text = text
        self.size = size
        self.center = center
        self.color = color
        self.image = pygame.surface.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.center        
        self.__renderImage()
        
    def __renderImage(self):
        self.font = pygame.font.SysFont("None", self.size)
        for index, line in enumerate(self.text):
            fontSize = self.font.size(line)
            self.fontImage = self.font.render(line, 1, self.color)                
            self.image.blit(self.fontImage, (self.rect.width / 2 - fontSize[0] / 2, fontSize[1] * index))
        
    def changeText(self, text):
        self.text = text
        self.__renderImage()

    def changeColor(self, color):
        self.color = color
        self.__renderImage()
        
    def changeSize(self, size):
        self.size = size
        self.__renderImage()

    def changePosition(self, center):
        self.center = self.center
        self.__renderImage()

    def doEvents(self, event):
        pass
    
    def update(self):
        pass
    



















class MyBasicSprite(pygame.sprite.Sprite):
    def __init__(self, center, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    def update(self):
        pass
    
    def doEvents(self, event):
        pass
    


class BasicSprite(pygame.sprite.Sprite):
    """ use this sprite when you want to 
        directly control the sprite with dx and dy
        or want to extend in another direction than DirSprite
    """
    def __init__(self, scene, (center), (delta), (area), color):
        pygame.sprite.Sprite.__init__(self)
        self.screen = scene.screen
        self.image = pygame.surface.Surface(area)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.dx = delta[0]
        self.dy = delta[1]

    def update(self):
        self.rect.center = (self.rect.centerx + self.dx, self.rect.centery + self.dy)
        self.checkBounds()
        
    def checkBounds(self):
        scrWidth = self.screen.get_width()
        scrHeight = self.screen.get_height()
        
        if self.rect.right > scrWidth:
            self.rect.right = 0
        if self.rect.left < 0:
            self.rect.left = scrWidth
        if self.rect.top > scrHeight:
            self.rect.top = 0
        if self.rect.bottom < 0:
            self.rect.bottom = scrHeight

    def die(self):
        pass
    
class SuperSprite(pygame.sprite.Sprite):
    """ An enhanced Sprite class
        expects a gameEngine.Scene class as its one parameter
        Use methods to change image, direction, speed
        Will automatically travel in direction and speed indicated
        Automatically rotates to point in indicated direction
        Five kinds of boundary collision
    """
    
    # Collision Constants
    WRAP = 0
    BOUNCE = 1
    STOP = 2
    HIDE = 3
    CONTINUE = 4
    
    def __init__(self, scene):
        pygame.sprite.Sprite.__init__(self)
        self.scene = scene
        self.screen = scene.screen
        
        #create a default text image as a placeholder
        #This will usually be changed by a setImage call
        self.font = pygame.font.Font("freesansbold.ttf", 30)
        self.imageMaster = self.font.render(">sprite>", True, (0, 0,0), (0xFF, 0xFF, 0xFF))
        self.image = self.imageMaster
        self.rect = self.image.get_rect()
        
        #create properties
        #most will be changed through method calls
        self.x = 200
        self.y = 200
        self.dx = 0
        self.dy = 0
        self.dir = 0
        self.rotation = 0
        self.speed = 0
        self.maxSpeed = 10
        self.minSpeed = -3
        self.boundAction = self.WRAP
        self.pressed = False
        self.oldCenter = (100, 100)
    
    def update(self):
        self.oldCenter = self.rect.center
        self.checkEvents()
        self.__rotate()
        self.__calcVector()
        self.__calcPosition()
        self.__checkBounds()
        self.rect.center = (self.x, self.y)
    
    def checkEvents(self):
        """ overwrite this method to add your own event code """
        pass

    def __rotate(self):
        """ PRIVATE METHOD
            change visual orientation based on 
            rotation property.
            automatically called in update.
            change rotation property directly or with 
            rotateBy(), setAngle() methods
        """
        oldCenter = self.rect.center
        self.oldCenter = oldCenter
        self.image = pygame.transform.rotate(self.imageMaster, self.rotation)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
    
    def __calcVector(self):
        """ calculates dx and dy based on speed, dir
            automatically called in update() 
        """
        theta = self.dir / 180.0 * math.pi
        self.dx = math.cos(theta) * self.speed
        self.dy = math.sin(theta) * self.speed
        self.dy *= -1
    
    def __calcPosition(self):
        """ calculates the sprites position adding
            dx and dy to x and y.
            automatically called in update()
        """
        self.x += self.dx
        self.y += self.dy

    def __checkBounds(self):
        """ checks boundary and acts based on 
            self.BoundAction.
            WRAP: wrap around screen (default)
            BOUNCE: bounce off screen
            STOP: stop at edge of screen
            HIDE: move off stage and wait
            CONTINUE: keep going at present course and speed
            
            automatically called by update()
        """
        
        scrWidth = self.screen.get_width()
        scrHeight = self.screen.get_height()
        
        #create variables to simplify checking
        offRight = offLeft = offTop = offBottom = offScreen = False
        
        if self.x > scrWidth:
            offRight = True
        if self.x < 0:
            offLeft = True
        if self.y > scrHeight:
            offBottom = True
        if self.y < 0:
            offTop = True
            
        if offRight or offLeft or offTop or offBottom:
            offScreen = True
        
        if self.boundAction == self.WRAP:
            if offRight:
                self.x = 0
            if offLeft:
                self.x = scrWidth
            if offBottom:
                self.y = 0
            if offTop:
                self.y = scrHeight
        
        elif self.boundAction == self.BOUNCE:
            if offLeft or offRight:
                self.dx *= -1
            if offTop or offBottom:
                self.dy *= -1
                
            self.updateVector()
            self.rotation = self.dir
        
        elif self.boundAction == self.STOP:
            if offScreen:
                self.speed = 0
        
        elif self.boundAction == self.HIDE:
            if offScreen:
                self.speed = 0
                self.setPosition((-1000, -1000))
        
        elif self.boundAction == self.CONTINUE:
            pass
            
        else:
            # assume it's CONTINUE - keep going forever
            pass    
    
    def setSpeed(self, speed):
        """ immediately sets the objects speed to the 
            given value.
        """
        self.speed = speed

    def speedUp(self, amount):
        """ changes speed by the given amount
            Use a negative value to slow down
        """
        self.speed += amount
        if self.speed < self.minSpeed:
            self.speed = self.minSpeed
        if self.speed > self.maxSpeed:
            self.speed = self.maxSpeed
    
    def setAngle(self, dir):
        """ sets both the direction of motion 
            and visual rotation to the given angle
            If you want to set one or the other, 
            set them directly. Angle measured in degrees
        """            
        self.dir = dir
        self.rotation = dir
    
    def turnBy (self, amt):
        """ turn by given number of degrees. Changes
            both motion and visual rotation. Positive is
            counter-clockwise, negative is clockwise 
        """
        self.dir += amt
        if self.dir > 360:
            self.dir = amt
        if self.dir < 0:
            self.dir = 360 - amt
        self.rotation = self.dir
    
    def rotateBy(self, amt):
        """ change visual orientation by given
            number of degrees. Does not change direction
            of travel. 
        """
        self.rotation += amt
        if self.rotation > 360:
            self.rotation = amt
        if self.rotation < 0:
            self.rotation = 360 - amt
    
    def setImage (self, image):
        """ loads the given file name as the master image
            default setting should be facing east.  Image
            will be rotated automatically """
        self.imageMaster = pygame.image.load(gameEngineUtil.DIR_GFX + image)
    
    def setDX(self, dx):
        """ changes dx value and updates vector """
        self.dx = dx
        self.updateVector()
    
    def addDX(self, amt):
        """ adds amt to dx, updates vector """
        self.dx += amt
        self.updateVector()
        
    def setDY(self, dy):
        """ changes dy value and updates vector """
        self.dy = dy
        self.updateVector()

    def addDY(self, amt):
        """ adds amt to dy and updates vector """
        self.dy += amt
        self.updateVector()
    
    def setComponents(self, components):
        """ expects (dx, dy) for components
            change speed and angle according to dx, dy values """
            
        (self.dx, self.dy) = components
        self.updateVector()
        
    def setBoundAction (self, action):
        """ sets action for boundary.  Values are
            self.WRAP (wrap around edge - default)
            self.BOUNCE (bounce off screen changing direction)
            self.STOP (stop at edge of screen)
            self.HIDE (move off-stage and stop)
            self.CONTINUE (move on forever)
            Any other value allows the sprite to move on forever
        """
        self.boundAction = action

    def setPosition (self, position):
        """ place the sprite directly at the given position
            expects an (x, y) tuple
        """
        (self.x, self.y) = position
        
    def moveBy (self, vector):
        """ move the sprite by the (dx, dy) values in vector
            automatically calls checkBounds. Doesn't change 
            speed or angle settings.
        """
        (dx, dy) = vector
        self.x += dx
        self.y += dy
        self.__checkBounds()

    def forward(self, amt):
        """ move amt pixels in the current direction
            of travel
        """
        
        #calculate dx dy based on current direction
        radians = self.dir * math.pi / 180
        dx = amt * math.cos(radians)
        dy = amt * math.sin(radians) * -1
        
        self.x += dx
        self.y += dy
        
    def addForce(self, amt, angle):
        """ apply amt of thrust in angle.
            change speed and dir accordingly
            add a force straight down to simulate gravity
            in rotation direction to simulate spacecraft thrust
            in dir direction to accelerate forward
            at an angle for retro-rockets, etc.
        """

        #calculate dx dy based on angle
        radians = angle * math.pi / 180
        dx = amt * math.cos(radians)
        dy = amt * math.sin(radians) * -1
        
        self.dx += dx
        self.dy += dy
        self.updateVector()
        
    def updateVector(self):
        #calculate new speed and angle based on dx, dy
        #call this any time you change dx or dy
        
        self.speed = math.sqrt((self.dx * self.dx) + (self.dy * self.dy))
        
        dy = self.dy * -1
        dx = self.dx
        
        radians = math.atan2(dy, dx)
        self.dir = radians / math.pi * 180

    def setSpeedLimits(self, max, min):
        """ determines maximum and minimum
            speeds you will allow through
            speedUp() method.  You can still
            directly set any speed you want
            with setSpeed() Default values:
                max: 10
                min: -3
        """
        self.maxSpeed = max
        self.minSpeed = min

    def dataTrace(self):
        """ utility method for debugging
            print major properties
            extend to add your own properties
        """
        print("x: %d, y: %d, speed: %.2f, dir: %.f, dx: %.2f, dy: %.2f" % \
              (self.x, self.y, self.speed, self.dir, self.dx, self.dy))
            
    def mouseDown(self):
        """ boolean function. Returns True if the mouse is 
            clicked over the sprite, False otherwise
        """
        self.pressed = False
        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.pressed = True
        return self.pressed
    
    def clicked(self):
        """ Boolean function. Returns True only if mouse
            is pressed and released over sprite
            
        """
        released = False
        if self.pressed:
            if pygame.mouse.get_pressed() == (0, 0, 0):
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    released = True
            return released
        
    def collidesWith(self, target):
        """ boolean function. Returns True if the sprite
            is currently colliding with the target sprite,
            False otherwise
        """
        collision = False
        if self.rect.colliderect(target.rect):
            collision = True
        return collision
    
    def collidesGroup(self, target):
        """ wrapper for pygame.sprite.spritecollideany() function
            simplifies checking sprite - group collisions
            returns result of collision check (sprite from group 
            that was hit or None)
        """
        collision = pygame.sprite.spritecollideany(self, target)
        return collision
        
    def distanceTo(self, point):
        """ returns distance to any point in pixels
            can be used in circular collision detection
        """
        (pointx, pointy) = point
        dx = self.x - pointx
        dy = self.y - pointy
        
        dist = math.sqrt((dx * dx) + (dy * dy))
        return dist
    
    def dirTo(self, point):
        """ returns direction (in degrees) to 
            a point """
        
        (pointx, pointy) = point
        dx = self.x - pointx
        dy = self.y - pointy
        dy *= -1
        
        radians = math.atan2(dy, dx)
        dir = radians * 180 / math.pi
        dir += 180
        return dir
    
    def drawTrace(self, color=(0x00, 0x00, 0x00)):
        """ traces a line between previous position
            and current position of object 
        """
        pygame.draw.line(self.scene.background, color, self.oldCenter,
                         self.rect.center, 3)
        self.screen.blit(self.scene.background, (0, 0))
    
    
    
""" ------------------------------------------------------------------------------------------------------------------------ """

""" Scene 
    
    Use this object creates a new python window in full screen mode and
    is used as a place to add group and sprites objects. Each scene
    has a physics engine which drives all group and sprite objects in their
    update functions.
    """
class Scene(object):  
    STOP_ANY_KEY = 0
    STOP_ESC = 1
    STOP_NEVER = -1
    #Constructor for our scene object. Takes in width and height parameters which is
    #used for our display screen.  
    def __init__(self, (width, height), title):
        #Initialize pygame and the screen in full screen mode with an black background.
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((0,0,0))
        self.setCaption(title)
        #Create our physics engine
        self.physics = Physics()
        
        #Create our sprites and group lists.
        #Also initialize any other variables.
        self.sprites = []
        self.groups = []
        self.topLayerGroup = []
        self.exit = False
        self.keepGoing = True
        self.stopBound = self.STOP_ANY_KEY
        
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        
    #Sets the scene on how it should stop. This bound is automatically handled in doEvents.
    def setStopBounds(self, bound):
        self.stopBound = bound
        
    #Start the scene.
    def start(self):
        self.__mainLoop()

    #Stop our scene by getting out of the main loop.
    def stop(self):
        self.keepGoing = False
        
    #Terminate our window complete by setting the exit flag to true.
    #The exit flag by self does nothing but outside callers can use
    #this flag to indicate when to terminate the whole program.
    def terminate(self):
        self.exit = True
        self.stop()
        
    #The main loop which executes the scene. The loop updates and renders the game and
    #calls doEvents automatically.
    def __mainLoop(self):
        
        while self.keepGoing:
            keys = pygame.key.get_pressed()
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    self.terminate()
                self.doEvents(event)
                for group in self.groups:
                    for sprite in group.sprites():
                        sprite.doEvents(event)
                    
            self.update()
            for group in self.groups:
                group.update()
                group.clear(self.screen, self.background)
                group.draw(self.screen)
            for group in self.topLayerGroup:
                group.update()
                group.clear(self.screen, self.background)
                group.draw(self.screen) 
            pygame.display.flip()
            
    #Adds group to the scene. All groups will be updated and drawn in the main loop.
    def addGroup(self, group):
        self.groups.append(group)

    def addTopLayerGroup(self, group):
        self.topLayerGroup.append(group)
        
    #Processes any events issued and detected. It is automatically called in
    #the main loop.
    def doEvents(self, event):
        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            if self.stopBound == self.STOP_ANY_KEY:
                self.stop()
            if self.stopBound == self.STOP_ESC and keys[pygame.K_ESCAPE]:
                self.stop()
        
    #Updates the scene. Is called automatically in the main loop.
    def update(self):
        pass
    
    #Changes the caption of the scene window. Must be used before the start()
    #method otherwise it will not be taken into effect.
    def setCaption(self, title):
        pygame.display.set_caption(title)


                    