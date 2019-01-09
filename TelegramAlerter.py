import sys
import time
import random
import datetime
import telepot
import os


class TelegramAlerter:

    def __init__(self):

        self.bot = telepot.Bot('763948635:AAGjMoPM4lFfnz0qmebXB2rpssQ8AUllu1s')
        self.bot.message_loop(self.handle)

        print("I am listening...")

        self.available_images = sorted(os.listdir('/home/pi/Desktop/Projects/SIOT_Project/output_images/'))
        self.image_count = len(self.available_images)
        self.latest_image = self.available_images[-1]
                
        while True:
            self.check_images()
            time.sleep(1)

    def handle(self, msg):

        self.chat_id = msg['chat']['id']
        self.command = msg['text']

        print("Got command: %s" % self.command)

        if self.command =='/start':
            self.bot.sendMessage(self.chat_id, 'Autotracking started!')

        if self.command =='/update':
            self.bot.sendMessage(self.chat_id, 'Update Requested! Last threat detected on the ' + self.latest_image[:10] + ' at ' + self.latest_image[11:-5])
            self.bot.sendPhoto(self.chat_id, open('/home/pi/Desktop/Projects/SIOT_Project/output_images/'+self.latest_image, 'rb'))

        #self.check_images()

    def check_images(self):

        available_images = sorted(os.listdir('/home/pi/Desktop/Projects/SIOT_Project/output_images/'))
        new_image_count = len(available_images)
        
        print("Current Image Count: ", self.image_count, ", New Image Count: ", new_image_count)

        if new_image_count > self.image_count:
            print("New Photo Found: Sending...")
            self.latest_image = available_images[-1]
            self.image_count = new_image_count
            print("Sending image: ", self.latest_image)
            
            if self.latest_image != '':
                self.bot.sendMessage(self.chat_id, 'THREAT AUTODETECT! Somebody is at your window on the ' + self.latest_image[:10] + ' at ' + self.latest_image[11:-5])
                self.bot.sendPhoto(self.chat_id, open('/home/pi/Desktop/Projects/SIOT_Project/output_images/'+self.latest_image, 'rb'))
                
                time.sleep(5)

if __name__ == '__main__':

    TelegramAlerter = TelegramAlerter()



