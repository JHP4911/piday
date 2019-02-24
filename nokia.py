#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  ##############################  NOTE  ############################# 
#  Though the code below does work, be warned.
#  At the time I wrote this code, I was pretty new to Python (and programming 
#  as such), and I only put it up there for a Stackexchange Code Review question:
#  https://codereview.stackexchange.com/questions/132682/pillow-based-basic-gui-library-for-an-lcd
#  As such, I used some weird, ineffective and/or un-pythonic concept here and there.
#  Though I did test all the functions/methods, and I don't recall any of them 
#  being buggy, the code would need a complete review and patch-up. I lack time, 
#  so don't expect that for a while from me. Feel free to fork this, or write
#  your own gui inspired by this.
#  ################################################################### 

#  Check main() for usage.

#  Copyright 2016 Gergely Nagy <passznemtudom@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
__author__ = "Gergely Nagy"
__license__ = "GPL"
__version__ = "0.1b"
__status__ = "development"


 
import time
from PIL import Image, ImageDraw, ImageFont, ImageChops

debugging = False

if not debugging or __name__!='__main__':
    # These device-specific modules are only neccessary if using a real Nokia 5110
    #   LCD screen, for debug usage (LcdCanvas.target is None) they can be left out
    import PCD8544 as LCD
    import Adafruit_GPIO.SPI as SPI


# Nokia LCD screen dimensions
LCD_WIDTH = 84
LCD_HEIGHT = 48




