from inky.inky_uc8159 import Inky, BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE, DESATURATED_PALETTE as color_palette
from enum import Enum
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

colorMap = {
    '01d':ORANGE, # clear sky
    '01n':YELLOW,
    '02d':BLACK, # few clouds
    '02n':BLACK,
    '03d':BLACK, # scattered clouds
    '03n':BLACK,
    '04d':BLACK, # broken clouds
    '04n':BLACK,
    '09d':BLACK, # shower rain
    '09n':BLACK,
    '10d':BLUE,  # rain
    '10n':BLUE, 
    '11d':RED,   # thunderstorm
    '11n':RED,
    '13d':BLUE,  # snow
    '13n':BLUE, 
    '50d':BLACK, # fog
    '50n':BLACK,
    'sunrise':BLACK,
    'sunset':BLACK
}
# icon name to weather icon mapping
iconMap = {
    '01d':u'', # clear sky
    '01n':u'',
    '02d':u'', # few clouds
    '02n':u'',
    '03d':u'', # scattered clouds
    '03n':u'',
    '04d':u'', # broken clouds
    '04n':u'',
    '09d':u'', # shower rain
    '09n':u'',
    '10d':u'', # rain
    '10n':u'',
    '11d':u'', # thunderstorm
    '11n':u'',
    '13d':u'', # snow
    '13n':u'',
    '50d':u'', # fog
    '50n':u'',

    'clock0':u'', # same as 12
    'clock1':u'',
    'clock2':u'',
    'clock3':u'',
    'clock4':u'',
    'clock5':u'',
    'clock6':u'',
    'clock7':u'',
    'clock8':u'',
    'clock9':u'',
    'clock10':u'',
    'clock11':u'',
    'clock12':u'',

    'celsius':u'',
    'fahrenheit':u'',
    'sunrise':u'',
    'sunset':u''
}

os.chdir('/home/pi/weather-impression')
project_root = os.getcwd()

class fonts(Enum):
    thin = project_root + "/fonts/Roboto-Thin.ttf"
    light =  project_root + "/fonts/Roboto-Light.ttf"
    normal = project_root + "/fonts/Roboto-Black.ttf"
    icon = project_root + "/fonts/weathericons-regular-webfont.ttf"

def getFont(type, fontsize=12):
    return ImageFont.truetype(type.value, fontsize)

def getFontColor(temp, wi):
    if temp < wi.cold_temp:
        return (0,0,255)
    if temp > wi.hot_temp:
        return (255,0,0)
    return getDisplayColor(BLACK)

def getUnitSign(unit):
    unit_imperial = "imperial"
    if(unit == unit_imperial):
        return iconMap['fahrenheit']
    
    return iconMap['celsius']

# return rgb in 0 ~ 255
def getDisplayColor(color):
    return tuple(color_palette[color])

def getTempretureString(temp):
    formattedString = "%0.0f" % temp
    if formattedString == "-0":
        return "0"
    else:
        return formattedString
    
# return color rgb in 0 ~ 1.0 scale
def getGraphColor(color):
    r = color_palette[color][0] / 255
    g = color_palette[color][1] / 255
    b = color_palette[color][2] / 255
    return (r,g,b)
