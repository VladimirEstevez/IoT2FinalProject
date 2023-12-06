#!/usr/bin/env python
# Import necessary libraries
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

# Define GPIO pins
led_pin = 24
fan_gpio_pin = 25
pump_gpio_pin = 4

# Set GPIO mode and setup LED pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

# Define Dweet.io URL and thing name
dweetIO = "https://dweet.io/dweet/for/"  # common url for all users (post)
myThing = "vladimir_raspi2"  # replace with you OWN thing name
n = 15  # starting counter
light_switch_status = False

# Function to turn on a motor for a specific duration


def turn_on_motor(duration, gpio_pin):
    # Set the GPIO pin to HIGH. This starts the motor.
    GPIO.output(gpio_pin, GPIO.HIGH)
    # Pause the program for the duration specified by the user.
    # The motor continues to run during this time.
    time.sleep(duration)
    # After the pause, set the GPIO pin to LOW. This stops the motor.
    GPIO.output(gpio_pin, GPIO.LOW)

# Function to get temperature threshold from user


def get_temperature_threshold():
    # Start an infinite loop
    while True:
        try:
            # Prompt the user to enter the desired temperature threshold
            # The input is converted to a float immediately
            temperature_threshold = float(
                input("Please enter the desired Temperature Threshold: "))
            # If the conversion to float is successful, return the temperature threshold
            return temperature_threshold
        except ValueError:
            # If the conversion to float fails (which means the user didn't enter a number), print an error message
            print("That's not a valid number. Please enter a number.")

# Function to get moisture threshold from user


def get_moisture_threshold():
    # Start an infinite loop
    while True:
        try:
            # Prompt the user to enter the desired moisture threshold
            # The input is converted to a float immediately
            moisture_threshold = float(
                input("Please enter the desired Moisture Threshold: "))
            # If the conversion to float is successful, return the moisture threshold
            return moisture_threshold
        except ValueError:
            # If the conversion to float fails (which means the user didn't enter a number), print an error message
            print("That's not a valid number. Please enter a number.")


# Get temperature and moisture thresholds
temperature_threshold = get_temperature_threshold()
moisture_threshold = get_moisture_threshold()

# Function to initialize the setup


def init():
    # Setup the ADC0832 module
    ADC0832.setup()
    # Setup the LED pin as an output pin
    GPIO.setup(LED_PIN, GPIO.OUT)
    # Set the LED pin to LOW (LED off)
    GPIO.output(LED_PIN, GPIO.LOW)

    # Setup the pump and fan GPIO pins as output pins
    GPIO.setup(pump_gpio_pin, GPIO.OUT)
    GPIO.setup(fan_gpio_pin, GPIO.OUT)
    # Set the pump and fan GPIO pins to LOW (pump and fan off)
    GPIO.output(pump_gpio_pin, GPIO.LOW)
    GPIO.output(fan_gpio_pin, GPIO.LOW)


# MQTT configuration
# The client ID must be unique within the AWS account
clientID = "554264267537"
# The endpoint is obtained from the settings page in the AWS IoT console
endpoint = "adfktbxo0eq6k-ats.iot.us-east-1.amazonaws.com"
port = 8883
topic = "tb/aws/iot/sensors/freezer-432"

# Initialize the MQTT client
mqttc = AWSIoTMQTTClient(clientID)
# Configure the endpoint and port
mqttc.configureEndpoint(endpoint, port)
# Configure the credentials
mqttc.configureCredentials(
    "./AmazonRootCA1.pem", "./raspberry-private.pem.key", "./raspberry-certificate.pem.crt")

# Function to send a message to the IoT topic
def send_data(message):
    # Publish the message to the topic
    mqttc.publish(topic, json.dumps(message), 0)
    print("Message Published")


# Main loop function
def loop():
    tmp = 0.0
    # Start an infinite loop
    while True:
        # Read the temperature, humidity, and light level
        tmp = SensorMethods.ds18b20Read()
        moisture = SensorMethods.humididtyRead()
        light = SensorMethods.getLight()
        print("MOISTURE in %", moisture)
        print("TEMPERATURE", tmp)
        print("light", light)

        # If the temperature is above the threshold, turn on the fan for 30 seconds
        if (tmp > temperature_threshold):
            # turn the fan motor for 30 seconds
            fan_thread = threading.Thread(
                target=turn_on_motor, args=(30, fan_gpio_pin))
            fan_thread.start()

            # If the moisture is below the threshold, turn on the pump for 3 seconds
        if (moisture < moisture_threshold):
            # turn the Pump on for 3 seconds
            pump_thread = threading.Thread(
                target=turn_on_motor, args=(3, pump_gpio_pin))
            pump_thread.start()

        # If the light level is low, turn on the LED
        if light == False:
            GPIO.output(led_pin, GPIO.HIGH)
        else:
            GPIO.output(led_pin, GPIO.LOW)
        
        # Prepare the data to be sent
        obj_to_send = {
            "val0": moisture,
            "val1": tmp,
            "val2": light
        }
        
        # Send the data
        send_data(obj_to_send)
        # Wait for 20 seconds before the next loop
        time.sleep(20)

# This line checks if this script is being run directly or being imported as a module
# If the script is being run directly, then __name__ is set to '__main__'
if __name__ == '__main__':
    # Call the init function to setup the GPIO pins and MQTT client
    init()
    try:
        # Connect to the MQTT broker
        mqttc.connect()
        print("Connect OK!")

        # Define a callback function that will be called when a message is received from the broker
        def callback(client, userdata, message):
            # Print the received message and the topic it was published on
            print("Received a new message: ")
            print(message.payload)
            print("from topic: ")
            print(message.topic)
            print("----------------------")

        # Subscribe to the topic "down/test" with QoS level 1
        # The callback function will be called whenever a message is received on this topic
        subscription_topic = "down/test"
        mqttc.subscribe(subscription_topic, 1, callback)

        # Start the main loop
        loop()
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, disconnect from the MQTT broker and cleanup the GPIO and ADC0832
        mqttc.disconnect()
        ADC0832.destroy()
        print('The end !')