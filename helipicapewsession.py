import time
import ac
import euclid

import helipicapewcar

try:
    import helipicapewthreading
except Exception as ex:
    ac.log("helipicapew::Error during import of helipicapewthreading: %s" % ex)


class HeliPicaPewSession(object):
    """A session like a qualifing or race; basically the instance of this app"""
    isRaceSession = False
    maxSlotId = 0
    track = ''
    cars = []
    nearcars = []
    isSingleplayer = True

    lastDriverCheck = 0

    def __init__(self):
        self.player = None
        self.prepare()
        helipicapewthreading.initConstants()

        self.isSingleplayer = not ac.getServerIP() or ac.getServerIP().isspace()


    def prepare(self):
        self.track = ac.getTrackName(0)

        #now we'll build the slots, so we later know every single (possible) car
        carIds = range(0, ac.getCarsCount(), 1)
        for carId in carIds:
            #first we'll check wether there is a car for this id; as soon it returns -1
            #it's over
            carModel = str(ac.getCarName(carId))
            if carModel == '-1':
                break
            else:
                maxSlotId = carId
                driverName = ac.getDriverName(carId)
                self.cars.append(helipicapewcar.HeliPicaPewCar(carId, driverName, carModel))

    def calcWorldPositions(self, delta):
        #we need to do all the calculations needed to draw this effectivly.
        
        self.nearcars = []
        self.player = self.cars[ac.getFocusedCar()]
        self.player.isPlayer = True
        self.player.calcCar()
        playerVectorReversed =  euclid.Vector2(self.player.currentVelocityVector.x * -1, self.player.currentVelocityVector.y * -1)
        # 绘车颜色方案 0: 玩家 1:玩家被套圈 2:其他车辆 3:套圈玩家的其他车车辆 4:其他车被玩家套圈
        self.player.colorRecipe = 0
        self.player.calcDrawingInformation(playerVectorReversed)

        for car in self.cars:
            car.calc(self.player)

            # 后面一段距离内是否有车快过玩家一圈
            isPlayerBlueFlag = False
            if car.isVisible and car.playerDistance < helipicapewcar.distanceThreshold and car != self.player:
                car.isPlayer = False
                car.calcDrawingInformation(playerVectorReversed)
                car.calcAngleToPlayer(self.player.centerPositionGui)
                # 绘车颜色方案 0: 玩家 1:玩家被套圈 2:其他车辆 3:套圈玩家的其他车车辆 4:其他车被玩家套圈
                car.colorRecipe = 2
                
                if self.isRaceSession:
                    if car.laps > self.player.laps:
                        # 是快过玩家至少一圈的车
                        car.colorRecipe = 3
                        if car.splineposition < self.player.splineposition and self.player.splineposition - car.splineposition < 0.05:
                            # 该车在玩家车后一小段距离
                            isPlayerBlueFlag = True

                    elif car.laps < self.player.laps:
                        # 是被玩家套圈的车
                        car.colorRecipe = 4
    
                self.nearcars.append(car)
                #ac.log("helipicapew::near car {0}: {1}, local {2}, gui {3}".format(car.name, car.currentWorldPosition, car.relativePositionMeters, car.centerPositionGui))
            if isPlayerBlueFlag:
                self.player.colorRecipe = 1
            else:
                self.player.colorRecipe = 0
 
