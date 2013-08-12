"""
    Author's name: Justin Hellsten
    Last Modified by: Justin Hellsten
    Date last Modified: Mon, August 5
    Program description:
                 Tile based side scroller where the player controlls a character called Ritz.
                 Collect coins and shoot various enemies in a platform tile side scroller.
                 
    Revision 0.2.0
        -> Added save feature (ctrl + s)
        -> Fixed grid render for the horizontal grid lines
        -> Change W A S D to arrow keys
        -> Fixed set tile callers to add + 1 to value of tile
        -> Added [size] attribute to file
        -> Added [imgs] attribute to file
        -> Added [imgdir] attribute to file
        -> Added functionality to place ritz location on the tile map (ctrl + r)
        -> Saving file message is now displayed when saving. It will disappear when user lets go of 
           ctrl + s
        -> Added functionality to clear tile map with (ctrl + alt + c)
        -> Added clear, add delete flags in tile map.
        -> Messages now occur for clear, add and delete flags
        -> Tile information hovered by mouse is now in message area
        -> Imported copy module to fix bug where variable value would not be assigned by value referenced
           in a list. (did not fix. look at later)
        -> Added feature to allow scrolling the map vertically with the mouse
        -> Added feature to scroll horizontally (hold ctrl)
        -> Scroll feature can only be activated while hovering over tile area
        -> Added [startlocation] attribute to tile
        -> Draw Ritz image where start location is
        -> Fixed issue with startlocation attribute not being read properly
        
"""

import pygame.gfxdraw, copy

pygame.init()

class DrawBar(pygame.sprite.Sprite):
    NUM_OF_TILES = 19
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
        self.image.fill((10,10,10))
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
    def __init__(self, surface, drawBar, size = (64, 64), tilesize = 16):
        pygame.sprite.Sprite.__init__(self)
        self.drawBar = drawBar
        self.surface = surface
        self.size = size
        self.tilesize = tilesize        
        self.scrollx = 0
        self.scrolly = 0
        self.tiles = []
        self.currentTilePosition = (0, 0)
        self.currentTileValue = 0
        self.savingFile = False
        self.clearMap = False
        self.deletedTile = False
        self.addTile = False
        self.scrollVertically = False
        
        self.startLocation = (surface.get_width() / 2, surface.get_height() / 2)
        self.ritzImage = pygame.image.load("gfx/ritz/idle0.png")
        
        for row in range(size[0]):
            self.tiles.append([])
            for column in range(size[1]):
                self.tiles[row].append(0)
            
        self.image = pygame.surface.Surface((self.surface.get_width(), self.surface.get_height()), 
                                            pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.__redraw()
        
    def __redraw(self):
        tileImages = self.drawBar.tileImages
        self.image.fill((10, 10, 10))
        for row in range(0, self.size[0]):
            for column in range(0, self.size[1]):
                tileValue = self.tiles[row][column]
                if tileValue != 0:
                    self.image.blit(tileImages[tileValue - 1], (-self.scrollx + column * self.tilesize, 
                                                            -self.scrolly + row * self.tilesize))
    
        #Draw lines
        for x in range(0, self.size[0]):
            pygame.gfxdraw.vline(self.image, x * self.tilesize + self.scrollx % self.tilesize, 0, 600, (0,0,0))
        for y in range(0, self.size[1]):
            pygame.gfxdraw.hline(self.image, 0, 608, y * self.tilesize + self.scrolly % self.tilesize, (0,0,0))
            
        #Draw start location (Ritz)
        self.image.blit(self.ritzImage, (-self.scrollx + self.startLocation[0], 
                                         -self.scrolly + self.startLocation[1]))
        
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
        

    def deleteTile(self, x, y):
        #Set tile information
        self.currentTilePosition = (x, y)
        self.currentTileValue = copy.deepcopy(self.tiles[y][x])
                
        self.tiles[y][x] = 0
        self.__redraw()
        self.clearMap = False
        self.deletedTile = True
        self.addTile = False
        

    def clear(self):
        for rowIndex, item in enumerate(self.tiles): 
            for column in enumerate(item):
                self.tiles[rowIndex][column[0]] = 0 
                
        self.clearMap = True
        self.addTile = False
        self.deletedTile = False
        self.__redraw()
        
    def changeSize(self, size):
        self.size = size
        self.__setSize()
        self.__redraw()
        
    def getMapSize(self):
        return (len(self.tiles) * self.tilesize, len(self.tiles[0]) * self.tilesize)
    
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
        
    #Saves the tile map to a file called level.dat
    def saveToFile(self):
        self.deletedTile = False
        self.addTile = False
        
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
        f.write(str(self.startLocation[0]) + "," + str(self.startLocation[1]))
        
        
    def doEvents(self, event):
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
                    #Clear all tiles in map
                    if keys[pygame.K_c]:
                        self.clear()
                    
                #Check if user is added start location
                if keys[pygame.K_r]:
                    self.setStartLocation(self.scrollx + mousePos[0] - self.rect.left, 
                                          self.scrolly + mousePos[1] - self.rect.top)
                    
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
    
    #Display tile information
    screen.blit(font.render("Tile: ({0},{1}) Value: {2}".format(tileMap.currentTilePosition[0], tileMap.currentTilePosition[1], tileMap.currentTileValue), 
                            1, (255, 255, 255)), (screenWidth - 180, screenHeight - 20))
    
                    
def main():
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

