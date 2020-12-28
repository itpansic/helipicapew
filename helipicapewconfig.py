import os
import ac

section = ''

# This flag tells wether the config has changed and needs to be written to the disk
update = False

# Those are the imports needed to set the defaults.
# Change your imports according to your needs and project
import helipicapewsession
import helipicapew
import helipicapewcar

# We'll need to find the user's "documents" folder even it it has been moved away
# from the default C:\users\<user>\Documents\. This is a solution by never_eat_yellow_snow
import winreg

def expand_ac(*args):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    v = winreg.QueryValueEx(k, "Personal")
    return os.path.join(v[0], *args)

def handleIni(appName):
    global update, section
    update = False
    section = appName
    iniDirectory = expand_ac("Assetto Corsa/cfg/apps/")

    iniFile = iniDirectory + appName + '.ini'
    if not os.path.exists(iniDirectory):
        update = True
        ac.log('helipicapew::handleIni ini directory ' + iniDirectory + ' does not exist, try to create it')
        os.makedirs(iniDirectory)
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser  # ver. < 3.0
    config = ConfigParser()
    config.read(iniFile)

    # if there is no ini-file (with an 'appName' section), we will create one
    # with the default values. This way we get configurable stuff
    # which is never overwritten by updates or even Steam Workshop
    if not config.has_section(appName):
        config.add_section(appName)
        update = True

    # Then we'll feed all the constants with either the ini
    # values, but they also can be overridden by the defaults

    helipicapew.showBackgroundPic = getOrSetDefaultInt(config, 'showBackgroundPic', 1)
    helipicapewcar.showIndicators = getOrSetDefaultInt(config, 'showIndicators', 1)
    helipicapew.showCars = getOrSetDefaultInt(config, 'showCars', 1)
    helipicapewcar.guiZoomFactor = getOrSetDefaultFloat(config, 'guiZoomFactor', 1.2)
    helipicapewcar.maxiumAlpha = getOrSetDefaultFloat(config, 'maxiumAlpha', 0.9)
    helipicapew.showTitle = getOrSetDefaultInt(config, 'showTitle', 5)
    helipicapewcar.worldzoom = getOrSetDefaultFloat(config, 'worldzoom', 5)
    helipicapewcar.opacityThreshold = getOrSetDefaultFloat(config, 'opacityThreshold', 8.0)
    helipicapewcar.frontFadeOutArc = getOrSetDefaultInt(config, 'frontFadeOutArc', 90)
    helipicapewcar.frontFadeAngle = getOrSetDefaultInt(config, 'frontFadeAngle', 10)
    helipicapewcar.carLength = getOrSetDefaultFloat(config, 'carLength', 4.3)
    helipicapewcar.carWidth = getOrSetDefaultFloat(config, 'carWidth', 1.8)
    helipicapewcar.distanceThreshold = getOrSetDefaultFloat(config, 'distanceThreshold', 30.0)
    helipicapew.updateThreshold = getOrSetDefaultFloat(config, 'updateThreshold', 0.03)
    helipicapew.removeBackgroundEveryFrame = getOrSetDefaultInt(config, 'removeBackgroundEveryFrame', 1)
    helipicapew.indicator1Colors = getOrSetDefaultFloatArray(config, 'indicator1Colors', 1,0.843,0)
    helipicapew.indicator2Colors = getOrSetDefaultFloatArray(config, 'indicator2Colors', 1,0.376,0)

    # 车辆边框厚度
    helipicapewcar.carBorderWidth = getOrSetDefaultFloat(config, 'carBorderWidth', 0.2)
    # 玩家车辆颜色1（车部部分颜色，默认是黄色）
    helipicapewcar.playerCarFrontColor = getOrSetDefaultFloatArray(config, 'playerCarFrontColor',1, 0.85, 0)
    # 玩家车辆颜色2（车尾部分颜色，默认是黄色）
    helipicapewcar.playerCarRearColor = getOrSetDefaultFloatArray(config, 'playerCarRearColor',0.68, 0.87, 0)
    # 玩家车辆边框颜色（车尾部分颜色，默认是黄色）
    helipicapewcar.playerCarBorderColor = getOrSetDefaultFloatArray(config, 'playerCarBorderColor',0.57, 0.55, 0)

    # 玩家被套圈时车辆颜色1（车部部分颜色，默认是黄色）
    helipicapewcar.playerCarFrontColorBlugFlag = getOrSetDefaultFloatArray(config, 'playerCarFrontColorBlugFlag',1, 0.85, 0)
    # 玩家被套圈时车辆颜色2（车尾部分颜色，默认是黄色）
    helipicapewcar.playerCarRearColorBlugFlag = getOrSetDefaultFloatArray(config, 'playerCarRearColorBlugFlag',0.68, 0.87, 0)
    # 玩家被套圈时车辆边框颜色（车尾部分颜色，默认是深黄色）
    helipicapewcar.playerCarBorderColorBlugFlag = getOrSetDefaultFloatArray(config, 'playerCarBorderColorBlugFlag',0.57, 0.55, 0)

    # 其他车辆颜色1（车部部分颜色，默认是淡灰色）
    helipicapewcar.otherCarFrontColor = getOrSetDefaultFloatArray(config, 'otherCarFrontColor',0.65, 0.65, 0.65)
    # 其他车辆颜色2（车尾部分颜色，默认是白色）
    helipicapewcar.otherCarRearColor = getOrSetDefaultFloatArray(config, 'otherCarRearColor',0.95, 0.95, 0.95)
    # 其他车辆边框颜色（车尾部分颜色，默认是灰）
    helipicapewcar.otherCarBorderColor = getOrSetDefaultFloatArray(config, 'otherCarBorderColor',0.5, 0.5, 0.5)

    # 套圈玩家的其他车车辆颜色1（车部部分颜色，默认是蓝色）
    helipicapewcar.otherCarFrontColorOverLapping = getOrSetDefaultFloatArray(config, 'otherCarFrontColorOverLapping',0.33, 0.6, 0.93)
    # 套圈玩家的其他车车辆颜色2（车尾部分颜色，默认是蓝色）
    helipicapewcar.otherCarRearColorOverLapping = getOrSetDefaultFloatArray(config, 'otherCarRearColorOverLapping',0.14, 0.5, 0.93)
    # 套圈玩家的其他车车辆边框颜色（车尾部分颜色，默认是深蓝色）
    helipicapewcar.otherCarBorderColorOverLapping = getOrSetDefaultFloatArray(config, 'otherCarBorderColorOverLapping',0, 0.21, 0.47)

    # 其他车被玩家套圈时车辆颜色1（车部部分颜色，默认是绿色）
    helipicapewcar.otherCarFrontColorUnderLapping = getOrSetDefaultFloatArray(config, 'otherCarFrontColorUnderLapping',0.42, 1, 0.15)
    # 其他车被玩家套圈时车辆颜色2（车尾部分颜色，默认是绿色）
    helipicapewcar.otherCarRearColorUnderLapping = getOrSetDefaultFloatArray(config, 'otherCarRearColorUnderLapping',0.15, 0.75, 0.18)
    # 其他车被玩家套圈时车辆边框颜色（车尾部分颜色，默认是深绿色）
    helipicapewcar.otherCarBorderColorUnderLapping = getOrSetDefaultFloatArray(config, 'otherCarBorderColorUnderLapping',0.28, 0.57, 0.15)

    helipicapewcar.updateColorRecipe()
    # If anything was written to the config, we'll have to write this to the config file
    # in the end
    if update:
        ac.log('helipicapew::handleIni Updates to ini file detected, will update ' + iniFile)
        with open(iniFile, 'w') as configfile:
            config.write(configfile)

