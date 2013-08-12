"""
    Author's name: Justin Hellsten
    Last Modified by: Justin Hellsten
    Date last Modified: Mon, August 5
    Program description:
                 Tile based side scroller where the player controlls a character called Ritz.
                 Collect coins and shoot various enemies in a platform tile side scroller.
                 
    Revision 0.1.0
        -> Window set to 800 by 600
        -> Window caption set to "Level Maker - Ritz"
        -> Added key handling function
        -> Added render handling function
        -> Render draws seperatation lines
        -> Added tile map class to store tiles
        -> Tile Map size can be set
        -> Can now add tiles or remove tiles from class
        -> Tile map re renders itself when updating 
        -> Added draw bar class which loads and holds the tile images
        -> Render tile images onto draw bar image
        -> Draw bar image renders on screen
        -> Map scrolls can now scroll. To scroll you use a combination of the mouse position and keyboard keys.
          (W A S D)
        -> TileMap reads tile images from draw bar. 
        -> Tilemap draws tile image based on tile values in the map.
        -> There is now boundary checking when scrolling the tile map.
        -> Added selected tile function to draw bar
        -> Draw bar now shows selected tile (green rectangle)
        -> Shifted rendering of sections to fit for a tile size of 16
        -> Added functionality to tile map to add tile based on selection in draw map,
           and location of click on the tile map area.
        -> Fixed bug with grid where it becomes offset from tile size when reaching boundaries whic
           do not divid evenly with the tile size
        -> Added delete feature for tile map (removes tile on right click)
        
"""

import pygame.gfxdraw

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
        for row in range(size[0]):
            self.tiles.append([])
            for column in range(size[1]):
                self.tiles[row].append(-1)
            
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
                if tileValue != -1:
                    self.image.blit(tileImages[tileValue], (-self.scrollx + column * self.tilesize, 
                                                            -self.scrolly + row * self.tilesize))
    
        #Draw lines
        for x in range(0, self.size[0]):
            pygame.gfxdraw.vline(self.image, x * self.tilesize + self.scrollx % self.tilesize, 0, 600, (0,0,0))
        for y in range(0, self.size[1]):
            pygame.gfxdraw.hline(self.image, 0, 600, y * self.tilesize + self.scrolly % self.tilesize, (0,0,0))
            
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
        self.tiles[y][x] = value
        self.__redraw()
        
    def deleteTile(self, x, y):
        self.tiles[y][x] = -1
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
        self.setTile(xindex, yindex, self.drawBar.getSelectedTile())
    
    def removeTile(self, coordx, coordy):
        xindex = coordx / self.tilesize + (self.scrollx / self.tilesize)
        yindex = coordy / self.tilesize + (self.scrolly / self.tilesize)
        self.deleteTile(xindex, yindex)
        
    def __checkInput(self):
        keys = pygame.key.get_pressed()
        mousePos = pygame.mouse.get_pos()
        mousePressed = pygame.mouse.get_pressed()
        if mousePos[0] > 0 and mousePos[0] < self.rect.right and \
           mousePos[1] > 0 and mousePos[1] < self.rect.bottom:
            if keys[pygame.K_w]:
                self.changeScrollPosition(0, -self.tilesize)
            if keys[pygame.K_s]:
                self.changeScrollPosition(0, self.tilesize)
            if keys[pygame.K_a]:
                self.changeScrollPosition(-self.tilesize, 0)
            if keys[pygame.K_d]:
                self.changeScrollPosition(self.tilesize, 0)
            #Handle mouse press. Draws tile at the location of mouse press
            if mousePressed[0]:
                self.drawTile(mousePos[0] - self.rect.left, mousePos[1] - self.rect.top)
            if mousePressed[2]:
                self.removeTile(mousePos[0] - self.rect.left, mousePos[1] - self.rect.top)
                
    def update(self):
        self.__checkInput()
    
def __render(screen):
    pygame.gfxdraw.vline(screen, 608, 0, 600, (255,255,255))
    
    
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

            drawGroup.update()

            drawGroup.draw(screen)
            __render(screen)
            
            pygame.display.flip()
    
if __name__ == "__main__": main()

