#!/usr/bin/env python
import ADC0832

def getLight():
	
	res = ADC0832.getADC(0)
	vol = 3.3/255 * res
	if vol >= 1.65:
		return("Light")
	else:
		return("Dark")
