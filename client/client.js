﻿const socket = new WebSocket("ws://10.42.0.1:3800");// 10.42.0.1:3800");
let passed = true;
let lap = 0;
   // data values 
let data = {
    Wheel_Angle: 0,
    Thrust: 0,
    Velocity: 0,
    Distance: 0,
    Direction: 0,
    Gear: 1,
};

let btns = {
    resetToggle:0, 
    autoOnOffToggle:0, 
    upToggle:0, 
    downToggle:0,
    leftToggle:0,
    rightToggle:0,
    gear:1,
};

let unit = {
    Wheel_Angle: "degrees",
    Thrust: "",
    Velocity: "m/s",
    Distance: "cm",
    Direction: "degrees",
    Gear: "",
}

let scanArray = [];


setInterval(() => {
    socket.send(JSON.stringify(btns));
}, 50);

socket.onopen = (event) => {
  console.log('Connected to the WebSocket server');
};



socket.addEventListener('message', (event) => {
    data.Wheel_Angle = JSON.parse(event.data).Wheel_Angle-25;
    data.Thrust = JSON.parse(event.data).Thrust-25;
    data.Velocity = JSON.parse(event.data).Velocity;
    data.Distance = Math.floor(JSON.parse(event.data).Distance/10);
    data.Gear = JSON.parse(event.data).Gear;
    scanArray = JSON.parse(event.data).Lidar;
    updateInfo(); 
});

setInterval(() => {
    drawMap(scanArray);
}, 25);


