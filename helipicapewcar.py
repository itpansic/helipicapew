import euclid
import ac
import acsys
import math

#Ini overwritable constants
#The init values here are just for example - they are all overwritten by the ini file!

#This is the zoom factor for the whole app.
#1.0-1.2 is normal on a 24" with full hd. Increase to have it bigger (e.g. 1.5), decrease to minimize (e.g. 0.7)
guiZoomFactor=1.2
#We can make the whole app semi-transparent, so it's even less disturbing. 1.0 = full opacity, 0.0 = invisible
maxiumAlpha=0.9
#show overlap indicators (0=off, 1=on, default=0).
showIndicators=1
#Distance threshold: How far away are the cars we paint?
distanceThreshold = 30.0
#world coordinates zoom or how big the bars are
worldzoom = 5.0
#Opacity threshold: At wich distance (in meters) should the cars start to fade?
#8 would be around 2 car lenghts
opacityThreshold = 8.0
#fade out cars in front of the player in an arc of X degrees (0 to disable)
frontFadeOutArc=90
#if a car in front is faded out, how soft should it fade? (again in degrees, 0 to disable = on/off, 10? is default and quite nice)
frontFadeAngle=10
#how big are the cars (in meters). Sorry, no data from ac available
carLength=4.3
carWidth=1.8

#Non-Ini constants
#painting offset, should match the window. better don't touch
xOff = 100.0
yOff = 100.0


# 车辆边框厚度
carBorderWidth = 0.2

# 玩家车辆颜色1（车部部分颜色，默认是黄色）
playerCarFrontColor = [254. / 255., 216. / 255., 0]
# 玩家车辆颜色2（车尾部分颜色，默认是黄色）
playerCarRearColor = [174. / 255., 222. / 255., 0]
# 玩家车辆边框颜色（车尾部分颜色，默认是黄色）
playerCarBorderColor = [145. / 255., 140. / 255., 0]

# 玩家被套圈时车辆颜色1（车部部分颜色，默认是黄色）
playerCarFrontColorBlugFlag = [254. / 255., 216. / 255., 0]
# 玩家被套圈时车辆颜色2（车尾部分颜色，默认是黄色）
playerCarRearColorBlugFlag = [174. / 255., 222. / 255., 0]
# 玩家被套圈时车辆边框颜色（车尾部分颜色，默认是深黄色）
playerCarBorderColorBlugFlag = [145. / 255., 140. / 255., 0]

# 其他车辆颜色1（车部部分颜色，默认是淡灰色）
otherCarFrontColor = [167. / 255., 168. / 255., 169. / 255.]
# 其他车辆颜色2（车尾部分颜色，默认是白色）
otherCarRearColor = [242. / 255., 242. / 255., 242. / 255.]
# 其他车辆边框颜色（车尾部分颜色，默认是灰）
otherCarBorderColor = [128. / 255., 130. / 255., 132. / 255.]

# 套圈玩家的其他车车辆颜色1（车部部分颜色，默认是蓝色）
otherCarFrontColorOverLapping = [83. / 255., 153. / 255., 238. / 255.]
# 套圈玩家的其他车车辆颜色2（车尾部分颜色，默认是蓝色）
otherCarRearColorOverLapping = [35. / 255., 128. / 255., 238. / 255.]
# 套圈玩家的其他车车辆边框颜色（车尾部分颜色，默认是深蓝色）
otherCarBorderColorOverLapping = [0. / 255., 54. / 255., 119. / 255.]

# 其他车被玩家套圈时车辆颜色1（车部部分颜色，默认是绿色）
otherCarFrontColorUnderLapping = [108. / 255., 255. / 255., 39. / 255.]
# 其他车被玩家套圈时车辆颜色2（车尾部分颜色，默认是绿色）
otherCarRearColorUnderLapping = [39. / 255., 192. / 255., 46. / 255.]
# 其他车被玩家套圈时车辆边框颜色（车尾部分颜色，默认是深绿色）
otherCarBorderColorUnderLapping = [71. / 255., 146. / 255., 39. / 255.]

