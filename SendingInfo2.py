#!/usr/bin/env python
import tkinter as tk
from tkinter import ttk
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
import smtplib
from email.mime.text import MIMEText

led_pin = 24
fan_gpio_pin = 25
pump_gpio_pin = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

dweetIO = "https://dweet.io/dweet/for/" #common url for all users (post) 
myThing = "vladimir_raspi2" #replace with you OWN thing name
n = 15 #starting counter
light_switch_status = False

class GreenhouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Greenhouse Control")
        
        self.led_status = False
        self.temperature_threshold_var = tk.DoubleVar(value=temperature_threshold)
        self.moisture_threshold_var = tk.DoubleVar(value=moisture_threshold)

        # Create LED control button
        self.led_button = tk.Button(root, text="Toggle LED", command=self.toggle_led)
        self.led_button.pack(pady=20)
        
        self.fan_button = tk.Button(root, text="Toggle Fan", command=self.toggle_fan)
        self.fan_button.pack(pady=10)

        # Create Pump control button
        self.pump_button = tk.Button(root, text="Toggle Pump", command=self.toggle_pump)
        self.pump_button.pack(pady=10)


    def toggle_led(self):
        # Toggle LED status
        self.led_status = not self.led_status

        # Control the actual LED based on the status
        GPIO.output(led_pin, GPIO.HIGH if self.led_status else GPIO.LOW)
        
    def toggle_fan(self):
        # Toggle Fan status
        fan_status = GPIO.input(fan_gpio_pin)
        GPIO.output(fan_gpio_pin, GPIO.LOW if fan_status else GPIO.HIGH)

    def toggle_pump(self):
        # Toggle Pump status
        pump_status = GPIO.input(pump_gpio_pin)
        GPIO.output(pump_gpio_pin, GPIO.LOW if pump_status else GPIO.HIGH)
        
        
def create_gui():
    root = tk.Tk()
    root.geometry("200x250")
    app = GreenhouseApp(root)
    root.mainloop()


def send_email(subject, message, sender_email, recipient_emails, smtp_server, smtp_port, username, password):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipient_emails)

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(sender_email, recipient_emails, msg.as_string())
    server.quit()


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
            moisture_threshold = float(input("Please enter the desired Moisture Threshold in %: "))
            return moisture_threshold
        except ValueError:
            print("That's not a valid number. Please enter a number.")
            
def get_user_input():
    sender_email = input("Enter your email address (sender): ")
    
    recipients = input("Enter recipient email(s), separated by commas: ")
    recipient_emails = [email.strip() for email in recipients.split(',')]

    google_app_password = input("Enter your Google App password: ")

    return sender_email, recipient_emails, google_app_password

temperature_threshold = get_temperature_threshold()
moisture_threshold = get_moisture_threshold()
sender_email, recipient_emails, google_app_password = get_user_input()
    
def init():
    ADC0832.setup()
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)
    
    
    GPIO.setup(pump_gpio_pin, GPIO.OUT)
    GPIO.setup(fan_gpio_pin, GPIO.OUT)
    GPIO.output(pump_gpio_pin, GPIO.LOW)
    GPIO.output(fan_gpio_pin, GPIO.LOW)
    
    gui_thread = threading.Thread(target=create_gui)
    gui_thread.start()
    
    
    
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
            try:
                send_email(
                    subject='Greenhouse Alert',
                    message=f'Temperature is over threshold({temperature_threshold}): current temperature in C: {tmp}',
                    sender_email=sender_email,
                    recipient_emails=recipient_emails,
                    smtp_server='smtp.gmail.com',
                    smtp_port=587,
                    username=sender_email,
                    password=google_app_password
                )
            except:
                print ("Email configuration not accepted")
            #turn the fan motor for 30 seconds
            fan_thread = threading.Thread(target=turn_on_motor, args=(30,fan_gpio_pin))
            fan_thread.start()
            
        if(moisture < moisture_threshold):
            #turn the Pump on for 3 seconds
            pump_thread = threading.Thread(target=turn_on_motor, args=(3,pump_gpio_pin))
            pump_thread.start()
            try:
                send_email(
                    subject='Greenhouse Alert',
                    message=f'Moisture is below threshold({moisture_threshold}): current moisture %: {moisture}',
                    sender_email=sender_email,
                    recipient_emails=recipient_emails,
                    smtp_server='smtp.gmail.com',
                    smtp_port=587,
                    username=sender_email,
                    password=google_app_password
                )
            except:
                print ("\nEmail configuration not accepted")
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
        time.sleep(2)

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



