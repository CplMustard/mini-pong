import pygame
import RPi.GPIO as GPIO
import io

class LedArray:
    """ A array of LED pixels arranged to form a screen """
    
    def __init__(self, screendim):
        self.width = screendim[0]
        self.height = screendim[1]
        self.dev = "/dev/spidev0.0"
        # Open SPI device
        self.spidev = file(self.dev, "wb")

    def reverseBytearrayOddLines(self, arrayofbytes):
        reverseoddlines = bytearray(self.width * self.height * 3 + 1)
    
        for x in range(self.height):
           for y in range(self.width):
             # Need to reverse every second line because it is a continuous strip
             if (x % 2) != 0:
                 screenloc = (x*self.width + self.width - y -1) * 3;
             else:
                 screenloc = (x*self.width +y)*3;
             reverseoddlines[screenloc] = arrayofbytes[(x*self.width +y)*3];
             reverseoddlines[screenloc + 1] = arrayofbytes[(x*self.width +y)*3 + 1];
             reverseoddlines[screenloc + 2] = arrayofbytes[(x*self.width +y)*3 + 2];
        return reverseoddlines

    def displayPygameScreen(self, pyscreen):
	flippedscreen = pygame.transform.flip(pyscreen, False, True)
        buffer = flippedscreen.get_buffer()
        bytesnoalpha = bytearray(self.width * self.height * 3 + 1)
        for x in range (self.height):
            for y in range (self.width):
                color = flippedscreen.get_at((y, x))
                screenloc = (x*self.width +y)*3;
     
                bytesnoalpha[screenloc] = color.r
                bytesnoalpha[screenloc + 1] = color.g
                bytesnoalpha[screenloc + 2] = color.b
    
        reverseoddlines = self.reverseBytearrayOddLines(bytesnoalpha)
        self.sendByteArrayToScreen(reverseoddlines);
   
    def displayImage(self, img):
        img    = img.resize((self.width, self.height), Image.ANTIALIAS)
        img    = img.transpose(Image.FLIP_TOP_BOTTOM)
        pixels = img.load()
        bytesnoalpha = bytearray(self.width * self.height * 3 + 1)
        for x in range (self.height):
            for y in range (self.width):
                pixelval = pixels[y, x]
                screenloc = (x*self.width +y)*3;
     
                bytesnoalpha[screenloc] = pixelval[0]
                bytesnoalpha[screenloc + 1] = pixelval[1]
                bytesnoalpha[screenloc + 2] = pixelval[2]
    
        reverseoddlines = self.reverseBytearrayOddLines(bytesnoalpha)
        self.sendByteArrayToScreen(reverseoddlines);
 
    def sendByteArrayToScreen (self, arrayofbytes):
        self.spidev.write(arrayofbytes)
        self.spidev.flush() 
