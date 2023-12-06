#!/usr/bin/env python

# Function to read temperature from the DS18B20 sensor
def ds18b20Read():
    # Open the file that the DS18B20 sensor writes its readings to
    tfile = open("/sys/bus/w1/devices/28-0000062abd71/w1_slave")
    # Read the entire contents of the file
    text = tfile.read()
    # Close the file
    tfile.close()
    # Split the text by newline characters and take the second line
    secondline = text.split("\n")[1]
    # Split the second line by spaces and take the tenth element
    temperaturedata = secondline.split(" ")[9]
    # Convert the temperature data to a float, ignoring the first two characters
    temperature = float(temperaturedata[2:])
    # Divide the temperature by 1000 to convert it to degrees Celsius
    temperature = temperature / 1000
    # Round the temperature to two decimal places
    temperature = round(temperature, 2)
    # Print the temperature
    print(temperature)
    # Return the temperature
    return temperature