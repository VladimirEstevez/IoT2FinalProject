#!/usr/bin/env python

# Import necessary libraries
import time
import os
import RPi.GPIO as GPIO

# Define the GPIO pins that will be used for the SPI communication with the ADC0832 chip
PIN_CLK = 18
PIN_DO = 27
PIN_DI = 22
PIN_CS = 17

# Function to setup the GPIO pins


def setup():
	# Disable warnings
	GPIO.setwarnings(False)
	# Set the GPIO mode to BCM
	GPIO.setmode(GPIO.BCM)
	# Setup the SPI interface pins
	GPIO.setup(PIN_DI,  GPIO.OUT)
	GPIO.setup(PIN_DO,  GPIO.IN)
	GPIO.setup(PIN_CLK, GPIO.OUT)
	GPIO.setup(PIN_CS,  GPIO.OUT)

# Function to cleanup the GPIO pins


def destroy():
	GPIO.cleanup()

# Function to read SPI data from the ADC0832 chip


def getADC(channel):
	# Start a new ADC conversion
	GPIO.output(PIN_CS, True)	  # clear last transmission
	GPIO.output(PIN_CS, False)	 # bring CS low

	# Start the clock
	GPIO.output(PIN_CLK, False)  # start clock low

	# Input the MUX address (channel selection)
	for i in [1, 1, channel]:  # start bit + mux assignment
		if (i == 1):
			GPIO.output(PIN_DI, True)
		else:
			GPIO.output(PIN_DI, False)

		GPIO.output(PIN_CLK, True)
		GPIO.output(PIN_CLK, False)

	# Read the 8-bit ADC value
	ad = 0
	for i in range(8):
		GPIO.output(PIN_CLK, True)
		GPIO.output(PIN_CLK, False)
		ad <<= 1  # shift bit
		if (GPIO.input(PIN_DO)):
			ad |= 0x1  # set first bit

	# Reset the CS line
	GPIO.output(PIN_CS, True)

	# Return the ADC value
	return ad

# Main loop function


def loop():
	while True:
		# Print the ADC values of channel 0 and 1
		print("ADC[0]: {}\t ADC[1]: {}".format(getADC(0), getADC(1)))
		# Wait for 1 second
		time.sleep(1)


# Main function
if __name__ == "__main__":
	# Setup the GPIO pins
	setup()
	try:
		# Start the main loop
		loop()
	except KeyboardInterrupt:
		# If the user presses Ctrl+C, cleanup the GPIO pins
		destroy()
