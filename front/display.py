#!/bin/env python

import spidev
import time
from datetime import datetime

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 4000000
spi.no_cs

digits = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67]
clock_dis = []

def to_display(now):
	clock_dis.clear()
	if now.second < 10:
		clock_dis.append(digits[now.second])	
		clock_dis.append(digits[0])
	else:
		clock_dis.append(digits[now.second%10])
		clock_dis.append(digits[now.second//10])
	if now.minute < 10:
		clock_dis.append(digits[now.minute])
		clock_dis.append(digits[0])
	else:
		clock_dis.append(digits[now.minute%10])
		clock_dis.append(digits[now.minute//10])
	if now.hour < 10:
		clock_dis.append(digits[now.hour])
		clock_dis.append(digits[0])
	else:
		clock_dis.append(digits[now.hour%10])
		clock_dis.append(digits[now.hour//10])

if __name__ == '__main__':
	try:
		while True:
			now = datetime.now()
			to_display(now)
			spi.writebytes(clock_dis)
			time.sleep(0.01)

	except KeyboardInterrupt:
		print()
		print('Exiting Program')

