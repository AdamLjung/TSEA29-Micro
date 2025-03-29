import math
import rplidardriver
import pygame

pygame.init()
display = pygame.display.set_mode((500,500))
display.fill((0,0,0))
pygame.display.update()

class Car:
    def __init__(self, xCoord, yCoord, state):
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.pos = (xCoord, yCoord)
        self.state = state

class Node:
    def __init__(self, xCoord, yCoord):
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.pos = (xCoord, yCoord)


class Cone:
    def __init__(self, xCoord, yCoord, coneType):
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.pos = (xCoord, yCoord)
        self.coneType = coneType

class Gate:
    def __init__(self, leftCone, rightCone, xCoord, yCoord, gateType):
        self.leftCone = leftCone
        self.rightCone = rightCone
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.pos = (xCoord, yCoord)
        self.gateType = gateType
        
## Cyan
def drawSmallCone(x, y):
   for i in range(5):
        for j in range(5):
            try:
                display.set_at((250 + int((x + i*25)/25), 250 + int((y + j*25)/25)), pygame.Color(0,255,255))
            except: 
                continue

## Green
def drawLargeCone(x, y):
   for i in range(5):
        for j in range(5):
            try:
                display.set_at((250 + int((x + i*25)/25), 250 + int((y + j*25)/25)), pygame.Color(0,255,0))
            except: 
                continue
                

def testFindNodes(car, lidar, nodes, coneNodes, cones, gates):
    readControll = 0
    for startBit,_, angle, distance in lidar.iter_measures():
        if readControll == 0:
            if distance <= 3000:
                xCoord =  car.xCoord + (distance * math.cos(math.radians(angle)))
                yCoord =  car.yCoord + (distance * math.sin(math.radians(angle)))
                nodes.append(Node(xCoord, yCoord))
                display.set_at((250 + int(xCoord/25), 250 + int(yCoord/25)), pygame.Color(255,255,255)) 

            if startBit:
                print("startbit")
                readControll += 1
                for i in range(len(nodes) - 1):
                    if math.dist(nodes[i].pos, nodes[i+1].pos) < 100:
                        coneNodes.append(nodes[i])
                        if (len(nodes) == (i + 1)):
                            coneNodes.append(nodes[i+1])
                            setCone(coneNodes, cones)
                            coneNodes = []
                    else:
                        coneNodes.append(nodes[i])
                        setCone(coneNodes, cones)
                        coneNodes = []
                #setGate
                #scanListShared[:] = cones #gate
                #print(scanListShared)
                for k in range(15):
                    for m in range(3):  
                        display.set_at((250 + int((k-1)), 250 + int((m-1))), pygame.Color(255,0,0))
                        
                pygame.display.update()
                display.fill((0,0,0))
                nodes = []
                cones = []
        elif startBit:
            if readControll >= 9:
                readControll = 0
            else:
                readControll += 1



def findNodes(car, lidar, nodes, coneNodes, cones, gates):
    readControll = 0
    for startBit,_, angle, distance in lidar.iter_measures():
        if readControll == 0:
            if distance <= 3000:
                xCoord = car.xCoord + (distance * math.cos(angle))
                yCoord = car.yCoord + (distance * math.sin(angle))
                nodes.append(Node(xCoord, yCoord))
            if startBit:
                cones = [] 
                readControll += 1
                for i in range(len(nodes) - 1):
                    if math.dist(nodes[i].pos, nodes[i+1].pos) < 100:
                        coneNodes.append(nodes[i]) #fix node[i + 1]
                    else:
                        i += 1
                    setCone(coneNodes, cones)
                if nodes == []:
                    setGate(car, cones, gates)
        elif startBit:
            if readControll >= 9:
                readControll = 0
            else:
                readControll += 1

def setCone(coneNodes, cones):
    coneSize = math.dist(coneNodes[0].pos, coneNodes[-1].pos)
    if coneSize > 100 and coneSize < 140:
        x = (coneNodes[0].xCoord + coneNodes[1].xCoord)/2
        y = (coneNodes[0].yCoord + coneNodes[1].yCoord)/2
        drawSmallCone(x,y)
  
        #cones.append((x,y))
        #cones.append(Cone(x, y, "small"))
        print(x,y)
    elif coneSize > 140 and coneSize < 200:
        x = (coneNodes[0].xCoord + coneNodes[1].xCoord)/2
        y = (coneNodes[0].yCoord + coneNodes[1].yCoord)/2
        drawLargeCone(x,y)
        #cones.append((x,y))
        #cones.append(Cone(x, y, "big"))
        print(x,y)
    
def setGate(car, cones, gates):
    for i in range(len(cones) - 1):
        leftCone = cones[i]
        rightCone = cones[i + 1]
        x = (leftCone.xCoord + rightCone.xCoord)/2
        y = (leftCone.yCoord + rightCone.yCoord)/2
        carPos = (car.xCoord, car.yCoord)
        if leftCone.type == "small":
            if rightCone.type == "small":
                gateType = "passage"
            elif rightCone.type == "big":
                gateType = "leftTurn"
        elif leftCone.type == "big":
            if rightCone.type == "small":
                gateType = "rightTurn"
            elif rightCone.type == "big":
                gateType = "goal"
        gates.append(Gate(leftCone, rightCone, x, y, gateType))
        gates.sorted(key=lambda point: math.dist((point.x, point.y), carPos))


def main():
    lidar = rplidardriver.RPLidar("/dev/ttyUSB2")
    car = Car(0, 0, "waiting")
    nodes = []
    coneNodes = []
    cones = []
    gates = []
    testFindNodes(car, lidar, nodes, coneNodes, cones, gates)

main()

