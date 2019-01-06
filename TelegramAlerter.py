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

        self.image_count = len(os.listdir('/home/pi/Desktop/Projects/SIOT_Project/output_images/'))
        self.latest_image = ''

        while 1:
            time.sleep(1000)

    def handle(self, msg):

        self.check_images()

        chat_id = msg['chat']['id']
        command = msg['text']

        print("Got command: %s" % command)

        if command =='/update':
            self.bot.sendMessage(chat_id, 'Update Requested!')

    def check_images(self):

        available_images = os.listdir('/home/pi/Desktop/Projects/SIOT_Project/output_images/'))
        new_image_count = len(available_images)

        if new_image_count > self.image_count:
            self.latest_image = available_images[-1]
            self.image_count = new_image_count

            self.send_image(self.latest_image)

    def send_image(self, filepath):
        self.bot.sendPhoto(chat_id, open('/home/pi/Desktop/Projects/SIOT_Project/output_images/'+filepath+'.png', 'rb'))





