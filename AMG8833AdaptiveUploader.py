import time
import busio
import board
import adafruit_amg88xx
import json
import numpy as np
from scipy.interpolate import griddata
from colour import Color
import math
import matplotlib.pyplot as plt

from subprocess import call
import datetime

SAMPLE_RATE = 1 # Hz
SAMPLES_BETWEEN_TIME_CHECK = 10 # check time every 10th loop


class AMG8833AdaptiveUploader:
    """
    Reads and saves the data from the IR camera
    """

    def __init__(self):

        # Init I2C and instantiate sensor on that bus
        i2c = busio.I2C(board.SCL, board.SDA)
        self.amg = adafruit_amg88xx.AMG88XX(i2c)

        # Period at which IR sensor is sampled
        self.period = 1 / SAMPLE_RATE

        # Track Mode
        self.track = False
        self.temp_data = []
        self.alerted = True
        self.track_over = False

        # Time at boot-up for output file
        self.current_time = datetime.datetime.now()

        current_year = self.current_time.year - 2000 # Dont' care about millenium
        current_month = self.current_time.month
        current_day = self.current_time.day
        current_hour = self.current_time.hour

        # Add leading zeroes to help with sorting filenames later
        if current_hour < 10:
            edh = '0'
        else:
            edh = ''

        if current_day < 10:
            edd = '0'
        else:
            edd = ''

        if current_month < 10:
            edm = '0'
        else:
            edm = ''

        # Output file
        self.filename = 'data_' + str(current_year) + edm + str(current_month) + edd + str(current_day) + edh + \
                        str(current_hour) + ".txt"

        self.file = open('/home/pi/Desktop/Projects/SIOT_Project/output_data/' + self.filename, 'w')

        while True:
            # Check the new time
            self.check_time()

            for i in range(SAMPLES_BETWEEN_TIME_CHECK):
                self.append_data()

    def check_time(self):
        """
        Checks the current time and closes the file and calls for upload when hour has changed
        """

        # Get new time
        new_time = datetime.datetime.now()

        # If hour has incremented or is back at 0 -> New day has begun
        if new_time.hour > self.current_time.hour or new_time.day > self.current_time.day or new_time.month \
                > self.current_time.month or new_time.year > self.current_time.year:

            new_year = new_time.year - 2000 # Don't care about the millenium
            new_month = new_time.month
            new_day = new_time.day
            new_hour = new_time.hour

            # Add leading zeroes to help with sorting filenames later
            if new_hour < 10:
                edh = '0'
            else:
                edh = ''

            if new_day < 10:
                edd = '0'
            else:
                edd = ''

            if new_month < 10:
                edm = '0'
            else:
                edm = ''

            # Close file and upload it
            self.file.close()
            self.upload_file()

            # Create a new file
            self.filename = 'data_' + str(new_year) + edm + str(new_month) + edd + str(new_day) + edh + \
                            str(new_hour) + ".txt"
            self.file = open('/home/pi/Desktop/Projects/SIOT_Project/output_data/' + self.filename, 'w')

            # Make new_time to current_time
            self.current_time = new_time

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

        data = []
        for row in self.amg.pixels:
            # Pad to 1 decimal place
            row_data = [float(round(temp, 2)) for temp in row]
            data.append(row_data)

        # Turn track mode on...
        nppixels = np.array(data)
        if nppixels.max() >= 14 and nppixels.std() > 1.5:
            self.track = True

            if debug:
                print("TRACK MODE: On! Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f'")[:-3])

            self.alerted = False
            self.temp_data.append(data)

        # Most of the times... OR: Turn track mode off again...
        else:
            # Set track flag to False, empty temp_data and set alerted as True
            self.track_over = True
            self.temp_data = []

        line_data = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f'")[:-3], data, self.track]
        json.dump(line_data, self.file)
        self.file.write("\n")

        if debug:
            debug_data = []
            for row in self.amg.pixels:
                # Pad to 1 decimal place
                debug_row_data = ['{0:.1f}'.format(temp) for temp in row]
                debug_data.append(debug_row_data)

            print("NORMAL MODE: Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f'")[:-3])
            print("\n")

        # When Track mode is turned off again... Alert user via WhatsApp
        if not self.alerted and self.track_over and self.temp_data != []:
            if debug:
                print("TRACK MODE: Off! Alerting user... Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f'")[:-3])
            self.save_images(self.temp_data)
            self.alerted = True

            self.track_over = False
            self.track = False

            if debug:
                print("SUCCESS: The user has been alerted! Time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f'")[:-3])

        if not self.track:
            # Sleep for our sampling rate
            time.sleep(self.period)

    def save_images(self, temp_data, debug=True):
        """ 
        Alerts the user with a Whatsapp message
        """

        if debug:
            print("The temp_data array: ")
            print(temp_data)      

        bicubics = []

        for i in range(len(temp_data)):

            pixels = []
            points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
            grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
        
            for row in temp_data[i]:
                pixels = pixels + row

            bicubics.append(griddata(points, pixels, (grid_x, grid_y), method='cubic'))

        if debug:
            print("The bicubics array: ")
            print(bicubics)

        plt.imsave('/home/pi/Desktop/Projects/SIOT_Project/output_images/' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f'")[:-3], bicubics[-1], format='png')

if __name__ == '__main__':

    sensor_data_node = AMG8833AdaptiveUploader()
