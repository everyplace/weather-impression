#!/usr/bin/env python3
import os

from weather_hardware import display_screen
from weather_image import display_image

import configparser

os.chdir('/home/pi/weather-impression')
project_root = os.getcwd()

config = configparser.ConfigParser()

try:
    config.read_file(open(project_root + '/config.txt'))
    output = config.get('ui', 'output', raw=False)
except:
    one_time_message = "Configuration file is not found or settings are wrong.\nplease check the file : " + project_root + "/config.txt\n\nAlso check your internet connection."
    print(one_time_message)

def update():

    if(output == 'image'):
        display_image()
    else :
        display_screen()

if __name__ == "__main__":
    update()
