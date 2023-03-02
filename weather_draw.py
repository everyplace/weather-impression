from weather_utils import colorMap, iconMap
from weather_utils import fonts, getFont, getFontColor
from weather_utils import getUnitSign, getTempretureString
from weather_utils import getDisplayColor, getGraphColor

from inky.inky_uc8159 import BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE, DESATURATED_PALETTE as color_palette


from PIL import Image, ImageDraw, ImageFont, ImageFilter
import time
import math
from datetime import date
from datetime import datetime

tmpfs_path = "/dev/shm/"

# draw current weather and forecast into canvas
def drawWeather(wi, cv):
    draw = ImageDraw.Draw(cv)
    width, height = cv.size

    # one time message
    if hasattr( wi, "weatherInfo") == False:
        draw.rectangle((0, 0, width, height), fill=getDisplayColor(ORANGE))
        draw.text((20, 70), u"", getDisplayColor(BLACK), anchor="lm", font =getFont(fonts.icon, fontsize=130))
        draw.text((150, 80), "Weather information is not available at this time.", getDisplayColor(BLACK), anchor="lm", font=getFont(fonts.normal, fontsize=18) )
        draw.text((width / 2, height / 2), wi.one_time_message, getDisplayColor(BLACK), anchor="mm", font=getFont(fonts.normal, fontsize=16) )
        return
    draw.text((width - 10, 2), wi.one_time_message, getDisplayColor(BLACK), anchor="ra", font=getFont(fonts.normal, fontsize=12))
    
    temp_cur = wi.weatherInfo[u'current'][u'temp']
    temp_cur_feels = wi.weatherInfo[u'current'][u'feels_like']
    icon = str(wi.weatherInfo[u'current'][u'weather'][0][u'icon'])
    description = wi.weatherInfo[u'current'][u'weather'][0][u'description']
    humidity = wi.weatherInfo[u'current'][u'humidity']
    pressure = wi.weatherInfo[u'current'][u'pressure']
    epoch = int(wi.weatherInfo[u'current'][u'dt'])
    #snow = wi.weatherInfo[u'current'][u'snow']
    dateString = time.strftime("%B %-d", time.localtime(epoch))
    weekDayString = time.strftime("%a", time.localtime(epoch))
    weekDayNumber = time.strftime("%w", time.localtime(epoch))

    # date 
    draw.text((15 , 5), dateString, getDisplayColor(BLACK),font=getFont(fonts.normal, fontsize=64))
    draw.text((width - 8 , 5), weekDayString, getDisplayColor(BLACK), anchor="ra", font =getFont(fonts.normal, fontsize=64))

    offsetX = 10
    offsetY = 40

    # Draw temperature string
    tempOffset = 20 
    temperatureTextSize = draw.textsize(getTempretureString(temp_cur), font =getFont(fonts.normal, fontsize=120))
    if(temperatureTextSize[0] < 71):
        # when the temp string is a bit short.
        tempOffset = 45

    draw.text((5 + offsetX , 35 + offsetY), "Temperature", getDisplayColor(BLACK),font=getFont(fonts.light,fontsize=24))
    draw.text((tempOffset + offsetX, 50 + offsetY), getTempretureString(temp_cur), getFontColor(temp_cur, wi),font =getFont(fonts.normal, fontsize=120))
    draw.text((temperatureTextSize[0] + 10 + tempOffset + offsetX, 85 + offsetY), getUnitSign(wi.unit), getFontColor(temp_cur, wi), anchor="la", font =getFont(fonts.icon, fontsize=80))
    # humidity
    # draw.text((width - 8, 270 + offsetY), str(humidity) + "%", getDisplayColor(BLACK), anchor="rs",font =getFont(fonts.light,fontsize=24))

    # draw current weather icon
    draw.text((440 + offsetX, 40 + offsetY), iconMap[icon], getDisplayColor(colorMap[icon]), anchor="ma",font=getFont(fonts.icon, fontsize=160))

    draw.text((width - 8, 35 + offsetY), description, getDisplayColor(BLACK), anchor="ra", font =getFont(fonts.light,fontsize=24))

    offsetY = 210
    
    # When alerts are in effect, show it to forecast area.
    if wi.mode == '1' and u'alerts' in wi.weatherInfo:
        alertInEffectString = time.strftime('%B %-d, %H:%m %p', time.localtime(wi.weatherInfo[u'alerts'][0][u'start']))

        # remove "\n###\n" and \n\n
        desc = wi.weatherInfo[u'alerts'][0][u'description'].replace("\n###\n", '')
        desc = desc.replace("\n\n", '')
        desc = desc.replace("https://", '') # remove https://
        desc = re.sub(r"([A-Za-z]*:)", "\n\g<1>", desc)
        desc = re.sub(r'((?=.{90})(.{0,89}([\.[ ]|[ ]))|.{0,89})', "\g<1>\n", desc)
        desc = desc.replace("\n\n", '')

        draw.text((5 + offsetX , 215), wi.weatherInfo[u'alerts'][0][u'event'].capitalize() , getDisplayColor(RED),anchor="la", font =getFont(fonts.light,fontsize=24))
        draw.text((5 + offsetX , 240), alertInEffectString + "/" + wi.weatherInfo[u'alerts'][0][u'sender_name'] , getDisplayColor(BLACK), font=getFont(fonts.normal, fontsize=12))

        draw.text((5 + offsetX, 270), desc, getDisplayColor(RED),anchor="la", font =getFont(fonts.normal, fontsize=14))
        return
    # feels like
    draw.text((5 + offsetX , 175 + 40), "Feels like", getDisplayColor(BLACK),font =getFont(fonts.light,fontsize=24))
    draw.text((10 + offsetX, 200 + 40), getTempretureString(temp_cur_feels),getFontColor(temp_cur_feels, wi),font =getFont(fonts.normal, fontsize=50))
    feelslikeTextSize = draw.textsize(getTempretureString(temp_cur_feels), font =getFont(fonts.normal, fontsize=50))
    draw.text((feelslikeTextSize[0] + 20 + offsetX, 200 + 40), getUnitSign(wi.unit), getFontColor(temp_cur_feels, wi), anchor="la", font=getFont(fonts.icon,fontsize=50))

    # Pressure
    draw.text((feelslikeTextSize[0] + 85 + offsetX , 175 + 40), "Pressure", getDisplayColor(BLACK),font =getFont(fonts.light,fontsize=24))
    draw.text((feelslikeTextSize[0] + 90 + offsetX, 200 + 40), "%d" % pressure, getDisplayColor(BLACK),font =getFont(fonts.normal, fontsize=50))
    pressureTextSize = draw.textsize("%d" % pressure, font =getFont(fonts.normal, fontsize=50))
    draw.text((feelslikeTextSize[0] + pressureTextSize[0] + 95 + offsetX, 224 + 40), "hPa", getDisplayColor(BLACK),font=getFont(fonts.normal, fontsize=22))
    
    # Graph mode
    if wi.mode == '2':
        import matplotlib.pyplot as plt
        from matplotlib import font_manager as fm, rcParams
        import numpy as np
        forecastRange = 47
        graph_height = 1.1
        graph_width = 8.4
        xarray = []
        tempArray = []
        feelsArray = []
        pressureArray = []
        try:
            for fi in range(forecastRange):
                finfo = forecastInfo()
                finfo.time_dt  = wi.weatherInfo[u'hourly'][fi][u'dt']
                finfo.time     = time.strftime('%-I %p', time.localtime(finfo.time_dt))
                finfo.temp     = wi.weatherInfo[u'hourly'][fi][u'temp']
                finfo.feels_like     = wi.weatherInfo[u'hourly'][fi][u'feels_like']
                finfo.humidity = wi.weatherInfo[u'hourly'][fi][u'humidity']
                finfo.pressure = wi.weatherInfo[u'hourly'][fi][u'pressure']
                finfo.icon     = wi.weatherInfo[u'hourly'][fi][u'weather'][0][u'icon']
                # print(wi.weatherInfo[u'hourly'][fi][u'snow'][u'1h']) # mm  / you may get 8 hours maximum
                xarray.append(finfo.time_dt)
                tempArray.append(finfo.temp)
                feelsArray.append(finfo.feels_like)
                pressureArray.append(finfo.pressure)
        except IndexError:
            # The weather forecast API is supposed to return 48 forecasts, but it may return fewer than 48.
            errorMessage = "Weather API returns limited hourly forecast(" + str(len(xarray)) + ")"
            draw.text((width - 10, height - 2), errorMessage, getDisplayColor(ORANGE), anchor="ra", font=getFont(fonts.normal, fontsize=12))
            pass
        
        fig = plt.figure()
        fig.set_figheight(graph_height)
        fig.set_figwidth(graph_width)
        plt.plot(xarray, pressureArray, linewidth=3, color=getGraphColor(RED)) # RGB in 0~1.0
        #plt.plot(xarray, pressureArray)
        #annot_max(np.array(xarray),np.array(tempArray))
        #annot_max(np.array(xarray),np.array(pressureArray))
        plt.axis('off')
        ax = plt.gca()
        airPressureMin = 990
        airPressureMax = 1020
        if min(pressureArray) < airPressureMin - 2:
            airPressureMin = min(pressureArray) + 2
        if max(pressureArray) > airPressureMax - 2:
            airPressureMax = max(pressureArray) + 2

        plt.ylim(airPressureMin,airPressureMax)

        plt.savefig(tmpfs_path + 'pressure.png', bbox_inches='tight', transparent=True)
        tempGraphImage = Image.open(tmpfs_path + "pressure.png")
        cv.paste(tempGraphImage, (-35, 330), tempGraphImage)

        # draw temp and feels like in one figure
        fig = plt.figure()
        fig.set_figheight(graph_height)
        fig.set_figwidth(graph_width)
        plt.plot(xarray, feelsArray, linewidth=3, color=getGraphColor(GREEN), linestyle=':') # RGB in 0~1.0
        plt.axis('off')
        plt.plot(xarray, tempArray, linewidth=3, color=getGraphColor(BLUE))

        for idx in range(1, len(xarray)):
            h = time.strftime('%-I', time.localtime(xarray[idx]))
            if h == '0' or h == '12':
                plt.axvline(x=xarray[idx], color='black', linestyle=':')
                posY = np.array(tempArray).max() + 1
                plt.text(xarray[idx-1], posY, time.strftime('%p', time.localtime(xarray[idx])))
        plt.axis('off')
        plt.savefig(tmpfs_path+'temp.png', bbox_inches='tight',  transparent=True)
        tempGraphImage = Image.open(tmpfs_path+"temp.png")
        cv.paste(tempGraphImage, (-35, 300), tempGraphImage)

        # draw label
        draw.rectangle((5, 430, 20, 446), fill=getDisplayColor(RED))/test.png
        draw.text((15 + offsetX, 428), "Pressure", getDisplayColor(BLACK),font=getFont(fonts.normal, fontsize=16))

        draw.rectangle((135, 430, 150, 446), fill=getDisplayColor(BLUE))
        draw.text((145 + offsetX, 428), "Temp", getDisplayColor(BLACK),font=getFont(fonts.normal, fontsize=16))

        draw.rectangle((265, 430, 280, 446), fill=getDisplayColor(GREEN))
        draw.text((275 + offsetX, 428), "Feels like", getDisplayColor(BLACK),font=getFont(fonts.normal, fontsize=16))
        return

    # Sunrise / Sunset iconography
    if wi.mode == '3':
        print("hello, sunrise")
        sunrise = wi.weatherInfo['current']['sunrise']
        sunset = wi.weatherInfo['current']['sunset']

        sunriseFormatted = datetime.fromtimestamp(sunrise).strftime("%#I:%M %p")
        sunsetFormatted = datetime.fromtimestamp(sunset).strftime("%#I:%M %p")

        print([sunriseFormatted, sunsetFormatted])

        columnWidth = width / 2
        textColor = (50,50,50)
        # center = column width / 2 - (text_width * .5)
        # measure sunrise
        sunrise_width, _ = getFont(fonts.normal, fontsize=16).getsize("Sunrise")
        sunriseXOffset = (columnWidth/2) - (sunrise_width * .5)
        
        sunriseFormatted_width, _ = getFont(fonts.normal, fontsize=12).getsize(sunriseFormatted)
        sunriseFormattedXOffset = (columnWidth/2) - (sunriseFormatted_width * .5)

        sunriseIcon_width, _ = getFont(fonts.icon, fontsize=90).getsize(iconMap['sunrise'])
        sunriseIconXOffset = (columnWidth/2) - (sunriseIcon_width * .5)

        draw.text((sunriseFormattedXOffset, offsetY + 220), sunriseFormatted,textColor,anchor="la", font =getFont(fonts.normal, fontsize=12))
        draw.text((sunriseIconXOffset, offsetY + 90), iconMap['sunrise'], getDisplayColor(colorMap['sunrise']), anchor="la",font =getFont(fonts.icon, fontsize=90))
        draw.text((sunriseXOffset,  offsetY + 200), "Sunrise", textColor,anchor="la", font =getFont(fonts.normal, fontsize=16))

        sunset_width, _ = getFont(fonts.normal, fontsize=16).getsize("sunset")
        sunsetXOffset = columnWidth + (columnWidth/2) - (sunset_width * .5)
        
        sunsetFormatted_width, _ = getFont(fonts.normal, fontsize=12).getsize(sunsetFormatted)
        sunsetFormattedXOffset = columnWidth + (columnWidth/2) - (sunsetFormatted_width * .5)

        sunsetIcon_width, _ = getFont(fonts.icon, fontsize=90).getsize(iconMap['sunset'])
        sunsetIconXOffset = columnWidth + (columnWidth/2) - (sunsetIcon_width * .5)

        draw.text((sunsetFormattedXOffset, offsetY + 220), sunsetFormatted,textColor,anchor="la", font =getFont(fonts.normal, fontsize=12))
        draw.text((sunsetIconXOffset, offsetY + 90), iconMap['sunset'], getDisplayColor(colorMap['sunset']), anchor="la",font =getFont(fonts.icon, fontsize=90))
        draw.text((sunsetXOffset,  offsetY + 200), "Sunset", textColor,anchor="la", font =getFont(fonts.normal, fontsize=16))

        return
    
    # Sunrise / Sunset graph
    if wi.mode == '4':
        print("ok")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager as fm, rcParams
        import matplotlib
        import numpy as np
        # import datetime

        def minutes_since(timestamp):
            dt = datetime.fromtimestamp(timestamp)
            timestamp_minutes_since_midnight = dt.hour * 60 + dt.minute
            return timestamp_minutes_since_midnight

        # icon font setup
        icon_font = getFont(fonts.icon, fontsize=12)
        icon_prop = fm.FontProperties(fname=icon_font.path)
        text_font = getFont(fonts.normal, fontsize=12)
        text_prop = fm.FontProperties(fname=text_font.path)

        graph_height = 1.1
        graph_width = 8.4

        x = [i for i in range(24)]
        # y = [math.sin(math.pi * i / 12) for i in x]
        y = [math.cos((i / 12 - 1) * math.pi) for i in x]

        fig = plt.figure()
        fig.set_figheight(graph_height)
        fig.set_figwidth(graph_width)

        plt.xlim(0, 23)
        plt.ylim(-1.2, 1.2)
        # add labels and title
        # plt.xlabel("Hour of Day")
        # plt.ylabel("Sun Elevation")
        plt.title("")

        # add sunrise and sunset lines
        sunrise_timestamp = wi.weatherInfo['current']['sunrise']
        sunset_timestamp = wi.weatherInfo['current']['sunset']
        sunrise_time = minutes_since(sunrise_timestamp)
        sunset_time = minutes_since(sunset_timestamp)
        sunrise_hour = sunrise_time / 60
        sunset_hour = sunset_time / 60
        sunriseFormatted = datetime.fromtimestamp(sunrise_timestamp).strftime("%#I:%M %p")
        sunsetFormatted = datetime.fromtimestamp(sunset_timestamp).strftime("%#I:%M %p")

        plt.axvline(x=sunrise_hour, color="orange", linestyle="--")
        plt.axvline(x=sunset_hour, color="blue", linestyle="--")

        plt.text(sunrise_hour-.35, 1.35, iconMap['sunrise'], fontproperties=icon_prop, ha="right", va="top", color=getGraphColor(YELLOW))
        plt.text(sunrise_hour-.3, 1.3, iconMap['sunrise'], fontproperties=icon_prop, ha="right", va="top", color=getGraphColor(ORANGE))

        plt.text(sunset_hour+.35, 1.35, iconMap['sunset'], fontproperties=icon_prop, ha="left", va="top", color=getGraphColor(YELLOW))
        plt.text(sunset_hour+.3, 1.3, iconMap['sunset'], fontproperties=icon_prop, ha="left", va="top", color=getGraphColor(BLUE))
        plt.text(sunrise_hour-.3, .8, sunriseFormatted, ha="right", va="top", fontproperties=text_prop, rotation="horizontal", color=getGraphColor(ORANGE))
        plt.text(sunset_hour+.3, .8, sunsetFormatted, ha="left", va="top", fontproperties=text_prop, rotation="horizontal", color=getGraphColor(BLUE))

        normal = getFont(fonts.normal, fontsize=12)
        plt.rcParams['font.family'] = normal.getname()

        plt.plot(x, y, linewidth=3, color=getGraphColor(RED)) # RGB in 0~1.0
        #plt.plot(xarray, pressureArray)
        #annot_max(np.array(xarray),np.array(tempArray))
        #annot_max(np.array(xarray),np.array(pressureArray))
        plt.axis('off')

        plt.savefig(tmpfs_path + 'day.png', bbox_inches='tight', transparent=True)
        tempGraphImage = Image.open(tmpfs_path+"day.png")
        cv.paste(tempGraphImage, (-35, 300), tempGraphImage)

        return
    
    forecastIntervalHours = int(wi.forecast_interval)
    forecastRange = 4
    for fi in range(forecastRange):
        finfo = forecastInfo()
        finfo.time_dt  = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'dt']
        finfo.time     = time.strftime('%-I %p', time.localtime(finfo.time_dt))
        finfo.timeIn12h = time.strftime('clock%-I', time.localtime(finfo.time_dt))
        #finfo.ampm     = time.strftime('%p', time.localtime(finfo.time_dt))
        #finfo.time     = time.strftime('%-I', time.localtime(finfo.time_dt))
        finfo.timePfx  = time.strftime('%p', time.localtime(finfo.time_dt))
        finfo.temp     = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'temp']
        finfo.feels_like = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'feels_like']
        finfo.humidity = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'humidity']
        finfo.pressure = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'pressure']
        finfo.icon     = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'weather'][0][u'icon']
        finfo.description = wi.weatherInfo[u'hourly'][fi * forecastIntervalHours + forecastIntervalHours][u'weather'][0][u'description'] # show the first 

        columnWidth = width / forecastRange
        textColor = (50,50,50)
        # Clock icon for the time.(Not so nice.)
        #draw.text((20 + (fi * columnWidth),  offsetY + 90), iconMap[finfo.timeIn12h], textColor, anchor="ma",font =ImageFont.truetype(project_root + "fonts/weathericons-regular-webfont.ttf", 35))
        draw.text((30 + (fi * columnWidth), offsetY + 220), finfo.time,textColor,anchor="la", font =getFont(fonts.normal, fontsize=12))
        draw.text((120 + (fi * columnWidth), offsetY + 220), ("%2.1f" % finfo.temp), textColor, anchor="ra", font=getFont(fonts.normal, fontsize=12) )
        
        draw.text(((columnWidth / 2) + (fi * columnWidth),  offsetY + 200), finfo.description, textColor,anchor="ma", font =getFont(fonts.normal, fontsize=16))
        draw.text((70 + (fi * columnWidth), offsetY + 90), iconMap[finfo.icon], getDisplayColor(colorMap[finfo.icon]), anchor="ma",font =getFont(fonts.icon, fontsize=80))
