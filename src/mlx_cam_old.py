"""!
@file mlx_cam.py
This file contains a wrapper that facilitates the use of a Melexis MLX90640
thermal infrared camera for general use. The wrapper contains a class MLX_Cam
whose use is greatly simplified in comparison to that of the base class,
@c class @c MLX90640, by mwerezak, who has a cool fox avatar, at
@c https://github.com/mwerezak/micropython-mlx90640

To use this code, upload the directory @c mlx90640 from mwerezak with all its
contents to the root directory of your MicroPython device, then copy this file
to the root directory of the MicroPython device.

There's some test code at the bottom of this file which serves as a beginning
example.

@author mwerezak Original files, Summer 2022
@author JR Ridgely Added simplified wrapper class @c MLX_Cam, January 2023
@copyright (c) 2022 by the authors and released under the GNU Public License,
    version 3.
"""

## @mainpage
#  The documentation of interest is for class MLX_Cam
#
#  @image html "ir_selfie_0.png"

import utime as time
from machine import Pin, I2C
import mlx90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern

import numpy as np


class MLX_Cam:
    """!
    @brief   Class which wraps an MLX90640 thermal infrared camera driver to
             make it easier to grab and use an image.
    """

    def __init__(self, i2c, address=0x33, pattern=ChessPattern,
                 width=NUM_COLS, height=NUM_ROWS):
        """!
        @brief   Set up an MLX90640 camera.
        @param   i2c An I2C bus which has been set up to talk to the camera;
                 this must be a bus object which has already been set up
        @param   address The address of the camera on the I2C bus (default 0x33)
        @param   pattern The way frames are interleaved, as we read only half
                 the pixels at a time (default ChessPattern)
        @param   width The width of the image in pixels; leave it at default
        @param   height The height of the image in pixels; leave it at default
        """
        ## The I2C bus to which the camera is attached
        self._i2c = i2c
        ## The address of the camera on the I2C bus
        self._addr = address
        ## The pattern for reading the camera, usually ChessPattern
        self._pattern = pattern
        ## The width of the image in pixels, which should be 32
        self._width = width
        ## The height of the image in pixels, which should be 24
        self._height = height

        # The MLX90640 object that does the work
        self._camera = mlx90640.MLX90640(i2c, address)
        self._camera.set_pattern(pattern)
        self._camera.setup()

        ## A local reference to the image object within the camera driver
        self._image = self._camera.image


    def ascii_image(self, array, pixel="██", textcolor="0;180;0"):
        """!
        @brief   Show low-resolution camera data as shaded pixels on a text
                 screen.
        @details The data is printed as a set of characters in columns for the
                 number of rows in the camera's image size. This function is
                 intended for testing an MLX90640 thermal infrared sensor.

                 A pair of extended ACSII filled rectangles is used by default
                 to show each pixel so that the aspect ratio of the display on
                 screens isn't too smushed. Each pixel is colored using ANSI
                 terminal escape codes which work in only some programs such as
                 PuTTY.  If shown in simpler terminal programs such as the one
                 used in Thonny, the display just shows a bunch of pixel
                 symbols with no difference in shading (boring).

                 A simple auto-brightness scaling is done, setting the lowest
                 brightness of a filled block to 0 and the highest to 255. If
                 there are bad pixels, this can reduce contrast in the rest of
                 the image.

                 After the printing is done, character color is reset to a
                 default of medium-brightness green, or something else if
                 chosen.
        @param   array An array of (self._width * self._height) pixel values
        @param   pixel Text which is shown for each pixel, default being a pair
                 of extended-ASCII blocks (code 219)
        @param   textcolor The color to which printed text is reset when the
                 image has been finished, as a string "<r>;<g>;<b>" with each
                 letter representing the intensity of red, green, and blue from
                 0 to 255
        """
        minny = min(array)
        scale = 255.0 / (max(array) - minny)
        for row in range(self._height):
            for col in range(self._width):
                pix = int((array[row * self._width + (self._width - col - 1)]
                           - minny) * scale)
                print(f"\033[38;2;{pix};{pix};{pix}m{pixel}", end='')
            print(f"\033[38;2;{textcolor}m")


    ## A "standard" set of characters of different densities to make ASCII art
    asc = " -.:=+*#%@"


    def ascii_art(self, array):
        """!
        @brief   Show a data array from the IR image as ASCII art.
        @details Each character is repeated twice so the image isn't squished
                 laterally. A code of "><" indicates an error, probably caused
                 by a bad pixel in the camera. 
        @param   array The array to be shown, probably @c image.v_ir
        """
        scale = 10 / (max(array) - min(array))
        offset = -min(array)
        for row in range(self._height):
            line = ""
            for col in range(self._width):
                pix = int((array[row * self._width + (self._width - col - 1)]
                           + offset) * scale)
                try:
                    the_char = MLX_Cam.asc[pix]
                    print(f"{the_char}{the_char}", end='')
                except IndexError:
                    print("><", end='')
            print('')
        return


    def get_csv(self, array, limits=None):
        """!
        @brief   Generate a string containing image data in CSV format.
        @details This function generates a set of lines, each having one row of
                 image data in Comma Separated Variable format. The lines can
                 be printed or saved to a file using a @c for loop.
        @param   array The array of data to be presented
        @param   limits A 2-iterable containing the maximum and minimum values
                 to which the data should be scaled, or @c None for no scaling
        """
        if limits and len(limits) == 2:
            scale = (limits[1] - limits[0]) / (max(array) - min(array))
            offset = limits[0] - min(array)
        else:
            offset = 0.0
            scale = 1.0
        for row in range(self._height):
            line = ""
            for col in range(self._width):
                pix = int((array[row * self._width + (self._width - col - 1)]
                          * scale) + offset)
                if col:
                    line += ","
                line += f"{pix}"
