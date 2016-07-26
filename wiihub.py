# -*- encoding: utf-8 -*-
import sys, cwiid, glob, time, pickle
from os import system
global wm

x=0
while True:
    try:
        print('Press 1 and 2 on your Wiimote')
        wm=cwiid.Wiimote()
    except RuntimeError:
        x+=1
        print('Not Found. Trying Again')
    else:
        break
    if x>=10:
        sys.exit()
print('Found')
wm.led = 1
wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC

print('''Hold your Wiimote sideways; like this:
--------------
| + O |:  ·· |
--------------

Controls:
A               Play Game
B               Exit Hub
Left and Right  Change Selected Game
''')
a=glob.glob('Games/*.py')
pos=0
item='Current game: '+a[pos][6:-3]
print(item)

while True:
    if (wm.state['buttons'] & cwiid.BTN_UP):
        pos=pos-1
        if pos<0:
            pos=len(a)-1
        item='Current game: '+a[pos][6:-3]
        print(item)
        time.sleep(0.5)
    elif (wm.state['buttons'] & cwiid.BTN_DOWN):
        pos=pos+1
        if pos>len(a)-1:
            pos=0
        item='Current game: '+a[pos][6:-3]
        print(item)
        time.sleep(0.5)
    elif (wm.state['buttons'] & cwiid.BTN_A):
        f=open(a[pos],mode='r')
        g=f.read()
        f.close()
        exec(g)
        main(wm)
    elif (wm.state['buttons'] & cwiid.BTN_B):
        wm.close()
        sys.exit()
