#!/usr/bin/python
# coding: utf-8

"""
#############################################################################################################
#  Andrea Favero 06 May 2023
#
# This script relates to CUBOTino micro, an extremely small and simple Rubik's cube solver robot 3D printed
# CUBOTino micro is the smallest version of the CUBOTino versions
# This specific script manages the display, and it's imported by Cubotino_m.py and Cubotino_m_servos.py
#
#############################################################################################################
"""


from PIL import Image, ImageDraw, ImageFont  # classes from PIL for image manipulation
import ST7789                                # library for the TFT display with ST7789 driver 
import os.path, pathlib, json                # library for the json parameter parsing for the display
from getmac import get_mac_address           # library to get the device MAC ddress
from get_macs_AF import get_macs_AF          # import the get_macs_AF function
macs_AF = get_macs_AF()                      # mac addresses of AF bots are retrieved



class Display:
    def __init__(self):
        """ Imports and set the display.
            (https://shop.pimoroni.com/products/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi).
            In my (AF) case 7.7€ from Aliexpress."""
                
        
        
        # convenient choice for Andrea Favero, to upload the settings fitting my robot, via mac check
        folder = pathlib.Path().resolve()                             # active folder (should be home/pi/cube)  
        eth_mac = get_mac_address().lower()                           # mac address is retrieved
        if eth_mac in macs_AF:                                        # case the script is running on AF (Andrea Favero) robot
            pos = macs_AF.index(eth_mac)                              # returns the mac addreess position in the tupple
            fname = self.get_fname_AF('Cubotino_m_settings.txt', pos) # AF robot settings (do not use these at the start)
        else:                                                         # case the script is not running on AF (Andrea Favero) robot
            fname = os.path.join(folder,'Cubotino_m_settings.txt')    # folder and file name for the settings, to be tuned
        
        if os.path.exists(fname):                                     # case the settings file exists
            with open(fname, "r") as f:                               # settings file is opened in reading mode
                settings = json.load(f)                               # json file is parsed to a local dict variable
            try:
                disp_width = int(settings['disp_width'])              # display width, in pixels
                disp_height = int(settings['disp_height'])            # display height, in pixels
                disp_offsetL = int(settings['disp_offsetL'])          # Display offset on width, in pixels, Left if negative
                disp_offsetT = int(settings['disp_offsetT'])          # Display offset on height, in pixels, Top if negative
            except:
                print('error on converting imported parameters to int') # feedback is printed to the terminal
        else:                                                         # case the settings file does not exists, or name differs
            print('could not find the file: ', fname)                 # feedback is printed to the terminal 

        
        self.disp = ST7789.ST7789(port=0, cs=0,                       # SPI and Chip Selection                  
                            dc=25, backlight=22,                      # GPIO pins used for the SPI and backlight control
                            width=disp_width,            #(AF 240)    # see note above for width and height !!!
                            height=disp_height,          #(AF 135)    # see note above for width and height !!!                         
                            offset_left=disp_offsetL,    #(AF 40)     # see note above for offset  !!!
                            offset_top= disp_offsetT,    #(AF 53)     # see note above for offset  !!!
                            rotation=0,                               # image orientation
                            invert=True, spi_speed_hz=10000000)       # image invertion, and SPI     
        
        self.disp.set_backlight(0)                                    # display backlight is set off
        self.disp_w = self.disp.width                                 # display width, retrieved by display setting
        self.disp_h = self.disp.height                                # display height, retrieved by display setting
        disp_img = Image.new('RGB', (self.disp_w, self.disp_h),color=(0, 0, 0))   # display image generation, full black
        self.disp.display(disp_img)                                   # image is displayed




    def set_backlight(self, value):
        """Set the backlight on/off."""
        self.disp.set_backlight(value)




    def clean_display(self):
        """ Cleans the display by settings all pixels to black."""

        disp_img = Image.new('RGB', (self.disp_w, self.disp_h), color=(0, 0, 0))  # full black screen as new image
        self.disp.display(disp_img)                                          # display is shown to display




    def show_on_display(self, r1,r2,x1=20,y1=15,x2=20,y2=70,fs1=26,fs2=26):
        """Shows text on two rows, with parameters to generalize this function; Parameters are
            r1, r2: text for row1 and row2
            x1, x2: x coordinate for text at row1 and row2
            y1, y2: y coordinate for text at row1 and row2
            fs1, fs2: font size for text at row1 and row2
            """
        
        font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs1)  # font and size for first text row
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs2)  # font and size for second text row
        disp_img = Image.new('RGB', (self.disp_w, self.disp_h), color=(0, 0, 0)) 
        disp_draw = ImageDraw.Draw(disp_img)
        disp_draw.text((x1, y1), r1, font=font1, fill=(255, 255, 255))    # first text row start coordinate, text, font, white color
        disp_draw.text((x2, y2), r2, font=font2, fill=(255, 255, 255))    # second text row start coordinate, text, font, white color
        self.disp.display(disp_img)                                       # image is plot to the display




    def display_progress_bar(self, percent, scrambling=False):
        """ Function to print a progress bar on the display."""
        
        w = self.disp_w                                            # display width, retrieved by display setting
        
        # percent value printed as text 
        fs = 48                 # font size
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)     # font and its size
        text_x = int(self.disp_w/2 - (fs*len(str(percent))+1)/2)                   # x coordinate for the text starting location         
        text_y = 6                                                           # y coordinate for the text starting location
        disp_img = Image.new('RGB', (self.disp_w, self.disp_h), color=(0, 0, 0)) 
        disp_draw = ImageDraw.Draw(disp_img)
        disp_draw.text((text_x, text_y), str(percent)+'%', font=font, fill=(255, 255, 255))    # text with percent value
        
        # percent value printed as progress bar filling 
        x = 10                  # x coordinate for the bar starting location
        y = 65                  # y coordinate for the bar starting location
        gap = 5                 # gap in pixels between the outer border and inner filling (even value is preferable) 
        if not scrambling:      # case the robot is solving a cube
            barWidth = 48       # width of the bar, in pixels
        elif scrambling:        # case the robot is scrambling a cube
            barWidth = 22       # width of the bar, in pixels
            fs = 28             # font size
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)  # font and its size
            disp_draw.text((15, 98), 'SCRAMBLING', font=font, fill=(255, 255, 255))                # SCRAMBLING text
            
        barLength = w-2*x-4 #210         # lenght of the bar, in pixels
        filledPixels = int( x+gap +(barLength-2*gap)*percent/100)  # bar filling length, as function of the percent
        disp_draw.rectangle((x, y, x+barLength, y+barWidth), outline="white", fill=(0,0,0))      # outer bar border
        disp_draw.rectangle((x+gap, y+gap, filledPixels, y+barWidth-gap), fill=(255,255,255)) # bar filling
        
        self.disp.display(disp_img) # image is plotted to the display




    def show_cubotino(self, built_by='', x=25, fs=22):
        """ Shows the Cubotino logo on the display."""
                
        image = Image.open("Cubotino_m_Logo_265x212_BW.jpg")       # opens the CUBOTino logo image (jpg file)
        image = image.resize((self.disp_w, self.disp_h))           # resizes the image to match the display.
        
        if built_by != '': 
            disp_draw = ImageDraw.Draw(image)                      # image is plotted to display
            font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)  # font1
            disp_draw.text((25, 4), "Andrea FAVERO's", font=font1, fill=(0, 0, 255))  # first row text test
            
            font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # font1
            disp_draw.text((80, 85), "Built by", font=font2, fill=(255, 255, 255))    # second row text test
            
            font3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)  # font1
            disp_draw.text((x, 106), built_by, font=font3, fill=(255, 0, 0))              # third row text test
        self.disp.display(image)                                   # draws the image on the display hardware.




    def show_face(self, side, colours=[]):
        """ Function to print a sketch of the cube face colours."""
        
        w = self.disp_w                                    # display width, retrieved by display setting
        h = self.disp_h                                    # display height, retrieved by display setting
        faces = ('', 'U', 'B', 'D', 'F', 'R', 'L')         # tuple of faces letters
        y_start = 10                                       # y coordinate for face top-left corner
        d = int(h-2*y_start)/3                             # facelet square side
        x_start = w-5-3*d                                  # x coordinate for face top-left corner
        gap = 5                                            # gap beftweem the facelets border and facelets coloured part
        
        font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)  # font1
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)  # font1
        disp_img = Image.new('RGB', (w, h), color=(0, 0, 0))  # full black image
        disp_draw = ImageDraw.Draw(disp_img)               # image is plotted to display
        disp_draw.text((20, 8), 'FACE', font=font1, fill=(255, 255, 255))   # first row text test
        disp_draw.text((15, 30), faces[side], font=font2, fill=(255, 255, 255))   # first row text test
        self.disp.set_backlight(1)                         # display backlight is set on
        
        fclt = 0
        y = y_start                                        # y coordinate value for the first 3 facelets
        for i in range(3):                                 # iteration over rows
            x = x_start                                    # x coordinate value for the first facelet
            for j in range(3):                             # iteration over columns
                disp_draw.rectangle((x, y, x+d, y+d), outline="white", fill=(0,0,0))   # outer bar border
                if len(colours)==9:                        # case colour is prodided
                    disp_draw.rectangle((x+gap, y+gap, x+d-gap-1, y+d-gap-1), colours[fclt]) #colours[fclt]) # bar filling
                x = x+d                                    # x coordinate is increased by square side
                if j == 2: y = y+d                         # once at the third column the row is incremented
                fclt+=1
        
        self.disp.display(disp_img) # image is plotted to the display




    def test_display(self):
        """ Test showing some text into some rectangles."""
        
        print("\nDisplay test for 20 seconds")
        print("Display shows rectangles, text and Cubotino logo")
        
        import time
        import RPi.GPIO as GPIO                                    # import RPi GPIO library
        GPIO.setwarnings(False)                                    # GPIO warning set to False to reduce effort on handling them
        GPIO.setmode(GPIO.BCM)                                     # GPIO modulesetting
        u_btn = 23                                                 # GPIO pin used by the uppert button
        b_btn = 24                                                 # GPIO pin used by the bottom button
        GPIO.setup(u_btn, GPIO.IN)                                 # set the upper button_pin as an input
        GPIO.setup(b_btn, GPIO.IN)                                 # set the bottom button_pin as an input
        
        w = self.disp_w                                            # display width, retrieved by display setting
        h = self.disp_h                                            # display height, retrieved by display setting
        
        font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)  # font1
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)  # font2
        disp_img = Image.new('RGB', (w, h), color=(0, 0, 0))       # full black image
        
        self.disp.set_backlight(1)                                 # display backlight is set on
        start = time.time()                                        # time refrence for countdown
        timeout = 20.5                                             # timeout
        while time.time() < start + timeout:                       # while loop until timeout
            
            if not GPIO.input(23) or not GPIO.input(24):           # case one of the buttons is pressed
                break                                              # while loop is interrupted
            
            t_left = int(round(timeout + start - time.time(),0))   # time left
            
            if t_left%2==0:                                        # case the time left is even
                t_left_str = str(t_left)                           # string of time left
                pos = 184 if t_left>9 else 199                     # position x for timeout text
                disp_img = Image.new('RGB', (w, h), color=(0, 0, 0))   # full black image
                disp_draw = ImageDraw.Draw(disp_img)               # image is plotted to display

                disp_draw.rectangle((2, 2, w-4, h-4), outline="white", fill=(0,0,0))    # border 1
                disp_draw.rectangle((5, 5, w-7, h-7), outline="white", fill=(0,0,0))    # border 2
                disp_draw.rectangle((8, 8, w-10, h-10), outline="white", fill=(0,0,0))  # border 3
                disp_draw.rectangle((172, 84, w-14, h-14), outline="red", fill=(0,0,0)) # border for timeout
                
                disp_draw.text((pos, h-45), t_left_str , font=font2, fill=(255, 0, 0))  # timeout text
                disp_draw.text((30, 25), 'DISPLAY', font=font1, fill=(255, 255, 255))   # first row text test
                disp_draw.text((33, 75), 'TEST', font=font1, fill=(255, 255, 255))      # second row text test
                self.disp.display(disp_img)                        # image is plotted to the display
                time.sleep(0.1)                                    # little sleeping time   
            else:                                                  # case the time left is odd
                self.show_cubotino()                               # cubotino logo is displayed
                time.sleep(0.1)                                    # little sleeping time
        
        if time.time() >= start + timeout:                         # case the while loop hasn't been interrupted
            time.sleep(1)                                          # little sleeping time
        self.clean_display()                                       # display is set to full black
        self.disp.set_backlight(0)                                 # display backlight is set off
        time.sleep(1)                                              # little sleeping time
        print("Display test finished\n")                           # feedback is printed to the terminal




    def test_btns(self):
        """ Buttons test: Text changes color when buttons are pressedTest showing some text into some rectangles."""
        
        print("\nButtons test for 30 seconds")
        print("Text color changes when buttons are pressed")
    
        import time
        import RPi.GPIO as GPIO                                    # import RPi GPIO library
        GPIO.setwarnings(False)                                    # GPIO warning set to False to reduce effort on handling them
        GPIO.setmode(GPIO.BCM)                                     # GPIO modulesetting
        u_btn = 23                                                 # GPIO pin used by the uppert button
        b_btn = 24                                                 # GPIO pin used by the bottom button
        GPIO.setup(u_btn, GPIO.IN)                                 # set the upper button_pin as an input
        GPIO.setup(b_btn, GPIO.IN)                                 # set the bottom button_pin as an input
        
        w = self.disp_w                                            # display width, retrieved by display setting
        h = self.disp_h                                            # display height, retrieved by display setting
        
        font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)  # font1
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)  # font2
        disp_img = Image.new('RGB', (w, h), color=(0, 0, 0))       # full black image
        
        self.disp.set_backlight(1)                                 # display backlight is set on
        start = time.time()                                        # time refrence for countdown
        timeout = 30                                               # timeout
        while time.time() < start + timeout:                       # while loop until timeout
            t_left = str(int(round(timeout + start - time.time(),0)))   # time left
            pos = 195 if len(t_left)>1 else 210                    # position x for timeout text
            col1 = (0, 255, 0) if not GPIO.input(23) else (255, 255, 255) # case upper button is pressed                        
            col2 = (0, 255, 0) if not GPIO.input(24) else (255, 255, 255) # case bottom button is pressed
            if not GPIO.input(23) and not GPIO.input(24):          # case both buttons are pressed
                col1 = col2 = (255, 0, 0)                          # red color is assigned
            
            disp_draw = ImageDraw.Draw(disp_img)                   # image is plotted to display
            disp_draw.rectangle((183, h-42, w-4, h-4), outline="red", fill=(0,0,0))  # border for timeout
            disp_draw.text((pos, h-35), t_left , font=font2, fill=(255, 0, 0))      # timeout text
            disp_draw.text((20, 25), 'BUTTONS', font=font1, fill=col1)      # first row text test
            disp_draw.text((20, 75), 'TEST', font=font1, fill=col2)    # second row text test
            
            self.disp.display(disp_img)                            # image is plotted to the display
        
        self.show_cubotino()                                       # cubotino logo is show to display
        time.sleep(2)                                              # little delay
        self.clean_display()                                       # display is set to full black
        self.disp.set_backlight(0)                                 # display backlight is set off
        print("Buttons test finished\n")                           # feedback is printed to the terminal




    def get_fname_AF(self, fname, pos):
        return fname[:-4] + '_AF' + str(pos+1) + '.txt'



display = Display()

if __name__ == "__main__":
    """the main function can be used to test the display. """

    display.test_display()
    display.test_btns()
    display.set_backlight(0)


##### test show_face #####
#     import random
#     import time
#     colors_rgb = {'white':(255,255,255), 'red':(204,0,0), 'green':(0,132,0),
#               'yellow':(245,245,0), 'orange':(255,128,0), 'blue':(0,0,204)}   # bright colors assigned to the six faces colors
#     colors=('white', 'red', 'green', 'yellow', 'orange', 'blue')
#     for f in range(6):
#         rgb=[]
#         for i in range(9):
#             ref=(colors_rgb[colors[random.randint(0,5)]])
#             rgb.append(ref)
#         display.show_face(f+1,rgb)
#         time.sleep(1)
#     display.set_backlight(0)
###############
    
