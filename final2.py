from array import array
from time import sleep
from math import sqrt
import pygame

from gpiozero import DistanceSensor
from pygame.mixer import Sound, get_init, pre_init, pause, unpause


tone_sensor = DistanceSensor(trigger=19, echo=13)
volume_sensor = DistanceSensor(trigger=21, echo=20)

class Note(Sound):
    def __init__(self, frequency, volume=.01):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

def get_tone():
    return 220 + sqrt(tone_sensor.distance) * 2200

def get_volume():
    return volume_sensor.distance / 10

def destroy():
    tone_sensor.close()


if __name__ == "__main__":
    pre_init(24000, -16, 1, 512)
    pygame.init()
    while True:
        try:
            note = Note(get_tone(), get_volume())
            if tone_sensor.distance < .9:
                note.play(-1, 25)
        except:
            destroy()