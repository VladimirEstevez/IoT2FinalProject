import ADC0832
import SensorMethods
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
gpio_pin = 25
GPIO.setup(gpio_pin, GPIO.OUT)

def init():
    ADC0832.setup()


def loop():
	while True:
		#light = SensorMethods.getLight()
		#temp = SensorMethods.ds18b20Read()
		#humid = SensorMethods.humididtyRead()
		#print(temp)
		#time.sleep(0.5)
		GPIO.output(gpio_pin, GPIO.HIGH)
		time.sleep(8)
		GPIO.output(gpio_pin, GPIO.LOW)
		time.sleep(1)


if __name__ == '__main__':
	init()
	try:
		loop()
	except KeyboardInterrupt: 
		ADC0832.destroy()
		GPIO.cleanup()
		print ('The end !')
