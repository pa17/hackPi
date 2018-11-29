import time
import pyowm
import json
import datetime
from subprocess import call

PERIOD = 300  # Check if there is new measurement every 5 minutes

class WeatherUploader:
    """
    Fetches weather data from OpenWeatherMap and uploads it to Dropbox
    """

    def __init__(self):

        # Period at which IR sensor is sampled
        self.period = PERIOD

        # OWM object
        self.owm = pyowm.OWM('f8ad0d18a50b27ed99a9c436bd21f2c2')  # You MUST provide a valid API key

        # Search for current weather in London (Great Britain)
        self.observation = self.owm.weather_at_place('London,GB')

        # Get the current weather
        current_weather = self.observation.get_weather()
        self.current_ref_time = datetime.datetime.fromtimestamp(current_weather.get_reference_time())

        self.last_line = ""

        # Determine filename
        current_year = self.current_ref_time.year - 2000 # Dont' care about millenium
        current_month = self.current_ref_time.month
        current_day = self.current_ref_time.day
        current_hour = self.current_ref_time.hour

        if current_hour < 10:
            extra_digit = '0'
        else:
            extra_digit = ''

        # Output file
        self.filename = 'wdata_' + str(current_year) + str(current_month) + str(current_day) + extra_digit + \
                        str(current_hour) + ".txt"

        self.file = open('/home/pi/Desktop/Projects/SIOT_Project/output_data/' + self.filename, 'w')

        while True:
            # Check the new time
            self.check_time()

            # Append the new observed values
            self.append_data()

    def check_time(self):
        """
        Checks the current time and closes the file and calls for upload when hour has changed
        """

        self.observation = self.owm.weather_at_place('London,GB')
        weather_now = self.observation.get_weather()
        new_ref_time = datetime.datetime.fromtimestamp(weather_now.get_reference_time())

        # If hour has incremented or is back at 0 -> New day has begun
        if new_ref_time.hour > self.current_ref_time.hour or new_ref_time.day > self.current_ref_time.day or \
                new_ref_time.month > self.current_ref_time.month or new_ref_time.year > self.current_ref_time.year:

            new_year = new_ref_time.year - 2000 # Don't care about the millenium
            new_month = new_ref_time.month
            new_day = new_ref_time.day
            new_hour = new_ref_time.hour

            if new_hour < 10:
                extra_digit = '0'
            else:
                extra_digit = ''

            # Close file and upload it
            self.file.close()
            self.upload_file()

            # Create a new file
            self.filename = 'wdata_' + str(new_year) + str(new_month) + str(new_day) + extra_digit + \
                            str(new_hour) + ".txt"
            self.file = open('/home/pi/Desktop/Projects/SIOT_Project/output_data/' + self.filename, 'w')

            # Make new_ref_time to current_ref_time
            self.current_ref_time = new_ref_time

    def upload_file(self):
        """
        Uploads the current file via a call to a Dropbox-Uploader script
        """

        output_path = "/home/pi/Desktop/Projects/SIOT_Project/output_data/"
        upload = "/home/pi/Desktop/Projects/SIOT_Project/Dropbox-Uploader/dropbox_uploader.sh upload " + output_path + \
                 self.filename + " " + self.filename
        call([upload], shell=True)

    def append_data(self, debug=True):
        """
        Reads raw data from the sensor and writes it to a file
        """

        weather_now = self.observation.get_weather()

        ref_time = datetime.datetime.fromtimestamp(weather_now.get_reference_time())
        temp = weather_now.get_temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
        status = weather_now.get_status() # Get weather short status
        detailed_status = weather_now.get_detailed_status()

        line_data = [str(ref_time.strftime("%Y-%m-%d %H:%M:%S")), temp, status, detailed_status]

        # Check if it's the same data as the previous one, if it's not add it to the file.
        if line_data != self.last_line:
            json.dump(line_data, self.file)
            self.file.write("\n")

            print(line_data)
            print("\n")

        self.last_line = line_data

        # Sleep for our sampling rate
        time.sleep(self.period)


if __name__ == '__main__':

    weather_data_node = WeatherUploader()
