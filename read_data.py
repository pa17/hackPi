import time
import busio
import board
import adafruit_amg88xx

from datetime import datetime

SAMPLE_RATE = 1 # Hz

period = 1 / SAMPLE_RATE

class AMG8833Reader:
    """
    Reads and saves the data from the IR camera
    """

    def __init__(self):

        i2c = busio.I2C(board.SCL, board.SDA)
        self.amg = adafruit_amg88xx.AMG88XX(i2c)


        self.now = datetime.now()

        month = self.now.month
        day = self.now.day

        self.file = open('collected_data/', +  'w')

        while True:
            upload_status = self.check_time()

            if not upload_status:
                self.append_data()
            else:
                self.save_data()

    def check_time(self):

        last

        return


    def save_data(self):


    def append_data(self, debug=False):
        for row in self.amg.pixels:
            # Pad to 1 decimal place
            self.file.write(['{0:.1f}'.format(temp) for temp in row])
            self.file.write("")
        self.file.write("\n")

        if debug:
            for row in self.amg.pixels:
                # Pad to 1 decimal place
                print(['{0:.1f}'.format(temp) for temp in row])
                print("")
            print("\n")

        # Sleep for our sampling rate
        time.sleep(period)

if __name__ == '__main__':

    sensor_data_node = AMG8833Reader()