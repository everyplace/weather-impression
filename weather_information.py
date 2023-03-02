import os

tmpfs_path = "/dev/shm/"
# font file path(Adjust or change whatever you want)
os.chdir('/home/pi/weather-impression')
project_root = os.getcwd()

class weatherInfomation(object):
    def __init__(self):
        #load configuration from config.txt using configparser
        import configparser
        self.config = configparser.ConfigParser()
        try:
            self.config.read_file(open(project_root + '/config.txt'))
            self.lat = self.config.get('openweathermap', 'LAT', raw=False)
            self.lon = self.config.get('openweathermap', 'LON', raw=False)
            self.mode = self.config.get('ui', 'mode', raw=False)
            self.forecast_interval = self.config.get('openweathermap', 'FORECAST_INTERVAL', raw=False)
            self.api_key = self.config.get('openweathermap', 'API_KEY', raw=False)
            # API document at https://openweathermap.org/api/one-call-api
            self.unit = self.config.get('openweathermap', 'TEMP_UNIT', raw=False)
            self.cold_temp = float(self.config.get('openweathermap', 'cold_temp', raw=False))
            self.hot_temp = float(self.config.get('openweathermap', 'hot_temp', raw=False))
            self.forecast_api_uri = 'https://api.openweathermap.org/data/3.0/onecall?&lat=' + self.lat + '&lon=' + self.lon +'&appid=' + self.api_key + '&exclude=daily'
            if(self.unit == 'imperial'):
                self.forecast_api_uri = self.forecast_api_uri + "&units=imperial"
            else:
                self.forecast_api_uri = self.forecast_api_uri + "&units=metric"
            self.loadWeatherData()
        except:
            self.one_time_message = "Configuration file is not found or settings are wrong.\nplease check the file : " + project_root + "/config.txt\n\nAlso check your internet connection."
            return

        # load one time messge and remove it from the file. one_time_message can be None.
        try:
            self.one_time_message = self.config.get('openweathermap', 'one_time_message', raw=False)
            self.config.set("openweathermap", "one_time_message", "")
            # remove it.
            with open(project_root + '/config.txt', 'w') as configfile:
                self.config.write(configfile)
        except:
            self.one_time_message = ""
            pass

    def loadWeatherData(self):
        import requests
        self.weatherInfo = requests.get(self.forecast_api_uri).json()
