from weather_utils import getDisplayColor
from weather_information import weatherInfomation
from weather_draw import drawWeather


from PIL import Image, ImageDraw, ImageFont, ImageFilter


saturation = 0.5
canvasSize = (600, 448)

from inky.inky_uc8159 import BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE, DESATURATED_PALETTE as color_palette


def display_image():
    wi = weatherInfomation()
    cv = Image.new("RGB", canvasSize, getDisplayColor(WHITE) )    #cv = cv.rotate(90, expand=True)
    drawWeather(wi, cv)
    cv.save("test.png")
