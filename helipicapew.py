import time
import math
import sys
import os
import platform

if platform.architecture()[0] == "64bit":
    sysdir = "stdlib64"
else:
    sysdir = "stdlib"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), sysdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

import ac
import acsys

import helipicapewsession
import helipicapewcar
import euclid
import threading

#Ini overwritable constants

#Update threshold: Do calculations every X seconds. 0 would be as often as possible, higher values won't
#switch this to 1 or a fancy background pic
showBackgroundPic=1
#show cars at all (0=off, 1=on, default=1)
showCars=1
#let the map be smooth (but faster). Default is 0.03 ~= 30 fps
updateThreshold=0.03
#Show title and background for x seconds
showTitle=5
#The background will be shortly after the app is shown (see showTitle).
#Unfortunately the background will stay after you click the app while racing, e.g. in a pitstop
#This is fixed by setting the background every frame, but this could affect performance.
#Switch to 0 if in doubt
removeBackgroundEveryFrame=1
#Color of the first indicator (default is yellow)
indicator1Colors = 1,0.843,0
#Color of the second indicator (default is orange)
indicator2Colors = 1,0.376,0


appWindow=0
lastTimeUpdate=0
running = True

hSession = None

showWindowTitle = True
appWindowActivated = 0
z = 1.0

#debug output label, ignore this
dbgLabel = 0

texture_radar = -1
texture_indicator_left = -1
texture_indicator_right = -1
version = "0.5"

sharedMemoryLoaded = False
# load sim_info: code by ferito

try:
    import sim_info
    sharedMemoryLoaded  = True
except Exception as e:
    ac.log("helipicapew::error while import sim_info. %s" % e)
    ac.log("helipicapew:: can't tell wether race or p/q, so blueflag is always enabled")


def acMain(ac_version):
    import time
 
    global appWindow, hSession, dbgLabel, texture_radar, texture_indicator_left, texture_indicator_right, z
    ac.log("helipicapew::acMain Start {}".format(time.localtime(time.time())))
    try:
        import helipicapewconfig
        helipicapewconfig.handleIni('helipicapew')

        z = helipicapewcar.guiZoomFactor

        appWindow=ac.newApp("helipicapew")
        ac.setSize(appWindow,200*z,200*z)
        ac.drawBorder(appWindow,0)
        ac.setBackgroundOpacity(appWindow,0)
        ac.setTitle(appWindow, "helipicapew v{}".format(version))

        ac.addRenderCallback(appWindow , onFormRender)
        ac.addOnAppActivatedListener(appWindow,onAppActivated)
        appWindowActivated = time.clock()
        showWindowTitle = True

        dbgLabel = ac.addLabel(appWindow, "")
        ac.setPosition(dbgLabel, 15, 405)

        texture_radar = ac.newTexture("apps/python/helipicapew/img/radar.png")
        texture_indicator_left = ac.newTexture("apps/python/helipicapew/img/indicatorL.png")
        texture_indicator_right = ac.newTexture("apps/python/helipicapew/img/indicatorR.png")

        hSession = helipicapewsession.HeliPicaPewSession()

        ac.log("helipicapew::acMain finished")

    except Exception as e:
        ac.log("helipicapew::acMain() %s" % e)
    return "helipicapew"

def onAppActivated(*args):
    global appWindowActivated, showWindowTitle
    ac.log("helipicapew::onAppActivated({0})".format(args))
    appWindowActivated = time.clock()
    showWindowTitle = True
    ac.setBackgroundOpacity(appWindow, 0.5)
    ac.setIconPosition(appWindow, 0, 0)
    ac.setTitle(appWindow, "helipicapew v{}".format(version))

def acShutdown():
    
    global running
    running = False
    hSession = None
    centerOffset = None
    ac.removeItem(appWindow)

def timeForCalculationCame():
    global lastTimeUpdate
    now = time.clock()

    # check if updateThreshold reached
    if (lastTimeUpdate == 0) or (now - lastTimeUpdate > updateThreshold):
        lastTimeUpdate = now
        return True
    else:
        return False