def getOrSetDefaultString(config, key, default):
    global update
    try:
        return config.get(section, key)
    except Exception as e:
        ac.log('helipicapew::getOrSetDefaultString error {}'.format(e))
        config.set(section, key, str(default))
        update=True
        return default

def getOrSetDefaultInt(config, key, default):
    global update
    try:
        return config.getint(section, key)
    except Exception as e:
        ac.log('helipicapew::getOrSetDefaultInt error {}'.format(e))
        config.set(section, key, str(default))
        update=True
        return default

def getOrSetDefaultFloat(config, key, default):
    global update
    try:
        return config.getfloat(section, key)
    except Exception as e:
        ac.log('helipicapew::getOrSetDefaultFloat error {}'.format(e))
        config.set(section, key, str(default))
        update=True
        return default

def getOrSetDefaultFloatArray(config, key, defaultR, defaultG, defaultB):
    global update
    try:
        floatArray = []
        i = 0
        for f in config.get(section, key).split(","):
            floatArray.append(float(f))
            i = i + 1
        return floatArray
    except Exception as e:
        ac.log('helipicapew::getOrSetDefaultFloatArray error {}'.format(e))
        config.set(section, key, str("{},{},{}".format(defaultR, defaultG, defaultB)))
        update=True
        return [ defaultR, defaultG, defaultB ]
