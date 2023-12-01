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
import SensorMethods
import threading

LED_PIN = 23
T_THRESHOLD = 30 
led_pin = 24
fan_gpio_pin = 25
pump_gpio_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

dweetIO = "https://dweet.io/dweet/for/" #common url for all users (post) 
myThing = "vladimir_raspi2" #replace with you OWN thing name
n = 15 #starting counter
light_switch_status = False

def turn_on_motor(duration, gpio_pin):
    GPIO.output(gpio_pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(gpio_pin, GPIO.LOW)

def get_temperature_threshold():
    while True:
        try:
            temperature_threshold = float(input("Please enter the desired Temperature Threshold: "))
            return temperature_threshold
        except ValueError:
            print("That's not a valid number. Please enter a number.")
            
def get_moisture_threshold():
    while True:
        try:
            moisture_threshold = float(input("Please enter the desired Moisture Threshold: "))
            return moisture_threshold
        except ValueError:
            print("That's not a valid number. Please enter a number.")

temperature_threshold = get_temperature_threshold()
moisture_threshold = get_moisture_threshold()

def init():
    ADC0832.setup()
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)
    
    GPIO.setup(pump_gpio_pin, GPIO.OUT)
    GPIO.setup(fan_gpio_pin, GPIO.OUT)
    GPIO.output(pump_gpio_pin, GPIO.LOW)
    GPIO.output(fan_gpio_pin, GPIO.LOW)
    
    
    
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
    tmp = 0.0
    while True:
        
        tmp = SensorMethods.ds18b20Read()
        moisture = SensorMethods.humididtyRead()
        light = SensorMethods.getLight()
        print("MOISTURE in %",moisture)
        print("TEMPERATURE",tmp)
        print("light", light)
        
        if(tmp > temperature_threshold):
            #turn the fan motor for 30 seconds
            fan_thread = threading.Thread(target=turn_on_motor, args=(30,fan_gpio_pin))
            fan_thread.start()
            
        if(moisture < moisture_threshold):
            #turn the Pump on for 3 seconds
            pump_thread = threading.Thread(target=turn_on_motor, args=(3,pump_gpio_pin))
            pump_thread.start()
        
        if light == False:
            GPIO.output(led_pin, GPIO.HIGH)
        else:
            GPIO.output(led_pin, GPIO.LOW)
        
        obj_to_send = {
                "val0": moisture,
                "val1": tmp,
                "val2": light
            }
        
        send_data(obj_to_send)
        time.sleep(20)

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



