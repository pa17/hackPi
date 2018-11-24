import time
import busio
import board
import adafruit_amg88xx
import json

from subprocess import call
import datetime

SAMPLE_RATE = 1 # Hz
SAMPLES_BETWEEN_TIME_CHECK = 10 # check time every 10th loop


class AMG8833Uploader:
    """
    Reads and saves the data from the IR camera
    """

    def __init__(self):

        # Init I2C and instantiate sensor on that bus
        i2c = busio.I2C(board.SCL, board.SDA)
        self.amg = adafruit_amg88xx.AMG88XX(i2c)

        # Period at which IR sensor is sampled
        self.period = 1 / SAMPLE_RATE

        # Time at boot-up for output file
        self.current_time = datetime.datetime.now()

        current_month = self.current_time.month
        current_day = self.current_time.day
        current_hour = self.current_time.hour

        if current_hour < 10:
            extra_digit = '0'
        else:
            extra_digit = ''

        # Output file
        self.filename = 'data_' + str(current_month) + str(current_day) + extra_digit + str(current_hour) + ".txt"
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

        # If hour has incremented or is back at 0 -> New hour has begun
        if new_time.hour > self.current_time.hour or new_time.hour == 0:

            new_month = new_time.month
            new_day = new_time.day
            new_hour = new_time.hour

            if new_hour < 10:
                extra_digit = '0'
            else:
                extra_digit = ''

            # Close file and upload it
            self.file.close()
            self.upload_file()

            # Create a new file
            self.filename = 'data_' + str(new_month) + str(new_day) + extra_digit + str(new_hour) + ".txt"
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
            row_data = ['{0:.1f}'.format(temp) for temp in row]
            data.append(row_data)

        line_data = {str(datetime.datetime.now()): data}
        json.dump(line_data, self.file)
        self.file.write('\n')

        if debug:
            debug_data = []
            for row in self.amg.pixels:
                # Pad to 1 decimal place
                debug_row_data = ['{0:.1f}'.format(temp) for temp in row]
                debug_data.append(debug_row_data)

            print(str(datetime.datetime.now()) + ";" + str(debug_data))
            print("\n")

        # Sleep for our sampling rate
        time.sleep(self.period)


if __name__ == '__main__':

    sensor_data_node = AMG8833Uploader()
