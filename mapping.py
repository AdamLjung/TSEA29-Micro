import math
import rplidardriver

# radSmall Cone = 7
# radLarge Cone = 10
# avstånd mellan = 45 - 55 Cone

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


def findNodes(scanListShared, lidarConnection, sharedVelocity):
    lidar = rplidardriver.RPLidar(lidarConnection)
    car = Car(0, 0, "waiting")
    readControll = 0
    cones = []
    nodes = []
    coneNodes = []
    gates = []
    halfway = False
    #value = 0
    try:
        for startBit,random, angle, distance in lidar.iter_measures():
            #value += 1
          #  if(distance == 0):
          #      print("Distance is 0!!!!!")
            
            #if startBit:
                #print(value)
                #print(angle)
                #value = 0

            
            if angle >= 355 and not halfway:
                halfway = True
            if distance <= 3000:# and (angle >= 270 or angle <= 90):
                xCoord =  car.xCoord + (distance * math.sin(math.radians(angle)))
                yCoord =  car.yCoord + (distance * math.cos(math.radians(angle)))
                nodes.append(Node(xCoord, yCoord))
            if angle >= 175 and angle <= 185 and halfway:
                halfway = False
                #skicka ett runt varv
                for i in range(len(nodes) - 1):
                    if math.dist(nodes[i].pos, nodes[i+1].pos) < 50: #kalibrera detta värde
                        coneNodes.append(nodes[i])
                        if (len(nodes) == (i + 1)):
                            coneNodes.append(nodes[i+1])
                            setCone(coneNodes, cones)
                            coneNodes = []
                    else:
                        coneNodes.append(nodes[i])
                        setCone(coneNodes, cones)
                        coneNodes = []
                setGate(gates, car, cones)
                scanListShared[:] = gates
                gates = []
                nodes = []
                cones = []
    except Exception as e:
        print(e)
        lidar.stop_lidar()
    
def setCone(coneNodes, cones):
    #x = int((coneNodes[0].xCoord + coneNodes[-1].xCoord)/2)
    #y = int((coneNodes[0].yCoord + coneNodes[-1].yCoord)/2)
    coneSize = int(math.dist(coneNodes[0].pos, coneNodes[-1].pos))
        
    if coneSize > 80 and coneSize < 140: # kalibrera
        x = int((coneNodes[0].xCoord + coneNodes[-1].xCoord)/2)
        y = int((coneNodes[0].yCoord + coneNodes[-1].yCoord)/2)
        cones.append((x,y, "small"))
            #cones.append(Cone(x, y, "small"))
            #print(x,y)
    elif coneSize >= 140 and coneSize < 200: # kalibrera
        x = int((coneNodes[0].xCoord + coneNodes[-1].xCoord)/2)
        y = int((coneNodes[0].yCoord + coneNodes[-1].yCoord)/2)
        cones.append((x,y, "big"))
            #cones.append(Cone(x, y, "big"))
    
def setGate(gates, car, cones):
    #print(len(cones))
    #print(range(len(cones)))
    usedCones = []
    usedPairs = []
    for i in range(len(cones)):
        for j in range(len(cones)):
            if i != j and not((i,j) in usedPairs  or (j,i) in usedPairs):
                if cones[i][2] == "big" or cones[j][2] == "big":
                    x1 = cones[i][0]
                    y1 = cones[i][1]
                    x2 = cones[j][0]
                    y2 = cones[j][1]
                    gateDist = math.dist((x1, y1), (x2, y2))
                    if gateDist > 550 and gateDist < 850:
                        gates.append(("gate", x1, y1, cones[i][2], x2, y2, cones[j][2]))
                        usedCones.append(i)
                        usedCones.append(j)
                        usedPairs.append((i,j))
                        
                else:
                    x1 = cones[i][0]
                    y1 = cones[i][1]
                    x2 = cones[j][0]
                    y2 = cones[j][1]
                    gateDist = math.dist((x1, y1), (x2, y2))
                    if gateDist > 520 and gateDist < 830:
                        gates.append(("gate", x1, y1, cones[i][2], x2, y2, cones[j][2]))
                        usedCones.append(i)
                        usedCones.append(j)
                        usedPairs.append((i,j))
                        #print(x1, y1)
                        #print(x2, y2)
                        #print("smoool sväng")
            
    for k in range(len(cones)):
        if k not in usedCones:
            gates.append(("cone", cones[k][0], cones[k][1], cones[k][2]))
#                rightCone = cones[j]
#                            
#            
#        x = (leftCone.xCoord + rightCone.xCoord)/2
#        y = (leftCone.yCoord + rightCone.yCoord)/2
#        carPos = (car.xCoord, car.yCoord)
#        if leftCone.type == "small":
#            if rightCone.type == "small":
#                gateType = "passage"
#            elif rightCone.type == "big":
#                gateType = "leftTurn"
#        elif leftCone.type == "big":
#            if rightCone.type == "small":
#                gateType = "rightTurn"
#            elif rightCone.type == "big":
#                gateType = "goal"
#        gates.append(Gate(leftCone, rightCone, x, y, gateType))
#        gates.sorted(key=lambda point: math.dist((point.x, point.y), carPos))










