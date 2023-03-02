from weather_information import weatherInfomation
import gpiod
from inky.inky_uc8159 import Inky

def initGPIO():
    chip = gpiod.chip(0) # 0 chip 
    pin = 4
    gpiod_pin = chip.get_line(pin)
    config = gpiod.line_request()
    config.consumer = "Blink"
    config.request_type = gpiod.line_request.DIRECTION_OUTPUT
    gpiod_pin.request(config)
    return gpiod_pin

def setUpdateStatus(gpiod_pin, busy):
    if busy == True:
        gpiod_pin.set_value(1)
    else:
        gpiod_pin.set_value(0)

def display_screen():
    wi = weatherInfomation()
    
    gpio_pin = initGPIO()
    setUpdateStatus(gpio_pin, True)
    
    cv = Image.new("RGB", canvasSize, getDisplayColor(WHITE) )
    #cv = cv.rotate(90, expand=True)
    drawWeather(wi, cv)
    # cv.save("test.png")
    #cv = cv.rotate(-90, expand=True)
    inky = Inky()
    inky.set_image(cv, saturation=saturation)
    inky.show()
    setUpdateStatus(gpio_pin, False)
