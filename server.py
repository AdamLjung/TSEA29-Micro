import asyncio
import websockets
import json
import functools

port = 3800

async def send_data_to_client(websocket, path, dataShared, btnsShared, scanListShared):
    async for message in websocket:
        clientBtns = json.loads(message)

        btnsShared.update(clientBtns)
    
        outputData = dataShared.copy()
        temp= scanListShared[:]
        #print(temp)
        outputData.update({"Lidar": temp})
        await websocket.send(json.dumps(outputData))

def run(dataShared, btnsShared, scanListShared):
    start_server = websockets.serve(functools.partial(send_data_to_client, dataShared=dataShared, btnsShared=btnsShared, scanListShared=scanListShared), "0.0.0.0", port)
    print("Server is running on port ", port)

    try:
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Server Closed by Cntr C")