class LcdCanvas(object):
    """
    A GUI for the Nokia 5110 LCD screen. It features two kind of cards: image cards and textboxes.
    Cards are moveable images on the base image (normally a blank white/black one). Textboxes are a
    special type of cards: they show the given text, and their image is generated automatically.
    Cards are referenced by their (unique) ID.
    
    The class can also be used without a physical LCD screen if LcdCanvas.target_LCD == None.  
    """


    class Card(object):
        """
        A card is an image that is positioned on the canvas. The coordinates of it
        are the upper left corner's of the image, and defaults to (0, 0).
        """

        
        def __init__(self, image, priority=0):
            """
            :param image: the Image to be used as the card
            :param priority: the priority of the card, higher overlaps lower
            """
            self.image = None
            self.size = 0
            self.change_image(image)
            self.position = (0, 0)
            self.priority = priority
            self.visible = True

            
        def change_image(self, image):
            """
            changes the card's picture with the conversion if neccessary
            :param image: the new image of the card
            """
            self.image = image
            if self.image.mode != '1':
                self.image = self.image.convert(mode='1', dither=Image.NONE)
            self.size = self.image.size


        def invert(self):
            """inverts the image (useful for i.e. highlighting)"""
            
            self.image = ImageChops.invert(self.image)


        def shift(self, amount):
            """
            moves the card by the given relative coordinates
            :param amount: the horizontal and vertical amount of shifting in pixels, tuple
            """
            x = amount[0] + self.position[0]
            y = amount[1] + self.position[1]
            self.position = (x, y)


        def align(self, horizontal, vertical):
            """
            Moves the card to the given position of the screen.
            :param horizontal: horizontal alignment; "left", "center", "right", or None
            :param vertical: vertical alignment; "top", "center", "bottom", or None
            """
            x, y = self.position[0], self.position[1]
            
            if horizontal == 'left':
                x = 0
            elif horizontal == 'center':
                x = int((LCD_WIDTH - self.size[0])/2)
            elif horizontal == 'right':
                x = LCD_WIDTH - self.size[0]
                
            if vertical == 'top':
                y = 0
            elif vertical == 'center':
                y = int((LCD_HEIGHT - self.size[1])/2)
            elif vertical == 'bottom':
                y = LCD_WIDTH - self.size[1]

            self.position = (x, y)


    class Textbox(object):
        """A special type of card that consist of a text and a frame. Size is auto-managed."""
        
        def __init__(self, text, text_color=0, font=None, spacing=0, text_align='left', frame_width=0, priority=0):
            """
            :param text: the text of the card
            :param text_color: the color of the text, 0 for black on white, else white on black
            :param font: the font type of the text (ImageFont instance)
            :param spacing: spacing between the lines of the text
            :param text_align: align of the text within the box ('left', 'center' or 'right')
            :param frame_width: the width of the frame line in pixels
            :param priority: higher overlaps lower
            """
            self.position = (0, 0)
            self.priority = priority
            self.visible = True
            
            self.text = None
            self.text_color = None
            self.font = None
            self.spacing = None
            self.text_align = None
            self.frame_width = None
            self.size = None
            self.image = Image.new('1', (0,0))  # dummy Image for ImageDraw
            self.draw = ImageDraw.Draw(self.image)
             
            self.edit_propertities(text, text_color, font, spacing, text_align, frame_width)
            

        def edit_propertities(self, text=None, text_color=None, font=0, spacing=None, text_align=None, frame_width=None):
            """
            Changes the card's given propertities (the ones that implies redrawing it)
            :param text: the text of the card
            :param text_color: the color of the text, 0 for black on white, else white on black
            :param font: the font type of the text (ImageFont instance)
            :param spacing: spacing between the lines of the text
            :param text_align: align of the text ('left', 'center' or 'right')
            :param frame_width: the width of the frame line in pixels
            """
            if text is not None:
                self.text = text
            if text_color is not None:
                self.text_color = 0 if text_color==0 else 255
            if font != 0:
                self.font = font
            if spacing is not None:
                self.spacing = spacing
            if text_align is not None:
                self.text_align = text_align
            if frame_width is not None:
                self.frame_width = frame_width

            x = self.draw.textsize(text)[0] + 2 + 2 * self.frame_width
            y = self.draw.textsize(text)[1] + 2 + 2 * self.frame_width
            self.size = (x, y)
            self.image = Image.new('1', self.size, (255 if self.text_color==0 else 0))
            self.draw = ImageDraw.Draw(self.image)

            text_coords = (self.frame_width + 1, self.frame_width + 1)
            #drawing text:
            self.draw.multiline_text(text_coords, self.text, fill=self.text_color, font=self.font,
                                     spacing=self.spacing, align=self.text_align)
            #drawing frame:
            for i in range(self.frame_width):
                self.draw.line([(i, 0), (i, self.size[1])], fill=self.text_color)  #left
                self.draw.line([(0, i), (self.size[0], i)], fill=self.text_color)  #top
                self.draw.line([(self.size[0]-1-i, 0), (self.size[0]-1-i, self.size[1])], fill=self.text_color)  #right
                self.draw.line([(0, self.size[1]-1-i), (self.size[0]), self.size[1]-1-i], fill=self.text_color)  #bottom



        def invert(self):
            """Inverts the image (useful for i.e. highlighting)."""
            
            self.image = ImageChops.invert(self.image)


        def shift(self, amount):
            """
            Moves the card by the given relative coordinates.
            :param amount: the horizontal and vertical amount of shifting in pixels, tuple
            """
            x = amount[0] + self.position[0]
            y = amount[1] + self.position[1]
            self.position = (x, y)


        def align(self, horizontal=None, vertical=None):
            """
            Moves the card to the given position; set None to do not change. 
            :param horizontal: horizontal alignment ('left', 'center', 'right' or None)
            :param vertical: vertical alignment ('top', 'center', 'bottom' or None)
            """
            x, y = self.position[0], self.position[1]
            if horizontal == 'left':
                x = 0
            elif horizontal == 'center':
                x = int((LCD_WIDTH - self.size[0])/2.0)
            elif horizontal == 'right':
                x = LCD_WIDTH - self.size[0]

            if vertical == 'top':
                y = 0
            elif vertical == 'center':
                y = int((LCD_HEIGHT - self.size[1])/2.0)
            elif vertical == 'bottom':
                y = LCD_WIDTH - self.size[0]

            self.position = (x, y)


    def __init__(self, target, base_color=1, base=None):
        """
        :param target: the LCD instance of the target Nokia 5110 LCD screen (use None for debug without an LCD)
        :param base_color: 0 for black, else white (if base == None)
        :param base: the base image on what the cards are drawn
        """
        self.LCD = target
        if self.LCD is not None:
            self.LCD.clear()
        if base is not None:
            self.base = base
            if self.base.size != (LCD_WIDTH, LCD_HEIGHT):
                self.base = self.base.resize((LCD_WIDTH, LCD_HEIGHT))
            if self.base.mode != '1':
                self.base = self.base.convert(mode='1', dither=Image.NONE)
        else:
            self.base = Image.new('1', (LCD_WIDTH, LCD_HEIGHT), (0 if base_color==0 else 255))

        #dictionary of all the image cards and textboxes. Keys are
        #the card_IDs, and the vaules are the cards themselves.
        self._cards = {}


    def add_card(self, card_ID, image, priority=0):
        """
        Adds a new card to the canvas.
        :param card_ID: the name of the card, should be unique
        :param image: the image of the card
        :param position: the position of the card ('s upper left corner)
        :param priority: the card with higher priority is drawn above the one with lower priority
        """
        if card_ID in self._cards.keys():
            raise ValueError("ID already exists")
            
        card = self.Card(image, priority)
        self._cards[card_ID] = card


    def add_textbox(self, card_ID,  text, text_color=0, font=None, spacing=0, align='left', frame_width=0, priority=0):
        """
        Adds a new textbox to the cards with the given propertities.
        :param card_ID: the name of the card, should be unique
        :param text: the text of the card
        :param text_color: the color of the text, 0 for black on white, else white on black
        :param font: the font type of the text (ImageFont instance)
        :param spacing: spacing between the lines of the text
        :param text_align: align of the text ('left', 'center' or 'right')
        :param frame_width: the width of the frame line in pixels
        :param priority: the card with higher priority is drawn above the one with lower priority
        """        
        if card_ID in self._cards.keys():
            raise ValueError("ID already exists")
        textbox = self.Textbox(text, text_color, font, spacing, align, frame_width, priority)
        self._cards[card_ID] = textbox


    def get_card(self, card_ID):
        """Returns the card itself, useful for reading their propertities."""

        return self._cards[card_ID]

        
    def edit_card_image(self, card_ID, image):
        """Changes the card's image"""
        
        try:
            self._cards[card_ID].change_image(image)
        except KeyError:
            raise ValueError("Invaild card ID")
        except AttributeError as e:
            raise TypeError("edit_card_image used on a Textbox", e)
            

    def edit_textbox(self, card_ID, text=None, text_color=None, font=0, spacing=None, align=None, frame_width=None):
        """Edits the textbox card's propertities. None means no change."""
        
        try:
            self._cards[card_ID].edit_propertities(text, text_color, font, spacing, align, frame_width)
        except KeyError:
            raise ValueError("Invaild card ID")
        except AttributeError as e:
            raise TypeError("edit_textbox called on a non-Textbox card", e)


    def set_priority(self, card_ID, value):
        """Sets the card's priority"""
        
        try:
            self._cards[card_ID].priority = value    
        except KeyError:
            raise ValueError("Invaild card ID")


    def hide_card(self, card_ID):
        """Makes the card hidden."""

        self._cards[card_ID].visible = False


    def show_card(self, card_ID):
        """Makes the card visible."""
        
        self._cards[card_ID].visible = True

            
    def set_pos(self, card_ID, pos):
        """sets the card's position."""
        
        assert type(pos) is tuple
        try:
            self._cards[card_ID].position = pos
        except KeyError:
            raise ValueError("Invaild card ID")


    def shift(self, card_ID, amount):
        """Moves the card by the given amount of pixels.
            :param amount: the horizontal and vertical amount of shifting in pixels; tuple"""
        
        try:
            self._cards[card_ID].shift(amount)
        except KeyError:
            raise ValueError("Invaild card ID")


    def align(self, card_ID, horizontal, vertical):
        """Aligns the card to the given position."""
        
        try:
            card = self._cards[card_ID]
            card.align(horizontal, vertical)
        except KeyError:
            raise ValueError("Invaild card ID") 


    def invert(self, card_ID):
        """Inverts the card's colour"""
        
        try:
            self._cards[card_ID].invert()
        except KeyError:
            raise ValueError("Invaild card ID")


    def delete_card(self, card_ID):
        """Deletes the card."""
        
        try:
            del self._cards[card_ID]
        except ValueError:
            raise ValueError("Invaild card ID")



    def construct_screen(self):
        """Flattens the canvas."""
            
        screen = self.base.copy()
        sorted_cards = sorted(self._cards.values(), key=lambda x: x.priority)   # sort the cards according to their priorities
        for card in sorted_cards:
            screen.paste(card.image, card.position)
        screen = screen.convert(mode='1', dither=Image.NONE)
        
        return screen


    def update_screen(self):
        """If self.LCD is specified, this outputs the canvas to it."""
        
        screen = self.construct_screen()
        if self.LCD is not None:
            self.LCD.image(screen)
            self.LCD.display()


    def debug_show_screen(self):
        """Outputs the canvas to the monitor instead of the LCD."""
        # note that normally the code is runned as root, and Image.show() does not work this way!
        self.construct_screen().show()





