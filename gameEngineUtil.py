'''
Created on Aug 1, 2013

@author: Justin Hellsten
'''

# Utility Constants
MAP_TOKENS = '[tokens]'
MAP_SIZE = '[size]'
MAP_IMG = '[imgs]'
MAP_IMGDIR = '[imgdir]'
MAP_STARTLOCATION = '[startlocation]'
MAP_SECTIONS = [MAP_TOKENS, MAP_SIZE, MAP_IMG, MAP_IMGDIR, MAP_STARTLOCATION]

# Default directories
DIR_DATA = 'data/'
DIR_GFX = 'gfx/'
DIR_MFX = 'mfx/'
DIR_SFX = 'sfx/'


""" tile map loader, requires map file to read map file data
    splits data based on tokens using "," as
    a delimeter and each line representing a row
    E.G
    0,1,2,3,4,5,6,7,8,9,10
    1,2,3,4,5,6,7,8,9,10,1 
    ...
    attributes: size, images ...
"""
def load_tileMap(mapfile):
    try:
        with open(DIR_DATA + mapfile): pass
        f = open(DIR_DATA + mapfile, 'r')    
    except IOError:
        return None


    data = {'[tokens]':[], '[size]':0, '[imgs]':[], '[imgdir]':'', '[startlocation]':(0,0)} 
    column = row = 0
    reading = ''
    
    for line in f.readlines():
        line = line.strip()
        readData = True
        
        for section in MAP_SECTIONS:
            if line == section: 
                reading = line
                readData = False
                            
        if not readData:
            continue
                     
        if reading == MAP_TOKENS:
            tokens = line.split(',')
            data[MAP_TOKENS].append([])      
            for token in tokens:       
                data[MAP_TOKENS][row].append(int(token))            
                column += 1
            row += 1
        elif reading == MAP_SIZE:
            data[MAP_SIZE] = int(line)
        elif reading == MAP_IMG:
            data[MAP_IMG].append(line)
        elif reading == MAP_IMGDIR:
            data[MAP_IMGDIR] = line
                    

    return data


    
    
    
    