#!/usr/bin/env python
import ADC0832

def getLight():
	res = ADC0832.getADC(0)
	vol = 3.3/255 * res
	if vol >= 1.65:
		return("Light")
	else:
		return("Dark")

def ds18b20Read():
	tfile = open("/sys/bus/w1/devices/28-3c01b5561f90/w1_slave")
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	temperaturedata = secondline.split(" ")[9]
	temperature = float(temperaturedata[2:])
	temperature = temperature / 1000
	temperature = round(temperature, 2)
	return temperature

def humididtyRead():
	res = ADC0832.getADC(1)
	moisture = 255 - res
	print (("analog value: %03d  moisture: %d") %(res, moisture))
	return moisture