"""
    Author's name: Justin Hellsten
    Last Modified by: Justin Hellsten
    Date last Modified: Sun, August 11
    Program description:
                 Tile based side scroller where the player controlls a character called Ritz.
                 Collect coins and shoot various enemies in a platform tile side scroller.
                 
    Revision History: 1.0.0

    -> Moved goomba and shy guy enemies to enemies module.
    -> Moved coin and door to miscellaneous module.
    -> Added My Basic Sprite class in game engine. This is the provides the very basic for sprites.
       Sets the image, rect and center of rect and scene
    -> Added instructions button sprite.
    -> SquareButtonSprite buttons (w, a, s, d) have been added and rectangle button sprite (SPACE).
    -> Text is now along side and explains buttons
    -> Place text strings in resources module
    -> Change font sprite too be multi line compatible. 
    -> Fixed issue where ritz bullet would not fire
    -> moved death music to sound effect
    -> Ritz tile map no longer plays music, must be run in scene
    -> Instructions scene no longer plays music
    -> Play music function parameters have default values, can adjust the volume for music
    -> reduce sound volume to one third way for now
    -> Added static groups to tile map
    -> Added instructions door entity in miscellaneous
    -> Added 3 levels, first level now change to fourth level
    -> Fixed issue where instruction images were drawing over ritz
    -> Fixed glitch where you couldn't go through doors when your avatar dies
    -> Added level base class
    -> Added top layer group for scene
    -> Added sub class ritz level and ritz map
        ritz map inherits ritztilemap, ritz level inherits ritz map
    -> Moved ritz objects to ritz object module
    -> Added game over end screen (tile map)
    -> Game over scene shows score and there is a grave stone sprite
    
"""
import pygame, gameEngine, random, ritzObjects
import enemies, graphics, miscellaneous
import resources

""" Scene Constants """
SCENE_SPLASH = 0
SCENE_INSTRUCTIONS = 1
SCENE_START = 2
SCENE_PLAY = 3
SCENE_GAME_OVER = 4
SCENE_CREDITS = 5

    
class GameOver(ritzObjects.RitzTileMap):
    def __init__(self, scene, datafile): 
        ritzObjects.RitzTileMap.__init__(self, scene, datafile, True)
        
    def update(self):
        ritzObjects.RitzTileMap.update(self)
    


class LevelOne(ritzObjects.RitzLevel):
   
    def __init__(self, scene): 
        ritzObjects.RitzLevel.__init__(self, scene, "level1.dat")
        resources.playMusic(resources.MFX_LEVEL_ONE_THEME, -1, 0.3)

class LevelTwo(ritzObjects.RitzLevel):
   
    def __init__(self, scene): 
        ritzObjects.RitzLevel.__init__(self, scene, "level2.dat")
        resources.playMusic(resources.MFX_LEVEL_ONE_THEME, -1, 0.3)
        
class LevelThree(ritzObjects.RitzLevel):
   
    def __init__(self, scene): 
        ritzObjects.RitzLevel.__init__(self, scene, "level3.dat")
        resources.playMusic(resources.MFX_LEVEL_ONE_THEME, -1, 0.3)
                
class LevelFour(ritzObjects.RitzLevel):
 
    def __init__(self, scene): 
        ritzObjects.RitzLevel.__init__(self, scene, "level4.dat")
        resources.playMusic(resources.MFX_LEVEL_ONE_THEME, -1, 0.3)
  

class GamePlayScene(gameEngine.Scene):
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
          
        """
            Misc. Init
        """
        self.setStopBounds(self.STOP_NEVER)
        
        """
            Load Levels
        """
        self.levelCount = 0
        self.currentLevel = LevelOne(self)
        self.ritzTileMapGroup = pygame.sprite.Group(self.currentLevel)
        self.addGroup(self.ritzTileMapGroup)
  
    def nextLevel(self): 
        
        self.runningScore = self.currentLevel.scoreBoard.getScore()
        for sprite in self.currentLevel.topLayerGroup:
            sprite.kill()
        self.ritzTileMapGroup.remove(self.currentLevel)

        self.levelCount += 1
        
        if self.levelCount == 2:
            self.currentLevel = LevelTwo(self)
        elif self.levelCount == 3:
            self.currentLevel = LevelThree(self)
        elif self.levelCount == 4:
            self.currentLevel = LevelFour(self)
        self.currentLevel.scoreBoard.addScore(self.runningScore)
        self.ritzTileMapGroup.add(self.currentLevel)

        
