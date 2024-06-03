from pysinewave import SineWave
from gpiozero import DistanceSensor, Button, LED
from math import sqrt
from time import sleep
from numpy import log
import sys
from pathlib import Path

HERE = Path(__file__).parent.parent
sys.path.append(str(HERE / 'Common'))
from ADCdevice import * 
USING_GRAVITECH_ADC = Fals
ADC = ADCDevice()

tone_sensor = DistanceSensor(trigger=21, echo=20)
volume_sensor = DistanceSensor(trigger=19, echo=26)

toggle_button = Button(12)
toggle_LED = LED(17)

kill_switch = Button(16)
kill_LED = LED(18)

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
    """Returns frequency based on distance sensor and the two adjustment knobs"""
    return round(ADC.analogRead(0) / 32) * (tone_sensor.distance) * 440 + ADC.analogRead(7)

def get_volume():
    """Returns volume based on distance sensor and adjustment knob"""
    return volume_sensor.distance * round(ADC.analogRead(5))


def kill():
    """Flips kill-switch boolean and adjusts the LED accordingly"""
    global switch 
    switch = not switch
    if switch:
        kill_LED.on()
    else:
        kill_LED.off()

def toggle():
    """Flips freeze-toggle boolean and adjusts the LED accordingly"""
    global pressed
    pressed = not pressed

    if pressed == False:
        toggle_LED.on()
    else:
        toggle_LED.off()

def destroy():
    devices: list = (tone_sensor, volume_sensor, ADC, toggle_button, toggle_LED, kill_switch, kill_LED)
    
    for device in devices:
        device.close()
    exit


if __name__ == "__main__":
    setup()
    wave = SineWave(decibels=10, pitch_per_second=48, decibels_per_second=64)
    
    pressed = False # Boolean used for freeze toggle
    switch = False # Boolean used for kill switch
    toggle_button.when_activated = toggle
    toggle_LED.on()
    kill_switch.when_activated = kill
    
    while True:
        try:
            if pressed: # Only changes frequency if the freeze-toggle is off
                frequency = get_frequency()
                wave.set_frequency(frequency)

            volume = get_volume()
            wave.set_volume(volume)
            
            if tone_sensor.distance < .9 and switch == False:
                wave.play()
                sleep(0.0022)
            else: # Stops wave if kill switch is active
                wave.stop()
        except KeyboardInterrupt:
            destroy()    
        