function drawMap(scanArray){
    let map = document.getElementById('canvas');
    const context = map.getContext('2d');


    let scaling = 6000
    map.style.width = "100%";
    map.style.height = "100%";
    map.width = map.offsetWidth;
    map.height = map.offsetHeight;
    const centerX = map.width / 2;
    const centerY = map.height / 2;
    
    context.clearRect(0,0, map.width, map.height);
    context.fillStyle = "white";

    let carX = centerX;
    let carY = centerY;
    context.fillRect(centerX, centerY, 10, 10);
    


    scanArray.forEach(item => {
        console.log(item);
        if(item[0] == "gate"){
            xCoord1 = centerX + (item[1]/scaling) * map.height;
            yCoord1 = centerY - (item[2]/scaling) * map.height;
            xCoord2 = centerX + (item[4]/scaling) * map.height;
            yCoord2 = centerY - (item[5]/scaling) * map.height;
            
            
            context.rect(xCoord1, yCoord1, 5, 5);
            if(item[3] == "big"){
                context.fillStyle = "aqua";
    
            }
            else if(item[3] == "small"){
                context.fillStyle = "coral";
            }
           

            context.fillRect(xCoord1, yCoord1, 5, 5);

            context.rect(xCoord2, yCoord2, 5, 5);

            if(item[6] == "big"){
                context.fillStyle = "aqua";
    
            }
            else if(item[6] == "small"){
                context.fillStyle = "coral";
            }

            context.fillRect(xCoord2, yCoord2, 5, 5);

            if(item[3] == "big" && item[6] == "big"){
                passed=false;
            }
            
            
            //context.fillRect((xCoord2+xCoord1)/2, (yCoord2+yCoord1)/2, 5, 5);
            //console.log((xCoord2+xCoord1)/2, (yCoord2+yCoord1)/2);

            //context.fillStyle = "yellow";


            //let vec2 = [-(yCoord1 - (yCoord2+yCoord1)/2), (xCoord1 - (xCoord2+xCoord1)/2)];
            //context.fillRect(vec2[0] + (xCoord2+xCoord1)/2, vec2[1] + (yCoord2+yCoord1)/2, 5, 5);
            //console.log(vec2[0] + (xCoord2+xCoord1)/2, vec2[1] + (yCoord2+yCoord1)/2);
            //console.log((item[4]+item[1])/2);
            //console.log(Math.atan(((item[4]+item[1])/2)/((item[5]+item[2])/2))*(180/Math.PI));
            
            context.fillStyle = "yellow";
            if (scanArray[0] == item){
                xCoord3 = centerX + (item[7][0]/scaling) * map.height;
                yCoord3 = centerY - (item[7][1]/scaling) * map.height;
                
                xCoord4 = centerX + (item[9][0]/scaling) * map.height;
                yCoord4 = centerY - (item[9][1]/scaling) * map.height;
                if(item[10] == "straight"){
                    previous = 0;
                }
                else if(item[10] == "left"){
                    previous = -45;
                }
                else if(item[10] == "right"){
                    previous = 45;
                }
                else{
                    previous = 0;
                }
                
                context.fillRect(xCoord3-2, yCoord3-2, 4, 4);
                context.fillRect(xCoord4-2, yCoord4-2, 4, 4);
                
                context.strokeStyle = "blue";
                
                context.beginPath();
                context.arc(xCoord3, yCoord3, (item[8]/scaling) * map.height, 0, 2*Math.PI);
                context.stroke();
            }
            else{
                context.strokeStyle = "white";
            }
            if(item[3]=="big" && item[6]=="big"){
                context.strokeStyle = "green";
            }
            context.beginPath();
            context.moveTo(xCoord1+2, yCoord1+2);
            context.lineTo(xCoord2+2, yCoord2+2);
            context.lineWidth = 2;
            context.stroke();
        }


        else if(item[0] = "backGate"){
                
                if(!passed && item[3] == "big" && item[6] == "big"){
                    lap++;
                    passed=true;
                    if(lap==4){btns.autoOnOffToggle=0;}
                }


                xCoord5 = centerX + (item[1]/scaling) * map.height;
                yCoord5 = centerY - (item[2]/scaling) * map.height;
                xCoord6 = centerX + (item[4]/scaling) * map.height;
                yCoord6 = centerY - (item[5]/scaling) * map.height;
            
            
                context.rect(xCoord5, yCoord5, 5, 5);
                if(item[3] == "big"){
                    context.fillStyle = "aqua";
        
                }
                else if(item[3] == "small"){
                    context.fillStyle = "coral";
                }
            

                context.fillRect(xCoord5, yCoord5, 5, 5);

                context.rect(xCoord6, yCoord6, 5, 5);
                
                if(item[6] == "big"){
                    context.fillStyle = "aqua";
        
                }
                else if(item[6] == "small"){
                    context.fillStyle = "coral";
                }
                context.strokeStyle = "red";
                context.fillRect(xCoord6, yCoord6, 5, 5);
                context.beginPath();
                context.moveTo(xCoord5+2, yCoord5+2);
                context.lineTo(xCoord6+2, yCoord6+2);
                context.lineWidth = 2;
                context.stroke();
        }


        else if(item[0] == "cone"){
            xCoord = centerX + (item[1]/scaling) * map.height;
            yCoord = centerY - (item[2]/scaling) * map.height;
            if(item[3] == "big"){
                context.fillStyle = "green";
    
            }
            else if(item[3] == "small"){
                context.fillStyle = "red";
            }
            context.fillRect(xCoord, yCoord, 5, 5);
        
        }
     });
    context.beginPath();
    context.moveTo(carX + 5, carY + 5);
    rad = data.Wheel_Angle * (Math.PI / 180);
    context.lineTo(carX + 5 + Math.sin(rad)*(5 + data.Thrust * 5), carY + 5 - Math.cos(rad)*(data.Thrust * 5 + 5));
    context.strokeStyle = "white";
    context.lineWidth = 2;
    context.stroke();
}


function updateInfo(){
    let x = 0;
    for (child of document.getElementById('data-content').children){
        
        const properties = Object.keys(data);
        const propertyName = properties[x];
        let propertyValue = data[propertyName];

        if(propertyName=="Gear"){
            propertyValue = btns["gear"];
        }

        child.innerHTML = `<strong>${propertyName}:</strong> ${propertyValue} </strong> ${unit[propertyName]}`;
        x++;
    }
    document.getElementById('data-content').children[x-1].innerHTML = `Lap:<strong>${lap}`;

}
  