class CreditScene(gameEngine.Scene):
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        
class GameOverScene(gameEngine.Scene):
    def __init__(self, (width, height), title, gameScore = 0):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.gameOverMap = GameOver(self, "gameover.dat")
        self.gameScore = gameScore
        """
            Misc. Init
        """         
        self.setStopBounds(self.STOP_ANY_KEY)
        resources.playMusic(resources.MFX_GAME_OVER, -1, 0.5)

        self.graveStoneSprite = miscellaneous.GraveStone((400, 470))
        self.gameOverText = gameEngine.MyFontSprite(self, (self.width / 2, 50), (200, 50), 
                                                    resources.GAME_OVER_TEXT, 40, (200, 25, 25))
        self.gameScore = gameEngine.MyFontSprite(self, (self.width / 2 - 200, self.height / 2), (200, 25),
                                                        ("Score: {0}".format(self.gameScore), ""), 24, (200, 200, 200))
        self.backgroundGroup = pygame.sprite.Group(self.gameScore, self.gameOverText, 
                                                   self.graveStoneSprite, self.gameOverMap)
        
        self.addGroup(self.backgroundGroup)
            
    
class StartScene(gameEngine.Scene):
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.startSceneMap = ritzObjects.RitzMap(self, "start.dat")
        """
            Misc. Init
        """         
        self.setStopBounds(self.STOP_NEVER)
        resources.playMusic(resources.MFX_INTRO_THEME)
        
        """
            Create and add sprite groups
        """
        self.playDoor = miscellaneous.PlaySceneDoor(self, self.startSceneMap, 
                                                               (300, 264))
        self.exitDoor = miscellaneous.ExitSceneDoor(self, self.startSceneMap, 
                                                               (500, 264))
        self.playText = gameEngine.MyFontSprite(self, (300, 225), (100, 25), resources.PLAY_TEXT)
        self.exitText = gameEngine.MyFontSprite(self, (500, 225), (100, 25), resources.EXIT_TEXT)
        self.doorGroup = pygame.sprite.Group(self.playDoor, self.exitDoor)
        self.textGroup = pygame.sprite.Group(self.playText, self.exitText)
        self.staticGroup = pygame.sprite.Group(self.doorGroup, self.textGroup)
                
        self.backgroundGroup = pygame.sprite.Group(self.startSceneMap)
        self.addGroup(self.backgroundGroup)
        self.startSceneMap.addStaticGroup(self.staticGroup)
            


class InstructionsScene(gameEngine.Scene):
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        self.instructionSceneMap = ritzObjects.RitzMap(self, "instructions.dat")
        
        """
            Misc. Init
        """         
        self.setStopBounds(self.STOP_NEVER)
        resources.playMusic(None)
        
        """
            Create and add sprite groups
        """
        self.jumpButton = miscellaneous.SquareButtonSprite((250, 450), "W")
        self.leftButton = miscellaneous.SquareButtonSprite((100, 400), "A")
        self.rightButton = miscellaneous.SquareButtonSprite((130, 400), "D")
        self.downButton = miscellaneous.SquareButtonSprite((700, 425), "S")
        self.shootButton = miscellaneous.RectangleButtonSprite((525, 450), (50, 25), "Space")
        
        self.howToMoveFont = gameEngine.MyFontSprite(self, (120, 360), (125, 40),
                                                         resources.howToMoveCharacterText)
        self.howToJumpFont = gameEngine.MyFontSprite(self, (250, 410), (125, 40),
                                                         resources.howToJumpText)
        self.howToShootFont = gameEngine.MyFontSprite(self, (525, 410), (125, 40),
                                                         resources.howToShootText)
        self.howToEnterDoorFont = gameEngine.MyFontSprite(self, (700, 390), (125, 40),
                                                         resources.howToEnterDoorText)
                
        self.instructionsDoor = miscellaneous.InstructionsDoor(self, self.instructionSceneMap, 
                                                               (700, 505))
        self.backgroundGroup = pygame.sprite.Group(self.instructionSceneMap)
        self.instructionsGroup = pygame.sprite.Group(self.jumpButton, self.leftButton, 
                                                     self.rightButton, self.downButton,
                                                     self.shootButton, self.howToMoveFont,
                                                     self.howToJumpFont, self.howToShootFont,
                                                     self.howToEnterDoorFont)
        self.staticGroup = pygame.sprite.Group(self.instructionsDoor, self.instructionsGroup)
        self.addGroup(self.backgroundGroup)

        self.instructionSceneMap.addStaticGroup(self.staticGroup)
        
class SplashScene(gameEngine.Scene):
    SPLASH_DEPLAY = 120
    def __init__(self, (width, height), title):
        gameEngine.Scene.__init__(self, (width, height), title)
        """
            Misc. Init
        """
        self.splashCount = 0
        resources.playMusic(resources.MFX_SPLASHSCENE, 1, 0.3)
        
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
        elif sceneFlow == SCENE_GAME_OVER:
            endGameScene = GameOverScene((800, 600), "Ritz by Justin Hellsten - End", 
                                         gamePlayScene.currentLevel.scoreBoard.score)
            endGameScene.start()
            programExit = endGameScene.exit
            sceneFlow = SCENE_INSTRUCTIONS
        elif sceneFlow == SCENE_CREDITS:
            creditScene = CreditScene((800, 600), "Ritz by Justin Hellsten - Credit")
            creditScene.start()
            programExit = creditScene.exit
            
        sceneFlow += 1
        if sceneFlow > SCENE_CREDITS:
            sceneFlow = 0

if __name__ == "__main__": main()
    
