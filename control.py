import serial
import time
import math
import numpy as np

def resetData(data):
    data.update({
        "Wheel_Angle": 25,
        "Thrust": 25,
        "Velocity": 0,
        "Distance": 0,
        "Lap_Time": 0,
        "Gear": 0,
    })
    
def sendData(ID, dataOut, serialConnection):
    dataOut = ID + dataOut
    packet = bytearray()
    packet.append(dataOut)
    serialConnection.write(packet)
    

def sendDataTest(vals, portstr):
    oldVal = 1
    oldThrustTest = 51
    serialConnection = serial.Serial(portstr,115200)
    cntr = 0
    
    while True:
        cntr +=1 
        dataOutAngle = 128 + vals[0]
        
        dataOutThrust = 0 + vals[1]
        
        packetThrust = bytearray()
        packetAngle = bytearray()
        
        packetThrust.append(dataOutThrust)
        packetAngle.append(dataOutAngle)
        
        if(not oldThrustTest == dataOutThrust) or cntr == 100: 
            cntr = 0
            serialConnection.write(packetThrust)
            oldThrustTest = dataOutThrust
            time.sleep(0.0001)
            
        
        if(not oldVal == dataOutAngle):
            serialConnection.write(packetAngle)
            oldVal = dataOutAngle
            
        time.sleep(0.005)
        

def receiveData(velocity, receivestr):
        readSerial = serial.Serial(receivestr, 115200)
        while True:
            result = readSerial.read(1)
            count = int.from_bytes(result, byteorder='big') 
            ms = (count * 0.0235) / 0.1
            velocity[0] = ms


oldThrust = 51
oldAngle = 51