# 车辆绘制颜色方案
colorRecipeList = [
    [playerCarFrontColor,               playerCarRearColor,             playerCarBorderColor],
    [playerCarFrontColorBlugFlag,       playerCarRearColorBlugFlag,     playerCarBorderColorBlugFlag],
    [otherCarFrontColor,                otherCarRearColor,              otherCarBorderColor],
    [otherCarFrontColorOverLapping,     otherCarRearColorOverLapping,   otherCarBorderColorOverLapping],
    [otherCarFrontColorUnderLapping,    otherCarRearColorUnderLapping,  otherCarBorderColorUnderLapping]
]

# 重设车辆颜色配方数据
def updateColorRecipe():
    global colorRecipeList
    # 车辆绘制颜色方案
    colorRecipeList = [
        [playerCarFrontColor,               playerCarRearColor,             playerCarBorderColor],
        [playerCarFrontColorBlugFlag,       playerCarRearColorBlugFlag,     playerCarBorderColorBlugFlag],
        [otherCarFrontColor,                otherCarRearColor,              otherCarBorderColor],
        [otherCarFrontColorOverLapping,     otherCarRearColorOverLapping,   otherCarBorderColorOverLapping],
        [otherCarFrontColorUnderLapping,    otherCarRearColorUnderLapping,  otherCarBorderColorUnderLapping]
    ]

# 计算一点绕另外一点逆时针旋转一个角度后的坐标
def rotatePoint(pt, ptCenter, cosValue, sinValue):
    x = pt[0]
    y = pt[1]
    rx0 = ptCenter.x
    ry0 = ptCenter.y

    x0 = (x - rx0) * cosValue - (y - ry0) * sinValue + rx0
    y0 = (x - rx0) * sinValue + (y - ry0) * cosValue + ry0
    return [x0, y0]

# 待绘点
class PaintPoint(object):
    # 部件位置 0:FL 1:FR 2:RL 3:RR
    partIndex = 0
    # x坐标
    x = 0
    # y坐标
    y = 0
    
    def __init__(self, pt, partIndex):
        self.x = pt[0]
        self.y = pt[1]
        self.partIndex = partIndex

