#!/usr/bin/python
# coding: utf-8

"""
#############################################################################################################
#  Andrea Favero 15 March 2024
#
# This script relates to CUBOTino micro, an extremely small and simple Rubik's cube solver robot 3D printed
# CUBOTino micro is the smallest version of the CUBOTino versions
# This specific script manages the display, and it's imported by Cubotino_m.py and Cubotino_m_servos.py
#
#############################################################################################################
"""


from Cubotino_m_settings_manager import settings as settings   # custom library managing the settings from<>to the settings files
from PIL import Image, ImageDraw, ImageFont  # classes from PIL for image manipulation
import ST7789                                # library for the TFT display with ST7789 driver 
import os.path, pathlib                      # libraries for path management



class Display:
    display_initialized = False
    def __init__(self):
        """ Imports and set the display.
            (https://shop.pimoroni.com/products/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi).
            In my (AF) case 7.7€ from Aliexpress."""
                
        if not self.display_initialized:
            s = settings.get_settings()                               # settings are retrieved from the settings Class
            self.disp_width = int(s['disp_width'])                    # display width, in pixels
            self.disp_height = int(s['disp_height'])                  # display height, in pixels
            self.disp_offsetL = int(s['disp_offsetL'])                # Display offset on width, in pixels, Left if negative
            self.disp_offsetT = int(s['disp_offsetT'])                # Display offset on height, in pixels, Top if negative
            self.built_by = str(s['built_by'])                        # maker's name to add on the Cubotino logo
            self.built_by_x = int(s['built_by_x'])                    # x coordinate for maker's name on display
            self.built_by_fs = int(s['built_by_fs'])                  # font size for the maker's name on display
            self.display_settings = True                              # display_settings is set True
        
        if not self.display_settings:                                 # case display_settings is still False
            print("Error on loading the display parameters at Cubotino_m_display")
        
        self.disp = ST7789.ST7789(port=0, cs=0,                       # SPI and Chip Selection                  
                            dc=25, backlight=22,                      # GPIO pins used for the SPI and backlight control
                            width = self.disp_width,         #(AF 240)  # see note above for width and height !!!
                            height = self.disp_height,       #(AF 135)  # see note above for width and height !!!                         
                            offset_left = self.disp_offsetL, #(AF 40)   # see note above for offset  !!!
                            offset_top = self.disp_offsetT,  #(AF 53)   # see note above for offset  !!!
                            rotation = 0,                             # image orientation
                            invert = True,                            # image invertion
                            spi_speed_hz=10000000)                    # SPI frequency
        
        self.disp.set_backlight(0)                                    # display backlight is set off
        self.disp_w = self.disp.width                                 # display width, retrieved by display setting
        self.disp_h = self.disp.height                                # display height, retrieved by display setting
        disp_img = Image.new('RGB', (self.disp_w, self.disp_h),color=(0, 0, 0))   # display image generation, full black
        self.disp.display(disp_img)                                   # image is displayed
        if not self.display_initialized:                              # case display_initialized is set False
            print("\nDisplay initialized\n")                          # feedback is printed to the terminal
            self.display_initialized = True                           # display_initialized is set True
        
        # loading the CUBOTino logo
        folder = pathlib.Path().resolve()                             # active folder (should be home/pi/cube)
        fname = "Cubotino_m_Logo_265x212_BW.jpg"                      # file name with logo image
        fname = os.path.join(folder,fname)                            # folder and file name for the logo image
        if os.path.exists(fname):                                     # case the logo file exists
            logo = Image.open(fname)                                  # opens the CUBOTino logo image (jpg file)
            self.logo = logo.resize((self.disp_w, self.disp_h))       # resizes the image to match the display.
        else:                                                         # case the logo file does not exist
            print(f"\nNot found {fname}")                             # feedback is printedto terminal
            print("Cubotino logo image is missed\n")                  # feedback is printedto terminal
            self.logo = Image.new('RGB', (self.disp_w, self.disp_h), color=(0, 0, 0))  # full black screen as new image
            logo_text = ImageDraw.Draw(self.logo)                     # image is drawned
            f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)  # font and size
            f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 29)  # font and size
            logo_text.text((10, 44), "CUBOT", font=f1, fill=(255, 255, 255))  # text, font, white color
            logo_text.text((165, 56), "ino", font=f2, fill=(255, 255, 255))   # text, font, white color




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
        disp_draw.rectangle((x, y, x+barLength, y+barWidth), outline="white", fill=(0,0,0))    # outer bar border
        disp_draw.rectangle((x+gap, y+gap, filledPixels, y+barWidth-gap), fill=(255,255,255))  # bar filling
        
        self.disp.display(disp_img) # image is plotted to the display
        self.disp.set_backlight(1)  # display backlight is set on





    def show_cubotino(self, built_by='', x=25, fs=22):
        """ Shows the Cubotino logo on the display."""
        
        if built_by != '': 
            disp_draw = ImageDraw.Draw(self.logo)          # image is plotted to display
            font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)  # font1
            disp_draw.text((25, 4), "Andrea FAVERO's", font=font1, fill=(0, 0, 255))  # first row text test
            
            font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # font1
            disp_draw.text((80, 85), "Built by", font=font2, fill=(255, 255, 255))    # second row text test
            
            font3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)  # font1
            disp_draw.text((x, 106), built_by, font=font3, fill=(255, 0, 0))              # third row text test
        
        self.disp.display(self.logo)                       # draws the image on the display hardware.
        self.disp.set_backlight(1)                         # display backlight is set on





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




    def plot_status(self, cube_status, plot_color, startup=False):
        """ Function to print the cube sketch of the cube colors."""
        
        if startup:
            self.c = plot_color

            x_start = 30                                   # x coordinate for face top-left corner
            y_start = 4                                    # y coordinate for face top-left corner
            s = 2                                          # gap between faces
            self.d = 14                                    # facelet square side
            self.g = 1                                     # offset for xy origin-square of colored facelet
            self.gg = 2*self.g                             # offset for xy end-square of colored facelet
            
            # dict with the top-left coordinate of each face (not facelets !)
            starts={0:(x_start+3*self.d+  s, y_start),
                    1:(x_start+6*self.d+2*s, y_start+3*self.d+  s),
                    2:(x_start+3*self.d+  s, y_start+3*self.d+  s),
                    3:(x_start+3*self.d+  s, y_start+6*self.d+2*s),
                    4:(x_start,              y_start+3*self.d+  s),
                    5:(x_start+9*self.d+3*s, y_start+3*self.d+  s)}
            
            # coordinate origin for the 54 facelets
            tlc=[]                                         # list of all the top-left vertex coordinate for the 54 facelets
            for value in starts.values():                  # iteration over the 6 faces
                x_start=value[0]                           # x coordinate fo the face top left corner
                y_start=value[1]                           # y coordinate fo the face top left corner
                y = y_start                                # y coordinate value for the first 3 facelets
                for i in range(3):                         # iteration over rows
                    x = x_start                            # x coordinate value for the first facelet
                    for j in range(3):                     # iteration over columns
                        tlc.append((x, y))                 # x and y coordinate, as list, for the top left vertex of the facelet is appendended
                        x = x+self.d                       # x coordinate is increased by square side
                        if j == 2: y = y+self.d            # once at the second column the row is incremented
            self.tlc = tuple(tlc)                          # tlc list is converted to tuple
            
            self.disp_img = Image.new('RGB', (self.disp_w, self.disp_h), color=(0, 0, 0))  # full black image
            self.disp_draw = ImageDraw.Draw(self.disp_img) # image is drawned
            
        
        # below part gets updated at every new cube_status sent
        for i, color in enumerate(cube_status):            # iteration over the 54 facelets interpreted colors
            B,G,R = self.c[color]                          # BGR values of the assigned colors for the corresponding detected color
            x = self.tlc[i][0]+self.g                      # x coordinate for the origin-square colored facelet
            y = self.tlc[i][1]+self.g                      # y coordinate for the origin-square colored facelet
            dx = x + self.d - self.gg                      # x coordinate for the end-square colored facelet
            dy = y + self.d - self.gg                      # y coordinate for the end-square colored facelet
            self.disp_draw.rectangle((x, y, dx, dy), (R,G,B))   # cube sketch grid
        
        self.disp.display(self.disp_img)                   # image is drawned
        self.disp.set_backlight(1)                         # display backlight is set on
    
    
    
    
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
    
