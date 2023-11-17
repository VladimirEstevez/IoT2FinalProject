#!/usr/bin/env python
import ADC0832
import time
import math
import RPi.GPIO as GPIO
import requests
import dweepy
import threading
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time




LED_PIN = 23
T_THRESHOLD = 30 

dweetIO = "https://dweet.io/dweet/for/" #common url for all users (post) 
myThing = "vladimir_raspi2" #replace with you OWN thing name
n = 15 #starting counter
temp_to_send = 25
light_to_send = 1
temperature='temperature'
humidity='light'



def init():
    ADC0832.setup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)
    
    
    
    # MQTT config (clientID must be unique within the AWS account)
clientID = "554264267537"
endpoint = "adfktbxo0eq6k-ats.iot.us-east-1.amazonaws.com" #Use the endpoint from the settings page in the IoT console
port = 8883
topic = "tb/aws/iot/sensors/freezer-432"

# Init MQTT client
mqttc = AWSIoTMQTTClient(clientID)
mqttc.configureEndpoint(endpoint,port)
mqttc.configureCredentials("./AmazonRootCA1.pem","./raspberry-private.pem.key","./raspberry-certificate.pem.crt")

# Send message to the iot topic
def send_data(message):
    mqttc.publish(topic, json.dumps(message), 0)
    print("Message Published")
    
    
def loop():
    light_on = False  
    while True:
        
        res1 = ADC0832.getADC(0)
        # Vr = 3.3 * res1 / 255
        # print("int :  ",Vr)
        Vr2 = 3.3 * float(res1) / 255
        #print("float : ", Vr2, "\n")
        if Vr2 >0:
            
            Rt = (10000 * 3.3 /  Vr2) - 10000

            #Rt = 10000 * Vr / (3.3 - Vr)
            #print ('Rt : %.2f' %Rt)
            if Rt > 0:  # Add this line
                temp = 1/(((math.log(Rt / 10000)) / 3455) + (1 / (273.15+25)))
               # print ('Temp : %.2f' %temp)
                Cel = temp - 273.15
                temp_to_send = '{:.2f}'.format(Cel) 
                Fah = Cel * 1.8 + 32
                #print ('Celsius: %.2f C  Fahrenheit: %.2f F' % (Cel, Fah))
                
                    
            else:  # Add this line
                print('Rt is zero or negative')
                     
        res2 = ADC0832.getADC(1)
        vol = 3.3/255 * res2
        light_to_send = vol
        
       # print ('analog value: %03d  || LIGHT SPECTRUM voltage: %.2fV' %(res2, vol))
         
        obj_to_send = {
                "val0": "loaded",
    "val1": temp_to_send,
    "val2": light_to_send,
    "val3": 0
            }
        
        send_data(obj_to_send)
       
                
        time.sleep(1)

if __name__ == '__main__':
    init()
    try:
        
        mqttc.connect()
        print("Connect OK!")
        

        # Define callback function
        def callback(client, userdata, message):
            print("Received a new message: ")
            print(message.payload)
            print("from topic: ")
            print(message.topic)
            print("----------------------")

        # Subscribe to the topic
        subscription_topic = "down/test"
        mqttc.subscribe(subscription_topic, 1, callback)

       
        
        
        loop()
    except KeyboardInterrupt: 
        mqttc.disconnect()
        ADC0832.destroy()
        print ('The end !')
