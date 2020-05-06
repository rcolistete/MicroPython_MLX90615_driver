"""
MicroPython driver for MLX90615 IR temperature I2C sensor :
https://github.com/rcolistete/MicroPython_MLX90615_driver
Version for BBC Micro:bit with simple read functions, without error checking : 0.2.1 @ 2020/05/04
Author: Roberto Colistete Jr. (roberto.colistete at gmail.com)
License: MIT License (https://opensource.org/licenses/MIT)
"""

__version__ = '0.2.1'


from micropython import const


MLX90615_I2C_DEFAULT_ADDR = const(0x5B)

_REG_ID_LOW = const(0x1E)              # EEPROM register - ID number low
_REG_ID_HIGH = const(0x1F)             # EEPROM register - ID number high
_REG_AMBIENT_TEMP = const(0x26)        # RAM register - ambient temperature register
_REG_OBJECT_TEMP  = const(0x27)        # RAM register - object temperature register 


class MLX90615:
    def __init__(self, i2c, address=MLX90615_I2C_DEFAULT_ADDR):
        self.i2c = i2c
        self.address = address
        self.register_buf = bytearray(1)
        self.buf = bytearray(3)

    def read16(self, register):
        self.register_buf[0] = register
        self.i2c.write(self.address, self.register_buf, repeat=True)
        self.buf =	self.i2c.read(self.address, 3, repeat=True)
        lsb = self.buf[0]
        msb = self.buf[1]
        return lsb | (msb << 8)

    def read_ambient_temp(self):
        return (self.read16(_REG_AMBIENT_TEMP))*2 - 27315

    def read_object_temp(self):
        return (self.read16(_REG_OBJECT_TEMP))*2 - 27315

    def read_id(self):
        return self.read16(_REG_ID_LOW) | (self.read16(_REG_ID_HIGH) << 16)

    def read_eeprom(self):
        eeprom_data = [0]*0x10
        for register in range(0x10, 0x20):
            eeprom_data[register - 0x10] = self.read16(register)
        return eeprom_data
