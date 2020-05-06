"""
MicroPython driver for MLX90615 IR temperature I2C sensor :
https://github.com/rcolistete/MicroPython_MLX90615_driver
Version with simple read functions : 0.2.1 @ 2020/05/05
Author: Roberto Colistete Jr. (roberto.colistete at gmail.com)
License: MIT License (https://opensource.org/licenses/MIT)
"""

__version__ = '0.2.1'


MLX90615_I2C_DEFAULT_ADDR = const(0x5B)

_REG_ID_LOW = const(0x1E)              # EEPROM register - ID number low
_REG_ID_HIGH = const(0x1F)             # EEPROM register - ID number high
_REG_AMBIENT_TEMP = const(0x26)        # RAM register - ambient temperature register
_REG_OBJECT_TEMP  = const(0x27)        # RAM register - object temperature register 


class MLX90615:
    def __init__(self, i2c, address=MLX90615_I2C_DEFAULT_ADDR):
        self.i2c = i2c
        self.address = address
        self.buf = bytearray(3)

    def _crc8(self, icrc, data):
        crc = icrc ^ data
        for _ in range(8):
            crc <<= 1
            if crc & 0x0100:
                crc ^= 0x07
            crc &= 0xFF
        return crc

    def read16(self, register, crc_check=True):
        self.i2c.readfrom_mem_into(self.address, register, self.buf)
        lsb = self.buf[0]
        msb = self.buf[1]
        pec = self.buf[2]
        crc = 0
        if crc_check:
            crc = self._crc8(crc, self.address << 1)
            crc = self._crc8(crc, register)
            crc = self._crc8(crc, (self.address << 1) + 1)
            crc = self._crc8(crc, lsb)
            crc = self._crc8(crc, msb)
        if (not crc_check) or (pec == crc):
            return lsb | (msb << 8)
        else:
            raise Exception("PEC != CRC8 error in reading register {:02x}.".format(register))

    def read_ambient_temp(self, pec_check=True):
        try:
            t = self.read16(_REG_AMBIENT_TEMP, crc_check=pec_check)
        except Exception as err:
            raise Exception("Error reading ambient temperature.\n{}".format(err))
        else:
            if (t > 0x7FFF):
                raise Exception("Invalid ambient temperature error.")
            else:
                return t*2 - 27315

    def read_object_temp(self, pec_check=True):
        try:
            t = self.read16(_REG_OBJECT_TEMP, crc_check=pec_check)
        except Exception as err:
            raise Exception("Error reading object temperature.\n{}".format(err))
        else:
            if (t > 0x7FFF):
                raise Exception("Invalid object temperature error.")
            else:
                return t*2 - 27315

    def read_id(self, pec_check=True):
        try:
            return self.read16(_REG_ID_LOW, crc_check=pec_check) | (self.read16(_REG_ID_HIGH, crc_check=pec_check) << 16)
        except Exception as err:
            raise Exception("Error reading sensor ID.\n{}".format(err))

    def read_eeprom(self, pec_check=True):
        eeprom_data = [0]*0x10
        for register in range(0x10, 0x20):
            try:
                eeprom_data[register - 0x10] = self.read16(register, crc_check=pec_check)
            except Exception as err:
                raise Exception("Error reading EEPROM.\n{}".format(err))
        return eeprom_data
