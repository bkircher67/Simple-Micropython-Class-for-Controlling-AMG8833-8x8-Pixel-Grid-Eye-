import machine
import AMG8833
from writer import Writer
from ssd1306 import SSD1306_I2C
import mono12
import time

# width and height of the display
WIDTH = const(128)
HEIGHT = const (64)


def rect_fill(ssd, x=0, y=0, w=WIDTH, h=HEIGHT, color = 0):
	"""
		supporting function to draw a box with either 0% (color=0), 50% (color=1) or 100% (color=2) fill
	
		x,y,w,h ... coordinates

		color ... color type
					0% (color=0), 
					50% (color=1) 
					100% (color=2)

	"""
	for _x in range(x, x + w):
		for _y in range(y, y + h):
			c = 0 if color == 0 else 1 if color == 2 else 1 if (_x % 2) == (_y % 2) else 0
			ssd.pixel(_x, _y, c)

# initualize the I2C bus (used for Display AND AMG8833)
sda_pin = machine.Pin(4)
scl_pin = machine.Pin(15)

i2c = machine.I2C(scl=scl_pin, sda=sda_pin, speed=400000)

# initialize display and AMG8833
ssd = SSD1306_I2C(WIDTH, HEIGHT, i2c)
amg = AMG8833.AMG8833(i2c, addr=0x69)

# initialize writer object for the display
wri2 = Writer(ssd, mono12, verbose=True)
Writer.set_clip(True, True)

while True:

	# get thermister value
	Writer.set_textpos(0, 0)
	wri2.printstring("%.2f" % amg.temperature())

	# get pixel data (as integer)
	data = amg.pixel()

	# find lowest and highest temperature on grid
	# calculate 'warm' and 'cold' values
	min = 65535
	max = 0

	for row in data:
		for item in row:
			max = item if item > max else max
			min = item if item < min else min

	delta = (max - min) / 3 # whole span / 3
	warm = max - delta
	cold = min + delta

	# show values on display
	Writer.set_textpos(10, 0)
	wri2.printstring("min=%.1f" % (min * 0.25))
	Writer.set_textpos(20, 0)
	wri2.printstring("max=%.1f" % (max * 0.25))
	Writer.set_textpos(30, 0)
	wri2.printstring("cold<%.1f" % (cold * 0.25))
	Writer.set_textpos(40, 0)
	wri2.printstring("warm>%.1f" % (warm * 0.25))

	# show 8x8 grid with different shades
	for r,row in enumerate(data):
		for c,item in enumerate(row):
			color = 2 if item > warm else 0 if item < cold else 1
			rect_fill(ssd,64 + r * 8 ,  c * 8, 8, 8, color)

	# refresh display
	ssd.show()
