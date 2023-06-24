import threading
import eventlet
import socketio
import serial
import time
import os
import json
from datetime import datetime

# The function that decides the next step in the recipe
def nextStep(data):
    global quantity
    global i
    if i == 1:
        # if the quntity of water diffrent of 0 launch the step of preparing water
        if(data['eau']!= 0):
            quantity = int(data['eau'])*1
            switchSteps(i,quantity)
        i = i + 1
    if i == 2:
        # if the quntity of coffee diffrent of 0 launch the step of preparing coffee
        if(data['cafe']!= 0):
            quantity = int(data['cafe'])*1
            switchSteps(i,quantity)
        i = i + 1
        print("next : ",i)
    elif i == 3:
        # if the quntity of milk diffrent of 0 launch the step of preparing milk
        if(data['lait']!= 0):
            quantity = int(data['lait'])*1
            switchSteps(i,quantity)
        i = i + 1
    elif i == 4:
        # if the quntity of sugar diffrent of 0 launch the step of preparing sugar
        if(data['sucre']!= 0):
            quantity = int(data['sucre'])*1
            switchSteps(i,quantity)
        i = i + 1
    elif i == 5:
        # the next step is mixing the ingredients
        switchSteps(i,quantity)
        i = i + 1
    elif i == 6:
        # the next step is the final one
        switchSteps(i,quantity)
def switchSteps(argument,quantity):
    global End
    global j
    global i
    global file
    if argument == 1:
        # if the step is preparing water , a string is sent to arduino to prepare water
        print("Case 1")
        Received = False
        ser.write(b"water\n")
        while not(Received):
#           print("waiting")
            line = ser.readline().decode('utf-8').rstrip()
            # when recieving the string "Hight" , the value of sensor is sent by the arduino
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # The level of the sensor is saved in the log file also saved to sent to app1
                file.write("water = " + line + "|")
                statistics['water']=line
            # Whene recieving the message "Prepared" it goes to the next step 
            if line.endswith("Prepared"):               
                Received = True
#                i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 2:
        # if the step is preparing coffee , a string is sent to arduino to prepare coffee
        print("Case 2")
        Received = False
        ser.write(b"coffee\n")
        while not(Received):
#            print("waiting")
            line = ser.readline().decode('utf-8').rstrip()
            # when recieving the string "Hight" , the value of sensor is sent by the arduino
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # The level of the sensor is saved in the log file also saved to sent to app1
                file.write("coffee = " + line + "|")
                statistics['coffee']=line
            # Whene recieving the message "Prepared" it goes to the next step 
            if line.endswith("Prepared"):               
                Received = True
#               i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 3:
        # if the step is preparing coffee , a string is sent to arduino to prepare coffee
        print("Case 3")
        Received = False
        ser.write(b"milk\n")
        while not(Received):
#            print("waiting")
            line = ser.readline().decode('utf-8').rstrip()
            # when recieving the string "Hight" , the value of sensor is sent by the arduino
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # The level of the sensor is saved in the log file also saved to sent to app1
                file.write("milk = " + line + "|")
                statistics['milk']=line
            # Whene recieving the message "Prepared" it goes to the next step 
            if line.endswith("Prepared"):               
                Received = True
#               i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 4:
        print("Case 4")
        Received = False
        ser.write(b"sugar\n")
        while not(Received):
#           print("waiting")
            line = ser.readline().decode('utf-8').rstrip()
            # when recieving the string "Hight" , the value of sensor is sent by the arduino
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # The level of the sensor is saved in the log file also saved to sent to app1
                file.write("sugar = " + line + "|")
                statistics['sugar']=line
            # Whene recieving the message "Prepared" it goes to the next step 
            if line.endswith("Prepared"):               
                Received = True
#               i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 5:
        # if the step is preparing coffee , a string is sent to arduino to prepare coffee
        print("Case 5")
        Received = False
        ser.write(b"mix\n")
        while not(Received):
#            print("waiting")
            line = ser.readline().decode('utf-8').rstrip()
            # Whene recieving the message "done" it goes to the next step 
            if line.endswith("done"):               
                Received = True
#               i = i + 1
            print(line)
            time.sleep(1)
    else:
        End = True
        file.write("\n")
#        print(End)
        print("Default case")

# Initialize the communication serial with arduino        
global ser
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()


# Create a Socket.IO server instance
sio = socketio.Server()

