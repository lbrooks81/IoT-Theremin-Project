from pysinewave import SineWave
from gpiozero import DistanceSensor, Button
from math import sqrt
from time import sleep
from numpy import log
import sys
from pathlib import Path

HERE = Path(__file__).parent.parent
sys.path.append(str(HERE / 'Common'))
from ADCdevice import * 

USING_GRAVITECH_ADC = False

ADC = ADCDevice()
tone_sensor = DistanceSensor(trigger=21, echo=20)
volume_sensor = DistanceSensor(trigger=19, echo=26)
toggle_button = Button(12)
kill_switch = Button(16)

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

def get_frequency():
    return round(ADC.analogRead(0) / 32) * (tone_sensor.distance) * 440 + ADC.analogRead(7)

def get_volume():
    return volume_sensor.distance * round(ADC.analogRead(5))


def button_flip():
    global pressed
    pressed = not pressed

def destroy():
    tone_sensor.close()
    volume_sensor.close()
    ADC.close()
    exit


if __name__ == "__main__":
    setup()
    pressed = False
    wave = SineWave(decibels=20, pitch_per_second=48, decibels_per_second=64)
    toggle_button.when_activated = button_flip
    kill_switch.when_activated = wave.stop
    while True:
        try:
            if pressed:
                frequency = get_frequency()
                wave.set_frequency(frequency)

            volume = get_volume()
            wave.set_volume(volume)
            
            if tone_sensor.distance < .9:
                wave.play()
                sleep(0.0022)
            else:
                wave.stop()
        except KeyboardInterrupt:
            destroy()    
        