document.addEventListener('DOMContentLoaded', function() {
    
    // VARIABLES AND LISTENERS RELATED TO DATA

    // Loop through the data and create HTML elements to display it
    for (const variable in data) {
        const variableElement = document.createElement('div');
        variableElement.innerHTML = variable;
        document.getElementById('data-content').appendChild(variableElement);
    }
    updateInfo();

    // VARIABLES AND LISTENERS RELATED TO BUTTONS AND KEYBOARD PRESSES

    // Variables
    let resetMessage = document.getElementById('resetMessage');
    let autoOnOffMessage = document.getElementById('autoOnOffMessage');
    let upMessage = document.getElementById('upMessage');
    let downMessage = document.getElementById('downMessage');
    let leftMessage = document.getElementById('leftMessage');
    let rightMessage = document.getElementById('rightMessage');
    // // End    

    // Event listener for a keyboard key presses
    document.addEventListener('keydown', function(event) {
        switch (event.key) {
            case 'PageUp':
                resetMessage.style.display = 'block';
                btns.resetToggle = 1;
                btns.gear = 1;
                lap = 0;
                break;
            case 'PageDown':
                var event = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                });
                autoOnOffButton.dispatchEvent(event);   
                break;
            case 'ArrowUp':
                if (btns.downToggle != 1){
                    upMessage.style.display = 'block';
                    btns.upToggle = 1;
                    }                
                break;
            case 'ArrowDown':
                if (btns.upToggle != 1){
                    downMessage.style.display = 'block';
                    btns.downToggle = 1;
                    }
                break;
            case 'ArrowLeft':
                if (btns.rightToggle != 1){
                    leftMessage.style.display = 'block';
                    btns.leftToggle = 1;
                    }                
                break;
            case 'ArrowRight':
                if (btns.leftToggle != 1){
                    rightMessage.style.display = 'block';
                    btns.rightToggle = 1;
                    }
                break;
            case '0':
                btns.gear = 0;
                break;
            case '1':
                btns.gear = 1;
                break;
            case '2':
                btns.gear = 2;
                break;
            case '3':
                btns.gear = 3;
                break;
            case '4':
                btns.gear = 4;
                break;
            case '5':
                btns.gear = 5;
                break;
            }
    });
    
    // Code for keyboard release actions
       
    // Event listener for keyboard key releases
    document.addEventListener('keyup', function(event) {
        switch (event.key) {
            case 'PageUp':
                resetMessage.style.display = 'none';
                btns.resetToggle = 0;
                break;
            case 'ArrowUp':
                upMessage.style.display = 'none';
                btns.upToggle = 0;
                break;
            case 'ArrowDown':
                downMessage.style.display = 'none';
                btns.downToggle = 0;
                break;
            case 'ArrowLeft':
                leftMessage.style.display = 'none';
                btns.leftToggle = 0;
                break;
            case 'ArrowRight':
                rightMessage.style.display = 'none';
                btns.rightToggle = 0;
                break;
        }
    });
    // End
});

function resetFunction() {
    if (btns.resetToggle == 0) {
        btns.resetToggle = 1;
        resetMessage.style.display = 'block';
        btns.gear = 0;
    } else {
        btns.resetToggle = 0;
        resetMessage.style.display = 'none';
    }
}

function autoOnOffFunction() {
    if (btns.autoOnOffToggle == 0) {
        btns.autoOnOffToggle = 1;
        autoOnOffMessage.style.display = 'block';
        
    } else {
        btns.gear = 1;
        btns.autoOnOffToggle = 0;
        autoOnOffMessage.style.display = 'none';
    }
}

function upFunction() {
    if (btns.upToggle == 0) {
        btns.upToggle = 1;
        upMessage.style.display = 'block';
    } else {
        btns.upToggle = 0;
        upMessage.style.display = 'none';
    }
}

function downFunction() {
    if (btns.downToggle == 0) {
        btns.downToggle = 1;
        downMessage.style.display = 'block';
    } else {
        btns.downToggle = 0;
        downMessage.style.display = 'none';
    }
}

function leftFunction() {
    if (btns.leftToggle == 0) {
        btns.leftToggle = 1;
        leftMessage.style.display = 'block';
    } else {
        btns.leftToggle = 0;
        leftMessage.style.display = 'none';
    }
}

function rightFunction() {
    if (btns.rightToggle == 0) {
        btns.rightToggle = 1;
        rightMessage.style.display = 'block';
    } else {
        btns.rightToggle = 0;
        rightMessage.style.display = 'none';
    }
}