# Wrap the Socket.IO server with an eventlet WSGI server
app = socketio.WSGIApp(sio)

# Socket.IO connect event 
@sio.event
def connect(sid, environ):
    path = "/home/digitalcraft/Desktop/code.txt"
    file = open(path,"a+")
    file.seek(0)
    line = file.readline()
    print(line)
    sio.emit('code_event', line, room=sid)
# Socket.IO statistics event 
@sio.on('statistics-event')
def getStatistics(sid,data):
    Received = False
    ser.write(b"statistics\n")
    while not(Received):
#           print("waiting")
        line = ser.readline().decode('utf-8').rstrip()
        if line.endswith("are"):  
            line = ser.readline().decode('utf-8').rstrip()
            json_statistics = json.loads(line)
        if line.endswith("done"):               
            Received = True
        print(line)
        time.sleep(1)
    # Convert the distance recieved from arduino into pourcentage
    json_statistics['coffee'] = ((10-json_statistics['coffee'])*100)/10
    json_statistics['milk'] = ((10-json_statistics['milk'])*100)/10
    json_statistics['water'] = ((10-json_statistics['water'])*100)/10
    json_statistics['sugar'] = ((10-json_statistics['sugar'])*100)/10
    print(json_statistics)
    string_statistics = json.dumps(json_statistics)
    print(string_statistics)
    # send the statistics to app1
    sio.emit('statistics-event',string_statistics , room=sid)

# Socket.IO power off the raspberry event 
@sio.on('powerOff-distribiteur')
def powerOfDistribiteur(sid,data):
    print("powering off")
    os.system("sudo shutdown now")

# Socket.IO unlock the distributerevent 
@sio.on('unlock-distribiteur')
def unlockDistribiteur(sid,data):
        # Send to arduino to unlock the distributer
        Received = False
        ser.write(b"unlock\n")
        while not(Received):
            line = ser.readline().decode('utf-8').rstrip()
            # When the distributer unlocked move to the locking part after 3 sec
            if line.endswith("unlocked"):               
                Received = True
            print(line)
            time.sleep(1)
        time.sleep(3)
        # Send to arduino to lock the distributer
        Received = False
        ser.write(b"lock\n")
        while not(Received):
#           print("waiting")
            line = ser.readline().decode('utf-8').rstrip()
            # When the distributer locked terminate the event
            if line.endswith("locked"):               
                Received = True
            print(line)
            time.sleep(1)
@sio.on('prepare-beverage')
def handleMessage(sid, data):
#    print(extra_argument)
    json_data = json.loads(data)
    #print(json_data)
    last_item = json_data[-1]
    # Extract the boissons sented by app1 and execute them one by one
    for item in json_data:
        print(item)
        print("Quntity : ",item['Quantite'])
        boissonnbr = 0
        # For the quantity specified by the client the boissons are prepared one by one 
        for k in range(item['Quantite']):
            boissonnbr = boissonnbr + 1 
            # Get the date of today to save the command in the log file correspend
            current_date = datetime.now().date()
            current_time = datetime.now()
            time_string = current_time.strftime("%H:%M:%S")
            date_string = str(current_date)
            path = "/home/digitalcraft/Desktop/log/"+ date_string + ".txt"
            global file
            # if the log file of today doesn't existe create it else it adds the line at the end
            file = open(path,"a+");
            file.write(time_string + ": ")
            global statistics
            # initilize the statistics structer
            statistics = {
                'milk' : 0,
                'coffee' : 0,
                'water' : 0,
                'sugar' : 0
            }
            global End
            global j
            global i
            global quantity
            quantity = 0
            End = False
            i = 1
            j = 0
            # while the last step didn't reached call next step and execute the correspended step
            while not(End):
                nextStep(item)
                time.sleep(1)
            # if the number of boissons are more then one and it's not the last boisson wait 5 seconds between the boisson and the next
            if(len(json_data)>1) and (item != last_item):
                time.sleep(5)
            elif(item == last_item):
                if(boissonnbr != item['Quantite']):
                    time.sleep(5)
    # when the process ends : close the file and send the event to app1 of done with the statistics
    print("work done")
    file.close()
    print("sendind done ")
    string_statistics = str(statistics)
    sio.emit('response_event',string_statistics , room=sid)
#run the server 
def run_server():
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
# Run the server
if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
