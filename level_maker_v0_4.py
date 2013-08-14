"""
    Author's name: Justin Hellsten
    Last Modified by: Justin Hellsten
    Date last Modified: Mon, August 5
    Program description:
                 Tile based side scroller where the player controlls a character called Ritz.
                 Collect coins and shoot various enemies in a platform tile side scroller.
                 
    Revision 0.4.0
        
    -> Added spike tile
    
        
"""

import pygame, pygame.gfxdraw, copy

class DrawBar(pygame.sprite.Sprite):
    NUM_OF_TILES = 20
    TILES_PER_ROW = 12
    def __init__(self, surface, tilesize = 16):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((192, 600), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = 608
        self.rect.y = 0
        self.tilesize = tilesize
        
        self.tileSelection = 0
        
        self.__loadImages()
        self.__render()
        
    def getSelectedTile(self):
        return self.tileSelection

    def __selectTile(self, coordx, coordy):
        self.tileSelection = (coordx / self.tilesize) + (coordy / self.tilesize) * self.TILES_PER_ROW
        self.__render()
        
    def __loadImages(self):
        self.tileImages = []
        for x in range(self.NUM_OF_TILES):
            self.tileImages.append(pygame.image.load("gfx/tiles/{0}.png".format(x)))
      
    def __render(self):
        self.image.fill((20,20,20))
        for tileIndex in range(0,self.NUM_OF_TILES):
            x = (tileIndex % self.TILES_PER_ROW) * self.tilesize
            y = tileIndex / self.TILES_PER_ROW * self.tilesize
            self.image.blit(self.tileImages[tileIndex], (x, y))
        selectx = (self.tileSelection % self.TILES_PER_ROW) * self.tilesize
        selecty = self.tileSelection / self.TILES_PER_ROW * self.tilesize
        pygame.gfxdraw.rectangle(self.image, 
                                 pygame.rect.Rect((selectx,selecty),(self.tilesize, self.tilesize)), 
                                 (0,255,0))
        
    def __checkInput(self):
        mousePos = pygame.mouse.get_pos()
        mousePressed = pygame.mouse.get_pressed()
        if mousePos[0] > self.rect.left and mousePos[0] < self.rect.right and \
           mousePos[1] > self.rect.top and mousePos[1] < self.rect.bottom:
            if mousePressed[0]:
                self.__selectTile(mousePos[0] - self.rect.left, mousePos[1] - self.rect.top)
            

    def update(self):
        self.__checkInput()
        
        
class TileMap(pygame.sprite.Sprite):
    def __init__(self, surface, drawBar):
        pygame.sprite.Sprite.__init__(self)
        self.drawBar = drawBar
        self.surface = surface
        self.scrollx = 0
        self.scrolly = 0
        self.tiles = []
        self.currentTilePosition = (0, 0)
        self.currentTileValue = 0
        
        self.entityInfo = []
        self.entities = []
        
        self.ritzImage = pygame.image.load("gfx/ritz/idle0.png")
        
            
        self.image = pygame.surface.Surface((self.surface.get_width(), self.surface.get_height()), 
                                            pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.__loadEntityConfiguration()
        self.resetFlags()
        self.reset()
        
    def __loadEntityConfiguration(self):
        f = open("level_maker.cfg", "r")
        for line in f.readlines():
            line = line.strip()
            tokens = line.split(",")
            self.entityInfo.append([tokens[0], tokens[1], pygame.image.load(tokens[2])])
            
        f.close()
        
    def __redraw(self):
        tileImages = self.drawBar.tileImages
        self.image.fill((20, 20, 20))
        for row in range(0, self.size[1]):
            for column in range(0, self.size[0]):
                tileValue = self.tiles[row][column]
                if tileValue != 0:
                    self.image.blit(tileImages[tileValue - 1], (-self.scrollx + column * self.tilesize, 
                                                            -self.scrolly + row * self.tilesize))
    
        #Draw Grid
        if self.gridOn:
            for x in range(0, self.size[0]):
                pygame.gfxdraw.vline(self.image, x * self.tilesize + self.scrollx % self.tilesize, 0, 600, (0,0,0))
            for y in range(0, self.size[1]):
                pygame.gfxdraw.hline(self.image, 0, 608, y * self.tilesize + self.scrolly % self.tilesize, (0,0,0))
                
        #Draw start location (Ritz)
        ritzRect = self.ritzImage.get_rect()
        ritzWidth = ritzRect.width
        ritzHeight = ritzRect.height
        self.image.blit(self.ritzImage, (-self.scrollx + self.startLocation[0] - ritzWidth / 2, 
                                         -self.scrolly + self.startLocation[1] - ritzHeight / 2))
        
        #Draw entities
        for entity in self.entities:
            for info in self.entityInfo:
                if info[0] == entity[0]:
                    entityWidth = info[2].get_width()
                    entityHeight = info[2].get_height()
                    self.image.blit(info[2], (-self.scrollx + entity[1] - entityWidth / 2, 
                                              -self.scrolly + entity[2] - entityHeight / 2) )
            
    def __setSize(self):
        originalSize = len(self.tiles)
        if originalSize < self.size:
            for column in range(0, originalSize):
                self.tiles[column].extend([-1]*(self.size - originalSize))
                self.tiles.extend([[-1]*self.size]*(self.size - originalSize))
        elif originalSize > self.size:
            self.tiles = self.tiles[0:self.size]
            for column in range(0, self.size):
                self.tiles[column] = self.tiles[column][0:self.size]
                
    def setTile(self, x, y, value):
        #Set tile information
        self.currentTilePosition = (x, y)
        self.currentTileValue = copy.deepcopy(self.tiles[y][x])
                
        self.tiles[y][x] = value
        self.__redraw()
        self.clearMap = False
        self.addTile = True
        self.deletedTile = False
        self.loadingFile = False

    def deleteTile(self, x, y):
        #Set tile information
        self.currentTilePosition = (x, y)
        self.currentTileValue = copy.deepcopy(self.tiles[y][x])
                
        self.tiles[y][x] = 0
        self.__redraw()
        self.clearMap = False
        self.deletedTile = True
        self.addTile = False
        self.loadingFile = False

    def clear(self):
        for rowIndex, item in enumerate(self.tiles): 
            for column in enumerate(item):
                self.tiles[rowIndex][column[0]] = 0 
                
        self.clearMap = True
        self.addTile = False
        self.deletedTile = False
        self.loadingFile = False
        self.__redraw()
        
    def changeSize(self, size):
        self.size = size
        self.__setSize()
        self.__redraw()
        
    def getMapSize(self):
        return (len(self.tiles[0]) * self.tilesize, len(self.tiles) * self.tilesize)
    
    def changeScrollPosition(self, scrollx, scrolly):
        mapSize = self.getMapSize()
        self.scrollx += scrollx
        self.scrolly += scrolly
        if self.scrollx < 0:
            self.scrollx = 0
        elif self.scrollx > mapSize[0] - self.surface.get_width():
            self.scrollx = mapSize[0] - self.surface.get_width()
        if self.scrolly < 0:
            self.scrolly = 0
        elif self.scrolly > mapSize[1] - self.surface.get_height():
            self.scrolly = mapSize[1] - self.surface.get_height()
        self.__redraw()
        
    def drawTile(self, coordx, coordy):
        xindex = coordx / self.tilesize + (self.scrollx / self.tilesize)
        yindex = coordy / self.tilesize + (self.scrolly / self.tilesize)
        self.setTile(xindex, yindex, self.drawBar.getSelectedTile() + 1)
    
    def removeTile(self, coordx, coordy):
        xindex = coordx / self.tilesize + (self.scrollx / self.tilesize)
        yindex = coordy / self.tilesize + (self.scrolly / self.tilesize)
        self.deleteTile(xindex, yindex)
        
    def setStartLocation(self, x, y):
        self.startLocation = (x, y)
        self.__redraw()
        
    #Loads the tile map from level.dat
    def loadFromFile(self):
        f = open("level.dat", "r")
        reading = ""
        tokensArray = []
        for line in f.readlines():
            line = line.strip()
            
                                
            if line == "[tokens]" or line == "[size]" or line == "[imgs]" or \
            line == "[imgdir]" or line == "[startlocation]" or line == "[entities]":
                reading = line
            elif reading == "[tokens]":
                tokens = line.split(",")
                tokensArray.append([])
                for index in range(0, len(tokens)):
                    tokensArray[len(tokensArray) - 1].append(int(tokens[index]))
            elif reading == "[size]":
                self.tilesize = int(line)
            elif reading == "[startlocation]":
                slToken = line.split(",")
                self.startLocation = (int(slToken[0]), int(slToken[1]))
            elif reading == "[entities]":
                entityTokens = line.split(",")    
                self.entities.append([entityTokens[0], int(entityTokens[1]), int(entityTokens[2])])
        
        self.tiles = tokensArray
        self.size = (len(self.tiles[0]), len(self.tiles))
        self.loadingFile = True
        self.__redraw()
                    
    #Saves the tile map to a file called level.dat
    def saveToFile(self):
        self.deletedTile = False
        self.addTile = False
        self.loadingFile = False
        
        f = open("level.dat", "w")
        f.write("[tokens]\n")
        for row in self.tiles:
            rowTokens = ""
            for tileValue in row:
                rowTokens = rowTokens + str(tileValue) + ','

            rowTokens = rowTokens[0:(len(rowTokens)-1)] + "\n"
            
            f.write(rowTokens)
            
        f.write("[size]\n")
        f.write(str(self.tilesize) + "\n")
        f.write("[imgs]\n")
        f.write("transparent.png" + "\n") 
        for i in range(0, DrawBar.NUM_OF_TILES):
            f.write(str(i) + ".png" + "\n") 
        f.write("[imgdir]\ntiles/\n")
        f.write("[startlocation]\n")
        f.write(str(self.startLocation[0]) + "," + str(self.startLocation[1]) + "\n")
        f.write("[entities]\n")
        for entity in self.entities:
            f.write(entity[0] + "," + str(entity[1]) + "," + str(entity[2]) + "\n")
        
    def setGrid(self, flag):
        self.gridOn = flag
        self.__redraw()
        
    def resetFlags(self):
        self.savingFile = False
        self.clearMap = False
        self.deletedTile = False
        self.addTile = False
        self.scrollVertically = False
        self.loadingFile = False
        self.gridOn = True
        self.newMap = False
        
    def reset(self):
        self.size = (50, 50)
        self.tilesize = 16
        self.tiles = []
        for row in range(self.size[0]):
            self.tiles.append([])
            columnCount = 0
            while columnCount != self.size[1]:
                columnCount += 1
                self.tiles[row].append(0)
        (mapWidth, mapHeight) = self.getMapSize()
        self.startLocation = (mapWidth / 2, mapHeight / 2)
        self.__redraw()
         
    def collidesWithEntity(self, (left, top), (width, height), remove = False):      
        for index, entity in enumerate(self.entities):
            for info in self.entityInfo:
                if entity[0] == info[0]:
                    entityWidthHalf = info[2].get_width() / 2
                    entityHeightHalf = info[2].get_height() / 2
                    if left + width > entity[1] - entityWidthHalf and left < entity[1] + entityWidthHalf and \
                    top + height > entity[2] - entityHeightHalf and top < entity[2] + entityHeightHalf:
                        self.originalEntity = self.entities[index]
                        if remove:
                            self.entities.pop(index)
                            self.__redraw()
                            
                        return self.originalEntity
                                    
    def doEvents(self, event):
        keys = pygame.key.get_pressed()
        mousePos = pygame.mouse.get_pos()
        if mousePos[0] > 0 and mousePos[0] < self.rect.right and \
           mousePos[1] > 0 and mousePos[1] < self.rect.bottom:        
            #Check mouse wheel scroll
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.dict['button'] == 4:
                    if self.scrollVertically:
                        self.changeScrollPosition(0, -self.tilesize)
                    else:
                        self.changeScrollPosition(-self.tilesize, 0)
                elif event.dict['button'] == 5:
                    if self.scrollVertically:
                        self.changeScrollPosition(0, self.tilesize)
                    else:
                        self.changeScrollPosition(self.tilesize, 0)
                
                #Check on right click
                if event.dict['button'] == 3:
                    self.collidesWithEntity((self.scrollx + mousePos[0] - self.rect.left, 
                                             self.scrolly + mousePos[1] - self.rect.top), 
                                            (0, 0), True)
                                    
                                    
                                    
            #Check key hit wonders
            if event.type == pygame.KEYDOWN:
            
                #Check ctrl function wonders
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    #Create a new map 
                    if keys[pygame.K_n]:
                        self.reset()
                    #Clear all tiles in map
                    if keys[pygame.K_c]:
                        self.clear()

                #Check alt function wonders.
                #These are assocciated with entity creations
                elif keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                    for info in self.entityInfo:
                        if info[1] == pygame.key.name(pygame.K_g) and keys[pygame.K_g]:
                            self.entities.append([info[0], self.scrollx + mousePos[0] - self.rect.left, 
                                                  self.scrolly + mousePos[1] - self.rect.top])
                            self.__redraw()
                        if info[1] == pygame.key.name(pygame.K_s) and keys[pygame.K_s]:
                            self.entities.append([info[0], self.scrollx + mousePos[0] - self.rect.left, 
                                                  self.scrolly + mousePos[1] - self.rect.top])
                            self.__redraw()
                        if info[1] == pygame.key.name(pygame.K_c) and keys[pygame.K_c]:
                            self.entities.append([info[0], self.scrollx + mousePos[0] - self.rect.left, 
                                                  self.scrolly + mousePos[1] - self.rect.top])
                            self.__redraw()
                                                        
                else:          
                    #Toggle grid visibility
                    if keys[pygame.K_g]:
                        self.setGrid(not self.gridOn)
                            
    def __checkInput(self):
        keys = pygame.key.get_pressed()
        mousePos = pygame.mouse.get_pos()
        mousePressed = pygame.mouse.get_pressed()
        
        if mousePos[0] > 0 and mousePos[0] < self.rect.right and \
           mousePos[1] > 0 and mousePos[1] < self.rect.bottom:
            if keys[pygame.K_UP]:
                self.changeScrollPosition(0, -self.tilesize)
            if keys[pygame.K_DOWN]:
                self.changeScrollPosition(0, self.tilesize)
            if keys[pygame.K_LEFT]:
                self.changeScrollPosition(-self.tilesize, 0)
            if keys[pygame.K_RIGHT]:
                self.changeScrollPosition(self.tilesize, 0)
            #Handle mouse press. Draws tile at the location of mouse press
            if mousePressed[0]:
                self.drawTile(mousePos[0] - self.rect.left, mousePos[1] - self.rect.top)
            if mousePressed[2]:
                self.removeTile(mousePos[0] - self.rect.left, mousePos[1] - self.rect.top)
            
 
            #User is pressing ctrl
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                self.scrollVertically = False
                #Checks if user is going to more advance functions (alt)
                if keys[pygame.K_LALT] or keys[pygame.K_RALT]:                    
                    pass
                
                    
                #Check if user is added start location
                if keys[pygame.K_r]:
                    self.setStartLocation(self.scrollx + mousePos[0] - self.rect.left, 
                                          self.scrolly + mousePos[1] - self.rect.top)
                    
                    
                #Check is user is trying to load from level.dat
                if keys[pygame.K_l]:
                    self.loadFromFile()
                else:
                    self.loadingFile = False
                    
                #Check if user is trying to save the tile map to a file (ctrl + s)
                #Make sure user can't just hold don't ctrl + s
                if keys[pygame.K_s] and not self.savingFile:
                    self.savingFile = True
                    self.saveToFile()
                elif not keys[pygame.K_s]:
                    self.savingFile = False
            else:
                self.savingFile = False    
                self.scrollVertically = True
                self.loadingFile = False
                
    def update(self):
        self.__checkInput()
    
def __render(screen, tileMap):
    screenWidth = screen.get_width()
    screenHeight = screen.get_height()
    
    pygame.gfxdraw.vline(screen, 608, 0, 600, (255,255,255))
    
    #If tile map is drawing tell the user we are drawing
    font = pygame.font.SysFont("None", 16)
    if tileMap.savingFile:
        screen.blit(font.render("File has been saved!", 1, (255, 255, 255)), 
                    (screenWidth - 150, screenHeight - 50))

    if tileMap.addTile:
        screen.blit(font.render("Tile has been added!", 1, (255, 255, 255)), 
                    (screenWidth - 150, screenHeight - 50))
    if tileMap.deletedTile:
        screen.blit(font.render("Tile has been deleted!", 1, (255, 255, 255)), 
                    (screenWidth - 150, screenHeight - 50))
    if tileMap.loadingFile:
        screen.blit(font.render("File has been loaded!", 1, (255, 255, 255)), 
                    (screenWidth - 150, screenHeight - 50))
            
    #Display tile information
    screen.blit(font.render("Tile: ({0},{1}) Value: {2}".format(tileMap.currentTilePosition[0], tileMap.currentTilePosition[1], tileMap.currentTileValue), 
                            1, (255, 255, 255)), (screenWidth - 180, screenHeight - 20))
    
                    
def main():
    pygame.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Level Maker - Ritz")
    background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    tileArea = pygame.Surface((608, 600), pygame.SRCALPHA)
    screen.blit(background, (0, 0))
    keepGoing = True
    clock = pygame.time.Clock()
    
    drawBar = DrawBar(screen)
    tileMap = TileMap(tileArea, drawBar)
    
    drawGroup = pygame.sprite.Group(drawBar, tileMap)
    
    
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            tileMap.doEvents(event)
                
            drawGroup.update()

            drawGroup.draw(screen)
            __render(screen, tileMap)
            
            pygame.display.flip()
    
if __name__ == "__main__": main()