def main():
    """
    A test code that uses almost all functions of the libary. Outputs to the LCD screen (normal usage).
    """
    
    # pins of the Nokia LCD are connected to these GPIO pins
    LCD_BL = 22
    LCD_DC = 17
    LCD_RST = 27
    LCD_SPI_PORT = 0
    SPI_DEVICE = 0

    #lcd=None
    lcd = LCD.PCD8544(LCD_DC, LCD_RST, spi=SPI.SpiDev(LCD_SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
    base = Image.new('RGB', (100,100), (200,0,0))
    canvas = LcdCanvas(lcd, base)

    square = Image.new('RGB', (10, 10), (0, 0, 0))
    canvas.add_card('square', square, 5)
    canvas.add_textbox('hodor', "Hodor\nhodor hodor\nhodor.", align='center', frame_width=1, priority=10)
    canvas.add_textbox('valmorg', "Valar\nMorghulis", align='right', frame_width=3, priority=1000)
    canvas.update_screen()
    print(1)
    time.sleep(2)
    
    canvas.align('valmorg', 'center', 'center')
    canvas.align('hodor', 'right', 'bottom')
    canvas.update_screen()
    print(2)
    time.sleep(2)
    
    canvas.invert('valmorg')
    canvas.update_screen()
    print(3)
    time.sleep(2)

    canvas.set_pos('hodor', (10, 10))
    canvas.shift('valmorg', (-5, 20))
    canvas.update_screen()
    print(4)
    time.sleep(2)

    rectangle = Image.new('HSV', (10, 20), (10, 20, 30))
    canvas.edit_card_image('square', rectangle)
    canvas.edit_textbox('hodor', text=".rodoh\nrodoh rodoh\nrodoH", spacing=2, align='left', frame_width=0)
    canvas.set_priority('valmorg', 0)
    canvas.update_screen()
    print(5)
    time.sleep(2)

    canvas.remove_card('valmorg')
    canvas.update_screen()


def debug_main():
    """
    A test code identical to main(), but outputs to the monitor, thus does not depend on the
    LCD libaries and doesn't need the assembled LCD.
    """
    lcd = None
    base = Image.new('RGB', (100,100), (200,0,0))
    canvas = LcdCanvas(lcd, base)

    square = Image.new('RGB', (10, 10), (0, 0, 0))
    canvas.add_card('square', square, priority=5)
    canvas.add_textbox('hodor', "Hodor\nhodor hodor\nhodor.", align='center', frame_width=1, priority=1)
    canvas.add_textbox('valmorg', "Valar\nMorghulis", align='right', frame_width=3, priority=10)
    canvas.debug_show_screen()
    time.sleep(0.5)
    
    canvas.align('valmorg', 'center', 'center')
    canvas.align('hodor', 'right', 'bottom')
    canvas.debug_show_screen()
    time.sleep(0.5)
    
    canvas.invert('valmorg')
    canvas.debug_show_screen()
    time.sleep(0.5)

    canvas.set_pos('hodor', (10, 10))
    canvas.shift('valmorg', (-5, 20))
    canvas.debug_show_screen()
    time.sleep(0.5)

    rectangle = Image.new('HSV', (10, 20), (10, 20, 30))
    canvas.edit_card_image('square', rectangle)
    canvas.edit_textbox('hodor', text=".rodoh\nrodoh rodoh\nrodoH", align='left', frame_width=0)
    canvas.set_priority('valmorg', 0)
    canvas.debug_show_screen()
    time.sleep(0.5)

    canvas.delete_card('valmorg')
    canvas.debug_show_screen()
    
    
if __name__=='__main__':

    main()
