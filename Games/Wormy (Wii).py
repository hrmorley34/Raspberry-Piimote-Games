import random, pygame, sys, cwiid, time
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

sizem = 2
ccclock = 0
def cellchange():
    global CELLSIZE, CELLWIDTH, CELLHEIGHT, sizem, ccclock
    
    if (wm.state['buttons'] & cwiid.BTN_1) and ccclock == 0:
        sizem += 1
        ccclock = 20
    if (wm.state['buttons'] & cwiid.BTN_2) and ccclock == 0:
        sizem -= 1
        ccclock = 20
    
    sizem = ((sizem - 1) % 4) + 1
    CELLSIZE = 5 * (2 ** (sizem-1))
    assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
    assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
    CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
    CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
    if ccclock > 0:
        ccclock -= 1

cellchange()

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
BRIGHTGREEN=(155, 255, 155)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main(wm):
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    
    wm.led = 1
    wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy Wii')

    showStartScreen(wm)
    while True:
        a=runGame(wm)
        if a==0:
            break
        wm.rumble=True
        time.sleep(1)
        wm.rumble=False
        a=showGameOverScreen(wm)
        if a==0:
            break
    return(0)

def runGame(wm):# Set a random start point.
    startx = random.randint(10, CELLWIDTH - 11)
    starty = random.randint(10, CELLHEIGHT - 11)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

        if (wm.state['buttons'] & cwiid.BTN_UP):
            if direction != RIGHT:
                direction=LEFT
        elif (wm.state['buttons'] & cwiid.BTN_DOWN):
            if direction != LEFT:
                direction=RIGHT
        elif (wm.state['buttons'] & cwiid.BTN_LEFT):
            if direction != UP:
                direction=DOWN
        elif (wm.state['buttons'] & cwiid.BTN_RIGHT):
            if direction != DOWN:
                direction=UP
        if (wm.state['buttons'] & cwiid.BTN_HOME):
            terminate()
            return(0)

        if wormCoords[HEAD]['x'] <= -1 or wormCoords[HEAD]['x'] >= CELLWIDTH or wormCoords[HEAD]['y'] <= -1 or wormCoords[HEAD]['y'] >= CELLHEIGHT:
            # When moving off one side move onto the other
            wormCoords[HEAD]['x'] = wormCoords[HEAD]['x'] % CELLWIDTH
            wormCoords[HEAD]['y'] = wormCoords[HEAD]['y'] % CELLHEIGHT
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return

        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            wm.rumble = True
            apple = getRandomLocation() # set a new apple somewhere
        else:
            wm.rumble = False
            del wormCoords[-1] # remove worm's tail segment

        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        cellchange()
        if ccclock == 19:
            apple = getRandomLocation()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press A to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def drawSizeMsg():
    chsizeSurf = BASICFONT.render('Press 1/2 to change the square sizes.', True, DARKGRAY)
    chsizeRect = chsizeSurf.get_rect()
    chsizeRect.topleft = (100, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(chsizeSurf, chsizeRect)

def checkForKeyPress():
    for event in pygame.event.get():
        if event.type == QUIT:      #event is quit 
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:   #event is escape key
                terminate()
            else:
                return event.key   #key found return with it
    # no quit or key events in queue so return None    
    return None

    
def showStartScreen(wm):
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)
    titleSurf3 = titleFont.render('Wormy!', True, BRIGHTGREEN)

    degrees1 = 0
    degrees2 = 0
    degrees3 = 0
    
    pygame.event.get()  #clear out event queue
    
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)
        
        rotatedSurf3 = pygame.transform.rotate(titleSurf3, degrees3)
        rotatedRect3 = rotatedSurf3.get_rect()
        rotatedRect3.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf3, rotatedRect3)

        drawPressKeyMsg()
        drawSizeMsg()
        
        if (wm.state['buttons'] & cwiid.BTN_A):
            break
        elif (wm.state['buttons'] & cwiid.BTN_HOME):
            terminate()
            return(0)
        
        cellchange()
        if ccclock == 19:
            apple = getRandomLocation()
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
        degrees1 += 3
        degrees2 += 9
        degrees3 += 15

def terminate():
    pygame.quit()

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def showGameOverScreen(wm):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    pygame.event.get()  #clear out event queue 
    while True:
        if (wm.state['buttons'] & cwiid.BTN_A):
            break
        elif (wm.state['buttons'] & cwiid.BTN_HOME):
            terminate()
            return(0)
        cellchange()
        if ccclock == 19:
            apple = getRandomLocation()
        pygame.time.wait(100)

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))
