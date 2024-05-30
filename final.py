from gpiozero import DistanceSensor, TonalBuzzer
from gpiozero.tones import Tone
from time import sleep
from math import cbrt
import pygame
from pathlib import Path
import sys
import time

tone_sensor = DistanceSensor(trigger=19, echo=13)
buzz = TonalBuzzer(5, octaves = 3)


HERE = Path(__file__).parent.parent
sys.path.append(str(HERE / 'Common'))
from ADCdevice import * 

USING_GRAVITECH_ADC = False

def setup():
    global ADC
    if(ADC.detectI2C(0x48) and USING_GRAVITECH_ADC): 
        ADC = GravitechADC()
    elif(ADC.detectI2C(0x48)): # Detect the pcf8591.
        ADC = PCF8591()
    elif(ADC.detectI2C(0x4b)): # Detect the ads7830
        ADC = ADS7830()
    else:
        print("No correct I2C address found, \n"
            "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
            "Program Exit. \n")
        exit(-1)

tone_range = buzz.max_tone - buzz.min_tone

def get_tone():
    print(ADC.analogRead(1) * 100)
    return buzz.min_tone + int(tone_range  * tone_sensor.distance)

def destroy():
    tone_sensor.close()
    buzz.close()
    
if __name__ == "__main__":
    while True:
        try:
            tone = get_tone()
            if tone_sensor.distance < .5:
                buzz.play(Tone(tone))
            else:
                buzz.stop()
        except:
            destroy()