def main(dataShared, btnsShared, scanListShared, stearingConnection, sensorConnection, valsShared, velocityShared, serverLidar):
    print("Running Control")

    Wheel_Angle = 25
    Thrust = 27
    sendPrevious = "straight"  

    while True:
        #Copy all shered values so lock only active for minimal time
        btns = btnsShared.copy()
        data = dataShared.copy()
        lidar = scanListShared[:]
            
        
        valsShared[0] = data["Wheel_Angle"]
        valsShared[1] = data["Thrust"]
        data["Velocity"] = velocityShared[0]
        

        if btns["resetToggle"] == 1:
            resetData(data)
            previous = ("gate", 0, 0, "small", 0, 0, "small")
        if btns["autoOnOffToggle"] == 0:
            if btns["rightToggle"] == 1:
                data["Wheel_Angle"] = 50
            elif btns["leftToggle"] == 1:
                data["Wheel_Angle"] = 0
            else:
                data["Wheel_Angle"] = 25
            if btns["upToggle"] == 1:
                data["Thrust"] = 25 + (5 * btns["gear"])
            elif btns["downToggle"] == 1:
                data["Thrust"] = 25 - (5 * btns["gear"])
            elif btns["upToggle"] == 0 and btns["downToggle"] == 0:
                data["Thrust"] = 25
        else:
            data["Thrust"] = Thrust + btns["gear"]
            data["Wheel_Angle"] = Wheel_Angle
        gates = []
        cones = []
        backGates = []
        if len(lidar) > 0: 
            for gate in lidar:
                
                if gate[0] == "gate":
                    
                    midPoint = getMidPoint((gate[1], gate[2]), (gate[4], gate[5]))[2]

                    dist = math.dist([midPoint[0], midPoint[1]], [0,0])
                    if midPoint[1] == 0:
                        angleGate = 0
                    else:
                        angleGate = math.degrees(math.atan(midPoint[0]/midPoint[1]))
                   
                    if(gate[2] > 0 and gate[5] > 0):
                        gates.append([gate, dist, midPoint])
                    elif dist < 1500 and abs(midPoint[0]) < 500:
                        gate = ("backGate", gate[1], gate[2], gate[3], gate[4], gate[5], gate[6])
                        backGates.append([gate, dist, midPoint])
                        
                        
                    sendPrevious = "straight"
                else:
                    cones.append(gate)
            gates.sort(key = sortGates)
            backGates.sort(key = sortGates)
            result = []
            if len(backGates)>0:
                for b in backGates:
                    if(b[0][2] < 0 and b[0][5] < 0):
                        result.append(b)
                        backGates = result
                result = []

            if len(backGates)>0:

                if backGates[0][0][3] == "small" and backGates[0][0][6] == "big":
                    sendPrevious = "left"
                    for g in gates:
                        x1 = g[2][0]
                        x2 = backGates[0][2][0]
                        if((x1 < 0 and x2 < 0 and x1 < x2) or (x1 > 0 and x2 > 0 and x1 < x2) or (x1 < 0 and x2 > 0)):
                            result.append(g)

                    gates = result
                elif backGates[0][0][3] == "big" and backGates[0][0][6] == "small":
                    sendPrevious = "right"
                    for g in gates:
                        x1 = g[2][0]
                        x2 = backGates[0][2][0]

                        if((x1 < 0 and x2 < 0 and x1 > x2) or (x1 > 0 and x2 > 0 and x1 > x2) or (x1 > 0 and x2 < 0)):
                            result.append(g)
                    gates = result
                elif backGates[0][0][3] == "big" and backGates[0][0][6] == "big":
                    sendPrevious = "goal"
                else:
                    sendPrevious = "straight"
                    for g in gates:
                        x1 = g[2][0]
                        x2 = backGates[0][2][0]
                        if abs(x1-x2) < 1000:
                            result.append(g)
                        gates = result

            prePreRadius = 800
            preRadius = 800 #600
            preScaling= 600 #600
            postScaling= 50
            prePreScaling = 1000
        
            if len(gates) > 0: 
                gate = gates[0][0]
                data["Distance"] = gates[0][1] 
                postPoint, prePoint, middlePoint, prePrePoint = getMidPoint((gate[1], gate[2]), (gate[4], gate[5]), preScaling, postScaling, prePreScaling)
            
                vecX = postPoint[0] - prePoint[0]
                vecY = postPoint[1] - prePoint[1]
                gates[0][0] += (prePoint, preRadius, postPoint, sendPrevious)

                if(abs(prePoint[0]) < preRadius and abs(prePoint[1]) < preRadius):
                     
                    angleTurn = math.degrees(math.atan(postPoint[0]/postPoint[1]))
                    k = 0.75
               # elif(abs(prePrePoint[0]) < prePreRadius and abs(prePrePoint[1]) < prePreRadius):
               #     angleTurn = math.degrees(math.atan(prePoint[0]/prePoint[1]))
               #     k = 0.65

                else:    
                    angleTurn = math.degrees(math.atan(prePoint[0]/prePoint[1]))
                    k = 0.65

                Wheel_Angle = turn(angleTurn, k)
                
        else:
            Wheel_Angle = 25
        tmp = []
        tmp += [g[0] for g in gates]
        if len(backGates)>0:
            tmp += [backGates[0][0]]
        tmp += cones
        serverLidar[:] = tmp
        dataShared.update(data)


def angleBetween(v1, v2):
    v1u = unitVector(v1)
    v2u = unitVector(v2)
    
    return math.degrees(np.arccos(np.clip(np.dot(v1u, v2u), -1.0, 1.0)))

def unitVector(vector):
    return vector/np.linalg.norm(vector)

def perpendicular(vec2d):
    return(-vec2d[1], vec2d[0])

def getMidPoint(p1,p2, preScaling=0, postScaling=0, prePreScaling=0):
    midX = (p1[0]+p2[0])/2
    midY = (p1[1]+p2[1])/2
    offset = perpendicular(((p1[0] - midX),(p1[1] - midY))) #pre gate
    normalized = unitVector(offset) 
    offset2 = (normalized[0] * preScaling, normalized[1] * preScaling)
    offset3 = (normalized[0] * postScaling, normalized[1] * postScaling)
    offset4 = (normalized[0] * prePreScaling, normalized[1] * prePreScaling)
                # post                                       pre                          mid                       prePre
    return (midX - offset3[0], midY - offset3[1]) , (midX+offset2[0], midY+offset2[1]), (midX, midY), (midX + offset4[0], midY+ offset4[1])

def sortGates(e):
    return e[1]

def sortAngle(e):
    return e[2]

def turn(angle, k):
    if(25 + angle * k > 50):
        return 50
    elif(25 + angle * k < 0):
        return 0
    else: 
        return math.floor(25 + angle * k)