class HeliPicaPewCar(object):
    """This represents both a car with coordinates and a driver"""
    name = "player name"
    carModel = "car model"
    id = 0
    currentWorldPosition = None
    currentVelocityVector = None
    isPlayer = False

    currentTyreHeadingVector = None
    currentSpeed = 0.0
    splineposition = 0.0
    laps = -1
    playerDistance = 0.0
    isVisible = False

    # 绘车颜色方案 0: 玩家 1:玩家被套圈 2:其他车辆 3:套圈玩家的其他车车辆 4:其他车被玩家套圈
    colorRecipe = 0

    relativePositionsAngle=0.0
    relativePositionMeters = None
    centerPositionGui = None

    overlapIndicatorL=0
    overlapIndicatorR=0

    maxOpacity = 0.0

    guiBorderPtFL = [0, 0]
    guiBorderPtFR = [0, 0]
    guiBorderPtRL = [0, 0]
    guiBorderPtRR = [0, 0]
    guiPtFL = [0, 0]
    guiPtFR = [0, 0]
    guiPtRL = [0, 0]
    guiPtRR = [0, 0]
    guiBorderPtList = []
    guiPtList = []
    


    def __init__(self,carId, name, carModel):
        self.name = name
        self.id = carId
        self.carModel = carModel
        self.updateGuiBorderPtListWithMinYPositionIndex(0)
        self.updateGuiPtListWithMinYPositionIndex(0)


    # 重排待画的背景点
    # minYPostionIndex Y值最小的点序号：0:FL 1: FR 2: RL 3: RR
    def updateGuiBorderPtListWithMinYPositionIndex(self, minYPostionIndex):
        ptFL = PaintPoint(self.guiBorderPtFL, 0)
        ptFR = PaintPoint(self.guiBorderPtFR, 1)
        ptRL = PaintPoint(self.guiBorderPtRL, 2)
        ptRR = PaintPoint(self.guiBorderPtRR, 3)
        if minYPostionIndex == 0:
            self.guiBorderPtList = [ptFL, ptRL, ptRR, ptFR]
            return
        if minYPostionIndex == 1:
            self.guiBorderPtList = [ptFR, ptFL, ptRL, ptRR]
            return
        if minYPostionIndex == 2:
            self.guiBorderPtList = [ptRL, ptRR, ptFR, ptFL]
            return
        if minYPostionIndex == 3:
            self.guiBorderPtList = [ptRR, ptFR, ptFL, ptRL]
            return
        self.guiBorderPtList = [ptFL, ptRL, ptRR, ptFR]

    # 重排待画的车框点
    # minYPostionIndex Y值最小的点序号：0:FL 1: FR 2: RL 3: RR
    def updateGuiPtListWithMinYPositionIndex(self, minYPostionIndex):
        ptFL = PaintPoint(self.guiPtFL, 0)
        ptFR = PaintPoint(self.guiPtFR, 1)
        ptRL = PaintPoint(self.guiPtRL, 2)
        ptRR = PaintPoint(self.guiPtRR, 3)
        if minYPostionIndex == 0:
            self.guiPtList = [ptFL, ptRL, ptRR, ptFR]
            return
        if minYPostionIndex == 1:
            self.guiPtList = [ptFR, ptFL, ptRL, ptRR]
            return
        if minYPostionIndex == 2:
            self.guiPtList = [ptRL, ptRR, ptFR, ptFL]
            return
        if minYPostionIndex == 3:
            self.guiPtList = [ptRR, ptFR, ptFL, ptRL]
            return
        self.guiPtList = [ptFL, ptRL, ptRR, ptFR]
        
    def checkForNewDriver(self):
        acname = ac.getDriverName(self.id)
        if acname == self.name:
            return False

        self.name = acname
        return True



    def calcCar(self):
        self.currentSpeed = ac.getCarState(self.id, acsys.CS.SpeedKMH)

        #get the world position and direction
        x, y, z = ac.getCarState(self.id, acsys.CS.WorldPosition)
        self.currentWorldPosition = euclid.Point2(x, z)
        ff, uf, lf = ac.getCarState(self.id, acsys.CS.TyreContactPoint, acsys.WHEELS.FL)
        fr, ur, lr = ac.getCarState(self.id, acsys.CS.TyreContactPoint, acsys.WHEELS.RL)
        f, u, l = ff-fr, uf-ur, lf-lr # f,u,l now represents the vector pointing from RL wheel to FL wheel
        self.currentVelocityVector = euclid.Vector2(f, l).normalize()
        self.laps = ac.getCarState(self.id, acsys.CS.LapCount)
        self.splineposition = ac.getCarState(self.id, acsys.CS.NormalizedSplinePosition)

        #the relative Position (to the player itself) is 0,0
        self.relativePositionMeters = euclid.Point2(0,0)
        self.playerDistance = 0

        return x, y, z

    def calc(self, player):
        if self == player or not ac.isConnected(self.id) or ac.isCarInPitline(self.id):
            self.isVisible = False
            return

        # we are visible, so it's worth calculating the car's properties
        self.isVisible = True
        x, y, z = self.calcCar()

        # and add the stuff relative to the driver
        self.relativePositionMeters = euclid.Point2(x - player.currentWorldPosition.x, z - player.currentWorldPosition.y)
        self.playerDistance = player.currentWorldPosition.distance(euclid.Point2(x,z))

    def calcDrawingInformation(self, playerVectorReversed):
        global carWidth, carLength, carBorderWidth
        #the big goal is the determination of the centerPositionGui of this car,
        #as well as the opacity to draw this one

        #the player car is slightly easier. We start at 0,0, add the offset and multiply with zoom
        if self.isPlayer:
            self.centerPositionGui = euclid.Point2((0 + xOff) * guiZoomFactor,(0 + xOff) * guiZoomFactor)
            self.maxOpacity = 1.0

              # 计算背景框四个点
  
            l = carLength / 2 * worldzoom * guiZoomFactor
            w = carWidth / 2 * worldzoom * guiZoomFactor
            borderWidth = carBorderWidth * worldzoom * guiZoomFactor

            
            #front left
            x = self.centerPositionGui.x - w
            y = self.centerPositionGui.y - l
            self.guiBorderPtFL = [x, y]
            minIndex = 0
            minPt = [x, y]

            
            #front right	
            x = self.centerPositionGui.x + w
            y = self.centerPositionGui.y - l
            self.guiBorderPtFR = [x, y]
            if y < minPt[1]:
                minIndex = 1
                minPt = [x, y]

            #rear left
            x = self.centerPositionGui.x - w
            y = self.centerPositionGui.y + l
            self.guiBorderPtRL = [x, y]
            if y < minPt[1]:
                minIndex = 2
                minPt = [x, y]

            #rear right
            x = self.centerPositionGui.x + w
            y = self.centerPositionGui.y + l
            self.guiBorderPtRR = [x, y]
            if y < minPt[1]:
                minIndex = 3
                minPt = [x, y]

            # Maybe it'll be useful.
            # Yesterday I've spent some hours drawing something about circles for my tachometer. I've discovered 2 rules to draw Quads and Triangles (ac.glBegin(2) or ac.glBegin(3)).
            # 1) 1st point ac.glVertex2f(x, y) must have minimal Y coordinate.
            # 2) other 2 or 3 points must be defined counterclockwise (as you look on it) from 1st point.
            self.updateGuiBorderPtListWithMinYPositionIndex(minIndex)


            # 计算车框四个点位置
            #front left
            x = self.centerPositionGui.x - w + borderWidth
            y = self.centerPositionGui.y - l + borderWidth
            self.guiPtFL = [x, y]
            minIndex = 0
            minPt = [x, y]

            #front right	
            x = self.centerPositionGui.x + w - borderWidth
            y = self.centerPositionGui.y - l + borderWidth
            self.guiPtFR = [x, y]
            if y < minPt[1]:
                minIndex = 1
                minPt = [x, y]

            #rear left
            x = self.centerPositionGui.x - w + borderWidth
            y = self.centerPositionGui.y + l - borderWidth
            self.guiPtRL = [x, y]
            if y < minPt[1]:
                minIndex = 2
                minPt = [x, y]
                
            #rear right	
            x = self.centerPositionGui.x + w - borderWidth
            y = self.centerPositionGui.y + l - borderWidth
            self.guiPtRR = [x, y]
            if y < minPt[1]:
                minIndex = 3
                minPt = [x, y]

            # 打印四个点信息：
            # ac.log('Tyres:')
            # ac.log('FL: {}'.format(self.guiPtFL))
            # ac.log('FR: {}'.format(self.guiPtFR))
            # ac.log('RL: {}'.format(self.guiPtRL))
            # ac.log('RR: {}'.format(self.guiPtRR))
            # Maybe it'll be useful.
            # Yesterday I've spent some hours drawing something about circles for my tachometer. I've discovered 2 rules to draw Quads and Triangles (ac.glBegin(2) or ac.glBegin(3)).
            # 1) 1st point ac.glVertex2f(x, y) must have minimal Y coordinate.
            # 2) other 2 or 3 points must be defined counterclockwise (as you look on it) from 1st point.
            self.updateGuiPtListWithMinYPositionIndex(minIndex)
 
        else:
            #the other cars have to be rotated around the origin, then translated and zoomed

            ####
            #Rotation: We need the angle to the reverted playerVector
            angleR =  math.atan2(-1, 0) - math.atan2(playerVectorReversed.y, playerVectorReversed.x)
            
            cosTheta = math.cos(angleR)
            sinTheta = math.sin(angleR)
            x = cosTheta * self.relativePositionMeters.x - sinTheta * self.relativePositionMeters.y
            y = sinTheta * self.relativePositionMeters.x + cosTheta * self.relativePositionMeters.y

            ####
            #Opacity: How far away is the other car - regarding y (we don't want to fade someone out who is on the same height)
            #self.maxOpacity = self.calcAlpha(self.playerDistance) #would be a circle around the player
            self.maxOpacity = self.calcAlpha(y)

            #####
            #Overlaping indicator
            if showIndicators == 1:
                self.calcOverlap(-x,y)


            ####
            #Translation: Now we add the offsets and multiply with the zoom
            x = x * worldzoom * -1
            y = y * worldzoom * -1
            self.centerPositionGui = euclid.Point2( (x+xOff)*guiZoomFactor, (y+yOff)*guiZoomFactor)

            # 计算当前车方向向量与玩家车方向向量的夹角
            velocityVectorReverse = euclid.Vector2(self.currentVelocityVector.x * -1, self.currentVelocityVector.y * -1)
            currentAngleFromPlayer = velocityVectorReverse.angle(playerVectorReversed)

            # 计算叉乘结果 为正代表速度向量在玩家速度向量的顺时针方向
            temp = velocityVectorReverse.x * playerVectorReversed.y - velocityVectorReverse.y * playerVectorReversed.x
            # 如果是需要逆时针旋转绘画点，则为1，顺时针则为-1
            rotateDirection = -1 if temp > 0 else 1
            
            cosValue = math.cos(currentAngleFromPlayer * rotateDirection)
            sinValue = math.sin(currentAngleFromPlayer * rotateDirection)

            # 计算背景框四个点
  
            l = carLength / 2 * worldzoom * guiZoomFactor
            w = carWidth / 2 * worldzoom * guiZoomFactor
            borderWidth = carBorderWidth * worldzoom * guiZoomFactor

            #front left
            x = self.centerPositionGui.x - w
            y = self.centerPositionGui.y - l
            self.guiBorderPtFL = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            minIndex = 0
            minPt = [x, y]

            #front right	
            x = self.centerPositionGui.x + w
            y = self.centerPositionGui.y - l
            self.guiBorderPtFR = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            if y < minPt[1]:
                minIndex = 1
                minPt = [x, y]

            #rear left
            x = self.centerPositionGui.x - w
            y = self.centerPositionGui.y + l
            self.guiBorderPtRL = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            if y < minPt[1]:
                minIndex = 2
                minPt = [x, y]

            #rear right
            x = self.centerPositionGui.x + w
            y = self.centerPositionGui.y + l
            self.guiBorderPtRR = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            if y < minPt[1]:
                minIndex = 3
                minPt = [x, y]

            # Maybe it'll be useful.
            # Yesterday I've spent some hours drawing something about circles for my tachometer. I've discovered 2 rules to draw Quads and Triangles (ac.glBegin(2) or ac.glBegin(3)).
            # 1) 1st point ac.glVertex2f(x, y) must have minimal Y coordinate.
            # 2) other 2 or 3 points must be defined counterclockwise (as you look on it) from 1st point.
            self.updateGuiBorderPtListWithMinYPositionIndex(minIndex)

            # 计算车框四个点位置
            #front left
            x = self.centerPositionGui.x - w + borderWidth
            y = self.centerPositionGui.y - l + borderWidth
            self.guiPtFL = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            minIndex = 0
            minPt = [x, y]

            #front right	
            x = self.centerPositionGui.x + w - borderWidth
            y = self.centerPositionGui.y - l + borderWidth
            self.guiPtFR = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            if y < minPt[1]:
                minIndex = 1
                minPt = [x, y]

            #rear left
            x = self.centerPositionGui.x - w + borderWidth
            y = self.centerPositionGui.y + l - borderWidth
            self.guiPtRL = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            if y < minPt[1]:
                minIndex = 2
                minPt = [x, y]

            #rear right	
            x = self.centerPositionGui.x + w - borderWidth
            y = self.centerPositionGui.y + l - borderWidth
            self.guiPtRR = rotatePoint([x, y], self.centerPositionGui, cosValue, sinValue)
            if y < minPt[1]:
                minIndex = 3
                minPt = [x, y]


            # Maybe it'll be useful.
            # Yesterday I've spent some hours drawing something about circles for my tachometer. I've discovered 2 rules to draw Quads and Triangles (ac.glBegin(2) or ac.glBegin(3)).
            # 1) 1st point ac.glVertex2f(x, y) must have minimal Y coordinate.
            # 2) other 2 or 3 points must be defined counterclockwise (as you look on it) from 1st point.
            self.updateGuiPtListWithMinYPositionIndex(minIndex)
            

    def calcAngleToPlayer(self, playerGuiPosition):

        ####
        #Angle to the player
        dx,dy = self.centerPositionGui.x-playerGuiPosition.x, self.centerPositionGui.y-playerGuiPosition.y
        rads = math.atan2(dy, dx)
        self.relativePositionsAngle = math.degrees(rads) + 90.0

        self.maxOpacity *= self.calcAlphaFromAngle()


    def calcAlpha(self, distanceInMeters):

        #alpha is determined by some distance to the player (usually y or x/y distance)
        alpha = 1 - (math.fabs(distanceInMeters)-opacityThreshold)/(distanceThreshold-opacityThreshold)

        if alpha < 0:
            alpha = 0
        elif alpha > 1:
            alpha = 1

        return alpha

    def calcOverlap(self, relativeX, distanceInMeters):
        #We seek some indicator if there is a) almost to a little bit and b) substantial overlap on each side
        self.overlapIndicatorL = 0
        self.overlapIndicatorR = 0

        # 修复左右侧很远也会触发超车警示的BUG，5个车身宽度外的超车不显示超车警示
        if math.fabs(relativeX) > carWidth * 5:
            return

        #Substantial= less than a 0.8 car lengths
        if math.fabs(distanceInMeters) < carLength*0.8:
            if relativeX > 0:
                self.overlapIndicatorR = 2
            else:
                self.overlapIndicatorL = 2
        #a bit is less than car length + 20% safety
        elif math.fabs(distanceInMeters) < carLength*1.2:
            if relativeX < 0:
                self.overlapIndicatorL = 1
            else:
                self.overlapIndicatorR = 1

    def calcAlphaFromAngle(self):

        #If configured, we'll reduce alpha in front of the player
        if frontFadeOutArc <= 0:
            return 1.0

        #We assume a car in front is 0°, and -90° (left side) or 90° (right side)
        alpha = (math.fabs(self.relativePositionsAngle)- frontFadeOutArc/2.0 + frontFadeAngle/2.0) / 10
        if alpha < 0:
            alpha = 0
        elif alpha > 1:
            alpha = 1
        return alpha


    def calcAlphaFromY(self):
        #BEWARE, this is plain wrong. relativePositions.y is still world-aligned, let's stick with the distance instead.

        #here we seek the longditudal(does this word exist?) distance to the player.
        #therefore we'll return to the relativePositionMeters.y, because this is already the distance in meters
        y = math.fabs(self.relativePositionMeters.y)
        if y < opacityThreshold:
            #inside the "draw always-circle"?
            return 1.0
        if y > distanceThreshold:
            #outside the "don't bother me"-circle? Shouldn't be possible anyway
            return 0.0

        #else we'll just get a linear decreasing value.
        return 1 - ( y / (distanceThreshold - opacityThreshold - carLength))

    def drawYourself(self):

        global colorRecipeList

        # 配色
        recipe = colorRecipeList[self.colorRecipe]

        ac.glColor4f(1,1,1, self.maxOpacity * maxiumAlpha)
        ac.glBegin(3) # 3 : Draw quads.
        # 先画底框（被车框覆盖后就会留下边线）
        ac.glColor4f(recipe[2][0], recipe[2][1], recipe[2][2], self.maxOpacity * maxiumAlpha)
        
        for i, pt in enumerate(self.guiBorderPtList):
            ac.glVertex2f(pt.x, pt.y)
        ac.glEnd()


        # 再画车框
        ac.glBegin(3) # 3 : Draw quads.
        #ac.log('helipicapew::drawYourself car paint pt list:-----------')
        for i, pt in enumerate(self.guiPtList):
            #ac.log('helipicapew::drawYourself tyre index: {}, pt: {} {}'.format(pt.partIndex, pt.x, pt.y))
            # 根据点代表的轮胎位置更新颜色设置
            if pt.partIndex == 0 or pt.partIndex == 1:
                ac.glColor4f(recipe[0][0], recipe[0][1], recipe[0][2], self.maxOpacity * maxiumAlpha)
            else:
                ac.glColor4f(recipe[1][0], recipe[1][1], recipe[1][2], self.maxOpacity * maxiumAlpha)
            ac.glVertex2f(pt.x, pt.y)
        ac.glEnd()
        