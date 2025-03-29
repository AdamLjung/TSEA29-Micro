from multiprocessing import Process, Manager
import server
import control
import serial
import mapping

useLidar = True
useSerial = True

def getSerial():
    devSerials = [
        "/dev/ttyUSB1",
        "/dev/ttyUSB0",
        "/dev/ttyUSB2",
        "/dev/ttyUSB3",
        "/dev/ttyUSB4",
    ]
    serialConnections = {
        'lidar' : None,
        'styr' : None,
        'sensor' : None,
        
    }
    if not useLidar:
        devSerials.pop()
        serialConnections.pop("lidar")
        
    check = 0
    
    styr_done = False
    lidar_done = not useLidar
    sensor_done = False
    while True:
        if check > 10:
            raise Exception("Unable to assign ports. RESTART AVR!!!")
            break
        for i in range(len(devSerials)):
            try:
                checkserial = serial.Serial(port=devSerials[i] ,baudrate=115200, timeout = 0.1)
            except:
                continue
            packet = bytearray()
            packet.append(0xFC)
            checkserial.write(packet)
            serialResponse = checkserial.read(1)
            response_int = int.from_bytes(serialResponse, byteorder='big')
            if response_int == 0xFA:
                serialConnections["styr"] = devSerials[i]
                styr_done = True
            elif styr_done == False:
                continue
            elif styr_done and not serialResponse:
                serialConnections["lidar"] = devSerials[i]
                lidar_done = True
            elif not lidar_done:
                continue
            elif styr_done and lidar_done and not response_int == 0xFA and not response_int == 0xFF:
                serialConnections["sensor"] = devSerials[i]
                sensor_done = True
            else:
                continue
            checkserial.close()
        
                
        if styr_done and sensor_done and lidar_done:
            break
        check+=1
        
    for i in serialConnections:
        print("Serial", i, ":", serialConnections[i] )
    
    return serialConnections


if __name__ == '__main__':

    if useSerial:
        # Ingen aning om denna fungerar, har ej testats 
        print("Checking Serial Ports")
        serialConnections = getSerial()

    with Manager() as manager:
        
        data = manager.dict()
        btns = manager.dict()
        scanList = manager.list()
        stearing = manager.list()
        stearing.append(25)
        stearing.append(25)
        
        velocity = manager.list()
        velocity.append(0)
        serverLidar = manager.list()

        data.update({
            "Wheel_Angle": 25,
            "Thrust": 25,
            "Velocity": 0,
            "Distance": 0,
            "Direction": 0,
            "Gear": 0,
            })
        
        btns.update({
            "resetToggle": 0,
            "autoOnOffToggle": 0,
            "upToggle": 0,
            "downToggle": 0,
            "leftToggle": 0,
            "rightToggle": 0,
            "gear": 0,
            })
        
        serverProcess = Process(target=server.run, args=(data, btns, serverLidar))
        if useSerial:
            controlProcess = Process(target=control.main, args=(data, btns, scanList, serialConnections["styr"], serialConnections["sensor"], stearing, velocity, serverLidar))
            serialProcess = Process(target=control.sendDataTest, args=(stearing, serialConnections["styr"]))
            receiveProcess = Process(target=control.receiveData, args=(velocity, serialConnections["sensor"]))
 
        else:
            controlProcess = Process(target=control.test, args=(data, btns, scanList))
        if useLidar: 
            lidarProcess = Process(target=mapping.findNodes, args=(scanList, serialConnections["lidar"], velocity))
        else:
            lidarProcess = Process(target=mapping.main, args=(scanList, 0))
        
        if useSerial:
            serialProcess.start()
            receiveProcess.start()
        serverProcess.start()
        controlProcess.start()
        lidarProcess.start()
        
        if useSerial:
            serialProcess.join()
            receiveProcess.join()
        serverProcess.join()
        controlProcess.join()
        lidarProcess.join()