def doCalculationStuff():

    #Phase 0: Is this a race session?
    if sharedMemoryLoaded:
        # get shared memory info
        sim_info_obj = sim_info.SimInfo()
        #ac.log("session_type is %d" % (sim_info_obj.graphics.session))
        hSession.isRaceSession = sim_info_obj.graphics.session == sim_info.AC_RACE
     
    #then all the cars will receive their geo-update
    hSession.calcWorldPositions(0)

    #Hotfix: Hide the background when clicked. I really hope this won't affect performance
    if removeBackgroundEveryFrame == 1 and showWindowTitle == False:
        ac.setBackgroundOpacity(appWindow, 0)



def onFormRender(deltaT):
    global showWindowTitle, appWindowActivated, appWindow, dbgLabel, running
    if not running:
        return

    #Important: Other apps can alter the global ac.gl Color and Alpha; let's reset this to White
    ac.glColor4f(1,1,1,1)

    #Show/Hide the title shortly after the app became visible
    if showWindowTitle:
        if (time.clock() - appWindowActivated > showTitle):
            showWindowTitle = False
            ac.setBackgroundOpacity(appWindow, 0)
            ac.setIconPosition(appWindow, -7000, -3000)
            ac.setTitle(appWindow, "")

    try:
        #we won't do all the calculations every time, so we have to sort out some frames.
        #But: We'll need the graphics stuff every single time, or we'll have flickering. But no worry, opengl is fast

        if timeForCalculationCame():
            doCalculationStuff()

        #Now we draw the current cars on the minimap
        drawCars()

    except Exception as e:
        ac.log("helipicapew::onFormRender() %s" % e)

    #Important: We'll clean the color again, so we might not affect other apps
    ac.glColor4f(1,1,1,1)


def drawIndicators(maxIndicatorL, maxIndicatorR, alpha):

    if helipicapewcar.showIndicators and alpha > 0:
        #left side
        if maxIndicatorL == 1:
            ac.glColor4f(indicator1Colors[0], indicator1Colors[1], indicator1Colors[2], alpha) #yellow
            ac.glQuadTextured(0, helipicapewcar.yOff*z - 152*z / 2, 100*z, 152*z,texture_indicator_left)
        elif maxIndicatorL == 2:
            ac.glColor4f(indicator2Colors[0], indicator2Colors[1], indicator2Colors[2], alpha) #orange
            ac.glQuadTextured(0, helipicapewcar.yOff*z - 152*z / 2, 100*z, 152*z,texture_indicator_left)

        #right side
        if maxIndicatorR == 1:
            ac.glColor4f(indicator1Colors[0], indicator1Colors[1], indicator1Colors[2], alpha) #yellow
            ac.glQuadTextured(helipicapewcar.xOff*z, helipicapewcar.yOff*z - 152*z / 2, 100*z, 152*z,texture_indicator_right)
        elif maxIndicatorR == 2:
            ac.glColor4f(indicator2Colors[0], indicator2Colors[1], indicator2Colors[2], alpha) #orange
            ac.glQuadTextured(helipicapewcar.xOff*z, helipicapewcar.yOff*z - 152*z / 2, 100*z, 152*z,texture_indicator_right)


def drawCars():
    global hSession

    #The whole appearance is dependent on the highest alpha setting of the near cars,
    #so we need to figure that one out. As we already iterate we also get the indicator values
    maxOpacity = 0.0
    maxIndicatorL = 0
    maxIndicatorR = 0
    for c in hSession.nearcars:
        if c.maxOpacity > maxOpacity:
            maxOpacity = c.maxOpacity
        if c.overlapIndicatorL > maxIndicatorL:
            maxIndicatorL = c.overlapIndicatorL
        if c.overlapIndicatorR > maxIndicatorR:
            maxIndicatorR = c.overlapIndicatorR

    #nothing to draw is nothing to draw
    if maxOpacity == 0.0:
        return

    #First: Draw background. It's dependent on the setting as well as the maximum alpha value
    if showBackgroundPic == 1:
        ac.glColor4f(1,1,1,maxOpacity)
        ac.glQuadTextured(0,0,200*z,200*z,texture_radar)


    #basicall we iterate all the (near) cars and try to draw points or
    #whatever shapes of them - relative to the player's position and direction

    #first we check wether to show any indicators
    if helipicapewcar.showIndicators:
        drawIndicators(maxIndicatorL, maxIndicatorR, maxOpacity)

    if showCars:
        
        #then we draw all near cars
        for c in hSession.nearcars:
            c.drawYourself()


        # then we'll draw the players car at the center.
        hSession.player.maxOpacity = maxOpacity
        hSession.player.drawYourself()
        