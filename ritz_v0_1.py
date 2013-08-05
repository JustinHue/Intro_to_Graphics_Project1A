"""
    Author: Justin Hellsten
    Date: August 2nd
    Last Modified By: Justin Hellsten
    Description: Tile based side scroller where the player controlls
                 a character called Ritz.
                 
    Version: 
        0.1 -> Added TileMap class to game engine
            -> Created Ritz sprite
            -> Added collision code for walls and tiles for tile map (not perfect)
            -> Added physics (gravity) to all My Sprite objects
            -> Added My Sprite object to game engine
            
"""
import pygame, gameEngine

""" Our hero avatar sprite """
class Ritz(gameEngine.MySprite):
    def __init__(self, scene):
        gameEngine.MySprite.__init__(self, "ritz_body.png")
        self.maxSpeed = 10
        self.minSpeed = 0
        self.jump = False
        
    def update(self):
        gameEngine.MySprite.update(self)
        
        self.setDX(0)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.setDX(-5)
        if keys[pygame.K_d]: 
            self.setDX(5)
   
   
        
      
             
class GamePlayScene(gameEngine.Scene):
    def __init__(self, (width, height)):
        gameEngine.Scene.__init__(self, (width, height))
        
        #Load level one
        self.l1MapSprite = gameEngine.TileMap(self, "level1.dat")
        
        self.ritzSprite = Ritz(self)
        self.ritzSprite.setPhysics(self.physics) 
        self.l1MapSprite.addSprite(self.ritzSprite)



        l1MapSpriteGroup = pygame.sprite.Group(self.l1MapSprite)
        l1BackgroundSprite = gameEngine.SuperSprite(self)
        l1BackgroundSprite.setImage("dark_background_line_surface_65896_1920x1200.jpg")
        l1BackgroundGroup = pygame.sprite.Group(l1BackgroundSprite)

        # Add level one sprites/groups
        self.addGroup(l1BackgroundGroup) 
        self.addGroup(l1MapSpriteGroup)
        
        self.currentLevel =  self.l1MapSprite
        
    def update(self):
        gameEngine.Scene.update(self)
        
        screenWidth = self.screen.get_width()
        screenHeight = self.screen.get_height()
        

        # Scroll map based on Ritz position
        self.currentLevel.setScrollPosition(self.ritzSprite.rect.x - screenWidth / 2, 
                                              self.ritzSprite.rect.y - screenHeight / 2)

            
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
    
