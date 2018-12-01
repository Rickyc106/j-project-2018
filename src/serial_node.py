#!/usr/bin/env python

import serial
import time
import struct
import sys
from numpy import *
from easy_pyserial import *

ardu_byte_size = {
	"int": 2,
	"float": 4,
	"bool": 1,
	"char": 1,
	"byte": 1,
	"long": 4,
	"short": 2,
	"double": 4,
}

class SerialNode:
	def __init__(self, port, baud, timeout):
		self.commands = zeros(8)
		self.ser = serial.Serial(port, baud, timeout = timeout)

	def begin(self, datatype, length):
		buffer_size = ardu_byte_size[datatype] * length
		ET = EasyTransfer(buffer_size, self.ser)

		return ET

	def main(self, _ETout, _ETin, data_out):
		self.ser.flushInput()
		self.ser.flushOutput()

		_ETout.sendData(data_out)
		_ETin.receiveData()

		print _ETin.data
		print ""

if __name__ == '__main__':
	try:
		print "Serial Node is Alive!"

		SN = SerialNode('/dev/ttyACM0', "115200", "1")

		ETout = SN.begin("float", 2)
		ETin = SN.begin("float", 2)

		SN.main()

	except KeyboardInterrupt:
		pass