#             line += "\r\n"
            yield line
        return

    def calibrate(self, array):
        calArray = []
        array = np.subtract(array, calArray)

    """ def find_cent(self, array):"
        cent = max(array)
        maxEachRow = array.max(axis=0)
        maxEachCol = array.max(axis=1)
        for rowVal in maxEachRow:
            if maxEachRow[rowVal] == cent:
                centX = maxEachRow[rowVal]
        for colVal in maxEachCol:
            if maxEachCol[colVal] == cent:
                centY = maxEachCol[colVal]
        
        row = 0
        col = 0
        vline = 0
        for i in np.nditer(array, flags = ['external_loop'], order = 'F'): 
            if (row < centX-2 or row > centX+2) and (col > 1 or col < len(maxEachCol)):
                row += row
                pass
            else:
                for j in i:
                    if (col < centY-2 or col > centY+2) and (j > 1 or j < len(i)):
                        col += col
                        pass
                    else:
                        if i and i[j] == maxEachCol[col] and vline == 5:     #j == col and col == 5:
                            xy = [row,col]
                    col += col
            row += row """
    
    def find_cent(self,array):
        avgAr = [] #creates an list to hold averages of each section of split image (below)
        splitArrays = np.array_split(array,96) #splits image into 96 arrays (4 arrays per row of 8 values...)
        for n in range(splitArrays):   #determines the average value of each array and puts into average array
            avgAr.append(np.mean(n))
        maxArrayInd = enumerate(avgAr)  #Finds the index of the max average value
        maxAr = splitArrays[maxArrayInd]    #Is set equal to the max average array 
        compArr = [0, 0, 0, 0, 0, 0, 0, 0] #Comparable variable used to compare each 4 value sof camera to the maxAr 
        for guy in range(len(array)): #Iterates through every value in array
            compArr[guy%8] = array[guy] #Sets each value in the comparable list to the current value in array; uses remainder of 8 to iterate positions
            if guy%8 == 0 and guy > 0: #Ever 8 values, compares the compArr to the array found to have the maximum average
                if compArr == maxAr: #If they're the same, set the center point for the gun to target equal to the current index - 3 (about center of array)
                    cent = guy-3
        centX = self._width - int(cent % self._width)   #Finds the x distance by subtracting the remainder of the center index by the width from the width
        centY = self._height - int(cent % self._height) #Finds the y distance by subtracting the remainder of the center index by the height from the height
        return [centX, centY]
    '''
    for i in array(axis=0)

        for pix_index in range(len(array)):
            if left < (.8*cent) and pix_index ~= ([0,self._width,2*self._width])
    '''
    def find_hot(self, array):
        hot = max(array)
        for pix_index in range(len(array)):
            if array[pix_index] == hot:
                return [self._width - (pix_index % self._width), self._height - int(pix_index / self._width), int(hot)]
            
    '''def find_errX(self,X_pos):
        X_cent = int(self._width)/2 #Center pixel of camera...?
        X_err = X_pos-X_cent #Finds the difference between the position and center
        return X_err

    def find_errY(self,Y_pos):
        Y_cent = int(self._height)/2 #Center pixel of camera...?
        Y_err = Y_pos-Y_cent #Finds the difference between the position and center
        return Y_err'''
    
    def find_errX(self,Xcurr, Xwant):
        return (Xwant-Xcurr)/100 #Returns the percentage difference between the values 
    
    def find_errY(self,Ycurr, Ywant):
        return (Ywant-Ycurr)/100 #Returns the percentage difference between the values 

    def get_image(self):
        """!
        @brief   Get one image from a MLX90640 camera.
        @details Grab one image from the given camera and return it. Both
                 subframes (the odd checkerboard portions of the image) are
                 grabbed and combined. This assumes that the camera is in the
                 ChessPattern (default) mode as it probably should be.
        @returns A reference to the image object we've just filled with data
        """
        for subpage in (0, 1):
            while not self._camera.has_data:
                time.sleep_ms(50)
                print('.', end='')
            self._camera.read_image(subpage)
            state = self._camera.read_state()
            image = self._camera.process_image(subpage, state)

        return image


