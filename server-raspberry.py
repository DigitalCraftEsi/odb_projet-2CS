import eventlet
import socketio
import serial
import time
import os
from datetime import datetime
# next Step in the recipe to send it to arduino
def nextStep(i,data):
    global quantity
    if i ==2:
        # Verify if the quantity is diffrent then 0
        if(data['coffee']!= 0):
            quantity = int(data['coffee'])*10/3
            # execute the current step
            switchSteps(i)
            i = i + 1
    elif i == 3:
        # Verify if the quantity is diffrent then 0
        if(data['milk']!= 0):
            quantity = int(data['coffee'])*10/5
            # execute the current step
            switchSteps(i)
            i = i + 1
    elif i == 4:
        # Verify if the quantity is diffrent then 0
        if(data['tea']!= 0):
            quantity = int(data['coffee'])*10/5
            # execute the current step
            switchSteps(i)
            i = i + 1
    elif i == 5:
        # Verify if the quantity is diffrent then 0
        if(data['sucre']!= 0):
            quantity = int(data['sucre'])*10/5
            # execute the current step
            switchSteps(i)
            i = i + 1
    elif i == 6:
        switchSteps(i)
        i = i + 1
    else:
        i = i + 1
def switchSteps(argument):
    global End
    global i
    global file
    if argument == 1:
        # if current step is one prepare the water
        print("Case 1")
        Received = False
        # send water to arduino to prepare water
        ser.write(b"Prepare water\n")
        while not(Received):
            line = ser.readline().decode('utf-8').rstrip()
            # if line received is heiight the next line is the level of ingredient
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # save the level in the log file
                file.write("water = " + line + "|")
                print("Height = ")
                statistics['water'] = line
            if line.endswith("Prepared"):               
                Received = True
                i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 2:
        # if current step is 2 prepare the coffee
        print("Case 2")
        Received = False
        # send coffee to arduino to prepare coffee
        ser.write(b"coffee\n")
        while not(Received):
            line = ser.readline().decode('utf-8').rstrip()
            # if line received is heiight the next line is the level of ingredient
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # save the level in the log file
                file.write("coffee = " + line + "|")
                statistics['coffee'] = line
            if line.endswith("Prepared"):               
                Received = True
                i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 3:
        # if current step is 3 prepare the milk
        print("Case 3")
        Received = False
        # send milk to arduino to prepare milk
        ser.write(b"milk\n")
        while not(Received):
            line = ser.readline().decode('utf-8').rstrip()
            # if line received is heiight the next line is the level of ingredient
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # save the level in the log file
                file.write("milk = " + line + "|")
                statistics['milk'] = line
            if line.endswith("Prepared"):               
                Received = True
                i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 4:
        # if current step is 4 prepare the sugar
        print("Case 4")
        Received = False
        # send sugar to arduino to prepare sugar
        ser.write(b"sugar\n")
        while not(Received):
            line = ser.readline().decode('utf-8').rstrip()
            # if line received is heiight the next line is the level of ingredient
            if line.endswith("Height"): 
                line = ser.readline().decode('utf-8').rstrip()
                # save the level in the log file
                file.write("sugar = " + line + "|")
                statistics['sugar'] = line
            if line.endswith("Prepared"):               
                Received = True
                i = i + 1
            print(line)
            time.sleep(1)
    elif argument == 5:
        # if current step is 5 mix the ingredients
        print("Case 5")
        Received = False
        # send coffee to arduino to mix
        ser.write(b"mix\n")
        while not(Received):
            line = ser.readline().decode('utf-8').rstrip()
            if line.endswith("Done"):               
                Received = True
                i = i + 1
            print(line)
            time.sleep(1)
    else:
        End = True
        file.write("\n")
        print("Default case")
        
global ser
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()


# Create a Socket.IO server instance
sio = socketio.Server()

# Wrap the Socket.IO server with an eventlet WSGI server
app = socketio.WSGIApp(sio)

# Define a Socket.IO event handler
def connect(sid, environ):
    print('Client connected:', sid)
# get the statistics from arduino and send it to app1
@sio.on('statistics-event')
def getStatistics(sid, data):
    Received = False
    # request the arduino to send statistics by sending the string statistics
    ser.write(b"statistics\n")
    while not(Received):
        line = ser.readline().decode('utf-8').rstrip()
        # when receiving a string ends with 'are' save the next line in variable statistics 
        if line.endswith("are"):
            line = ser.readline().decode('utf-8').rstrip()
            statistics = line               
        if line.endswith("Done"):            
            Received = True
        print(line)
        time.sleep(1)  
    # send the statistics to app1
    sio.emit('statistics_event', {'statistics': statistics}, room=sid)
# unlock the distributer
@sio.on('unlock-event')
def unlockDistributeur(sid, data):
    # infrom arduino to unlock disrtibuter
    Received = False
    ser.write(b"unlock\n")
    while not(Received):
        line = ser.readline().decode('utf-8').rstrip()
        if line.endswith("Unlocked"):               
            Received = True
        print(line)
        time.sleep(1)  
    # wait 5 seconds and reinform arduino to lock the distibuter
    time.sleep(5)    
    Received = False
    ser.write(b"lock\n")
    while not(Received):
        line = ser.readline().decode('utf-8').rstrip()
        if line.endswith("lock"):               
            Received = True
        print(line)
        time.sleep(1) 

# Prepare the command
@sio.on('prepare-beverage')
def handleMessage(sid, data):
    # get the current date to create or save the histroy
    current_date = datetime.now().date()
    current_time = datetime.now()
    time_string = current_time.strftime("%H:%M:%S")
    date_string = str(current_date)
    # creat file with current date
    path = "/home/digitalcraft/Desktop/log/"+ date_string + ".txt"
    # open the file
    global file
    file = open(path,"a+")
    file.write(time_string + ": ")
    global statistics
    # initilize statistics 
    statistics = {
        "coffee":0,
        "milk":0,
        "sugar":0,
        "water":0
    }
    print('Command is preparing !')
    # Initilize the end to false and the first step to one
    global End
    global i
    global quantity
    quantity = 0
    End = False
    i = 1
    # while not the end of steps reexcute the nextstep
    while not(End):
        nextStep(i)
        time.sleep(1)
    print("work done")
    # close the file when the command is done
    file.close()
    # send the new statistics to app1
    sio.emit('response_event', {'statistics': statistics}, room=sid)

# Run the server
if __name__ == '__main__':
    # run a server on port 8080 to listen to events of socket.io 
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
