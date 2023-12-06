#!/usr/bin/env python
# Import the ADC0832 library
import ADC0832

# Function to get light level
def getLight():
    # Get the ADC value from channel 0
    res = ADC0832.getADC(0)
    # Convert the ADC value to voltage
    vol = 3.3/255 * res
    # If the voltage is greater than or equal to 1.65, return True, else return False
    if vol >= 1.65:
        return(True)
    else:
        return(False)

# Function to read from the ds18b20 temperature sensor
def ds18b20Read():
    # Vlads sensor number 28-3c01b5561f90
    # Emile sensor number 28-3c01b5561f90

    # Open the file that the sensor writes to
    tfile = open("/sys/bus/w1/devices/28-3c01b5561f90/w1_slave")
    # Read the file
    text = tfile.read()
    # Close the file
    tfile.close()
    # Split the text by line and get the second line
    secondline = text.split("\n")[1]
    # Split the second line by space and get the tenth item
    temperaturedata = secondline.split(" ")[9]
    # Convert the temperature data to a float and divide by 1000 to get Celsius
    temperature = float(temperaturedata[2:]) / 1000
    # Round the temperature to 2 decimal places
    temperature = round(temperature, 2)
    # Print the temperature
    print("tempSensor", temperature)
    # Return the temperature
    return temperature

# Function to read the humidity
def humididtyRead():
    # Get the ADC value from channel 1
    res = ADC0832.getADC(1)
    # Print the ADC value
    print(res)
    # Calculate the moisture level and round to 2 decimal places
    moisture = round(((255-res)/255)*100, 2)
    # Return the moisture level
    return moisture