# The test code sets up the sensor, then grabs and shows an image in a terminal
# every ten and a half seconds or so.
## @cond NO_DOXY don't document the test code in the driver documentation
if __name__ == "__main__":

    # The following import is only used to check if we have an STM32 board such
    # as a Pyboard or Nucleo; if not, use a different library
    try:
        from pyb import info

    # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
    except ImportError:
        # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
        i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))

    # OK, we do have an STM32, so just use the default pin assignments for I2C1
    else:
        i2c_bus = I2C(1)

    print("MXL90640 Easy(ish) Driver Test")

    # Select MLX90640 camera I2C address, normally 0x33, and check the bus
    i2c_address = 0x33
    scanhex = [f'0x{addr:X}' for addr in i2c_bus.scan()]
    print(f"I2C Scan: {scanhex}")

    # Create the camera object and set it up in default mode
    camera = MLX_Cam(i2c_bus)

    while True:
        try:
            # Get and image and see how long it takes to grab that image
            print("Click.", end='')
            begintime = time.ticks_ms()
            image = camera.get_image()
            print(f" {time.ticks_diff(time.ticks_ms(), begintime)} ms")

            # Can show image.v_ir, image.alpha, or image.buf; image.v_ir best?
            # Display pixellated grayscale or numbers in CSV format; the CSV
            # could also be written to a file. Spreadsheets, Matlab(tm), or
            # CPython can read CSV and make a decent false-color heat plot.
            show_image = False
            show_csv = True
            if show_image:
                camera.ascii_image(image.buf)
            elif show_csv:
                for line in camera.get_csv(image.v_ir, limits=(0, 99)):
                    print(line)
            else:
                camera.ascii_art(image.v_ir)
            time.sleep_ms(300)

        except KeyboardInterrupt:
            break

    print ("Done.")

## @endcond End the block which Doxygen should ignore


