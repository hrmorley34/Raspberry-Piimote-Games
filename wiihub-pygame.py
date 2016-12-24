#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys, cwiid, glob, time, pickle, pygame
from pygame.locals import *
from os import system

def main():
    global wm, SIZE, CBACKGROUND, CTEXT, CTEXTC, BACKGROUND, TEXT, TEXTC, TEXTT, FPS, FPSCLOCK, DISPLAYSURF, consolel, CLINES, DIC, CTRLS
    pygame.init()

    FPSCLOCK = pygame.time.Clock()
    SIZE = (640, 480)
    CBACKGROUND = (0, 0, 0)
    CTEXT = pygame.font.Font('freesansbold.ttf', 10)
    CTEXTC = (0, 255, 0)
    BACKGROUND = (0, 200, 0)
    TEXT = pygame.font.Font('freesansbold.ttf', 20)
    TEXTT = pygame.font.Font('freesansbold.ttf', 50)
    TEXTC = (0, 0, 0)
    FPS = 30
    CLINES = SIZE[1] / (10 + CTEXT.get_linesize())
    DISPLAYSURF = pygame.display.set_mode(SIZE)
    DIC = True
    CTRLS = "Hold your Wiimote sideways; the\nD-pad and (A) to the left and\n\
(1) and (2) to the right. Controls:\nA - Play Game\nB - Exit Hub\n+/- or left/\
right - Change Selected Game"
    wait = 0
    consolel = []
    pygame.display.set_caption('::< WiiHub >::')

    x=0
    while True:
        try:
            DISPLAYSURF.fill(CBACKGROUND)
            title()
            console('Press 1 and 2 on the Wiimote that\nyou would like to connect.')
            consolebl()
            pygame.display.flip()
            FPSCLOCK.tick(FPS)
            print("Connecting...")
            wm=cwiid.Wiimote()
        except RuntimeError:
            x+=1
            DISPLAYSURF.fill(CBACKGROUND)
            title()
            console('Not Found. Trying Again.')
            consolebl()
            pygame.display.flip()
            FPSCLOCK.tick(FPS)
            print("Not found.")
        else:
            break
        if x>=10:
            print("Quitting.")
            sys.exit()
    DISPLAYSURF.fill(CBACKGROUND)
    title()
    console('Found.')
    consolebl()
    pygame.display.flip()
    FPSCLOCK.tick(FPS)
    print("Found.")
    
    wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
    wm.led = 1

    DISPLAYSURF.fill(CBACKGROUND)
    title()
    ctrlbl()
    consolebl()
    pygame.display.flip()
    FPSCLOCK.tick(FPS)

    a=glob.glob('Games/*.py')
    pos=0

    try:
        item='Current game: '+a[pos][6:-3]
    except IndexError:
        item='There are no games.'
    print("Mainloop.")

    while True:
        DISPLAYSURF.fill(BACKGROUND)
        title()
        consolebl()
        citem(item)
        ctrlbl()

        if ((wm.state['buttons'] & cwiid.BTN_UP) or (wm.state['buttons'] & cwiid.BTN_MINUS)) and wait == 0:
            pos=pos-1
            if pos<0:
                pos=len(a)-1
            if item != 'There are no games.':
                item='Current game: '+a[pos][6:-3]
            wait = 12
        elif ((wm.state['buttons'] & cwiid.BTN_DOWN) or (wm.state['buttons'] & cwiid.BTN_PLUS)) and wait == 0:
            pos=pos+1
            if pos>len(a)-1:
                pos=0
            if item != 'There are no games.':
                item='Current game: '+a[pos][6:-3]
            wait = 12
        elif (wm.state['buttons'] & cwiid.BTN_A):
            if item != 'There are no games.':
                f=open(a[pos],mode='r')
                g=f.read()
                f.close()
                while (wm.state['buttons'] & cwiid.BTN_A):
                    do = "nothing"
                exec(g)
                main(wm, ds=DISPLAYSURF, fpsc=FPSCLOCK)
                # Redifine variables if overwritten
                CBACKGROUND = (0, 0, 0)
                CTEXT = pygame.font.Font('freesansbold.ttf', 10)
                CTEXTC = (0, 255, 0)
                BACKGROUND = (0, 200, 0)
                TEXT = pygame.font.Font('freesansbold.ttf', 20)
                TEXTT = pygame.font.Font('freesansbold.ttf', 50)
                TEXTC = (0, 0, 0)
                FPS = 30
                CLINES = SIZE[1] / (10 + CTEXT.get_linesize())
                DISPLAYSURF = pygame.display.set_mode(SIZE)
                DIC = True
                CTRLS = "Hold your Wiimote sideways; the\nD-pad and (A) to the \
left and\n(1) and (2) to the right.\nControls: A - Play Game\nB - Exit Hub\n+/- \
or left/right - Change Selected Game"
                consolel = ["Game QUIT."]
                wait = 12
        elif (wm.state['buttons'] & cwiid.BTN_B) or (wm.state['buttons'] & cwiid.BTN_HOME):
            wm.close()
            pygame.quit()
            sys.exit()
        if wait > 0:
            wait -= 1
        else:
            wait = 0

        pygame.display.flip()
        FPSCLOCK.tick(FPS)

def console(text):
    global consolel
    for t in text.split("\n"):
        if len(t) > 40:
            consolel.append(t[:40])
            consolel.append(t[40:80])
        else:
            consolel.append(t)

def consolebl():
    global consolel
    n = 0
    consolel = consolel[-CLINES:]
    for text in consolel:
        f = CTEXT.render(text, True, CTEXTC)
        DISPLAYSURF.blit(f, (0,n))
        n += 10+CTEXT.get_linesize()

def ctrlbl():
    n = 50
    for ctrl in CTRLS.split("\n"):
        f = TEXT.render(ctrl, True, TEXTC)
        DISPLAYSURF.blit(f, (0,n))
        n += 20+TEXT.get_linesize()

def citem(text):
    f = TEXT.render(text, True, TEXTC)
    fr = Rect((0, 0), TEXT.size(text))
    fr.center = (SIZE[0] / 2, SIZE[1] - 20)
    DISPLAYSURF.blit(f, fr)

def title(t="::< WiiHub >::"):
    pygame.display.set_caption(t)
    f = TEXTT.render(t, True, TEXTC, BACKGROUND)
    fr = Rect((0, 0), TEXTT.size(t))
    fr.center = (SIZE[0] / 2, 25)
    DISPLAYSURF.blit(f, fr)
