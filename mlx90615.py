"""
MicroPython driver for MLX90615 IR temperature I2C sensor :
https://github.com/rcolistete/MicroPython_MLX90615_driver
Version: 0.1.6 @ 2020/04/20
Author: Roberto Colistete Jr. (roberto.colistete at gmail.com)
License: MIT License (https://opensource.org/licenses/MIT)
"""

__version__ = '0.1.6'


import time


MLX90615_I2C_DEFAULT_ADDR = const(0x5B)

_REG_SLAVE_I2C_ADDRESS = const(0x10)   # EEPROM register - slave I2C address
_REG_EMISSIVITY = const(0x13)          # EEPROM register - Emissivity
_REG_ID_LOW = const(0x1E)              # EEPROM register - ID number low
_REG_ID_HIGH = const(0x1F)             # EEPROM register - ID number high
_REG_RAW_IR_DATA = const(0x25)         # RAM register - raw IR data register
_REG_AMBIENT_TEMP = const(0x26)        # RAM register - ambient temperature register
_REG_OBJECT_TEMP  = const(0x27)        # RAM register - object temperature register 

_EEPROM_DEFAULT_TIME_MS = const(50)           # erase/write EEPROM time in ms


class MLX90615:
    def __init__(self, i2c, address=MLX90615_I2C_DEFAULT_ADDR):
        self.i2c = i2c
        self.address = address
        self.buf = bytearray(3)

    def crc8(self, icrc, data):
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
        pep = self.buf[2]
        crc = 0
        if crc_check:
            crc = self.crc8(crc, self.address << 1)
            crc = self.crc8(crc, register)
            crc = self.crc8(crc, (self.address << 1) + 1)
            crc = self.crc8(crc, lsb)
            crc = self.crc8(crc, msb)
        if (not crc_check) or (pep == crc):
            return lsb | (msb << 8)
        else:
            raise Exception("PEP != CRC8 error in reading register {:02x}.".format(register))

    def write16(self, register, data, read_check=True, eeprom_time=_EEPROM_DEFAULT_TIME_MS):
        lsb = data & 0x00FF
        msb = data >> 8        
        crc = self.crc8(0, self.address << 1)
        crc = self.crc8(crc, register)
        crc = self.crc8(crc, lsb)
        crc = self.crc8(crc, msb)
        self.buf[0] = lsb; self.buf[1] = msb; self.buf[2] = crc
        self.i2c.writeto_mem(self.address, register, self.buf)
        time.sleep_ms(eeprom_time)
        if read_check:
            try:
                data_read = self.read16(register)
            except Exception as err:
                raise Exception("Error reading after writing to EEPROM register {:02x}.\n{}".format(register, err))
            else:
                if data != data_read:
                    raise Exception("Error reading after writing to EEPROM register {:02x}.\n{}".format(register, err))

    def read_ambient_temp(self, pep_check=True):
        try:
            t = self.read16(_REG_AMBIENT_TEMP, crc_check=pep_check)
        except Exception as err:
            raise Exception("Error reading ambient temperature.\n{}".format(err))
        else:
            if (t > 0x7FFF):
                raise Exception("Invalid ambient temperature error.")
            else:
                return t*2 - 27315

    def read_object_temp(self, pep_check=True):
        try:
            t = self.read16(_REG_OBJECT_TEMP, crc_check=pep_check)
        except Exception as err:
            raise Exception("Error reading object temperature.\n{}".format(err))
        else:
            if (t > 0x7FFF):
                raise Exception("Invalid object temperature error.")
            else:
                return t*2 - 27315

    def read_raw_ir_data(self, pep_check=True):
        try:
            d = self.read16(_REG_RAW_IR_DATA, crc_check=pep_check)
        except Exception as err:
            raise Exception("Error reading raw IR data.\n{}".format(err))
        else:
            return d

    def read_eeprom(self, pep_check=True):
        eeprom_data = [0]*0x10
        for register in range(0x10, 0x20):
            try:
                eeprom_data[register - 0x10] = self.read16(register, crc_check=pep_check)
            except Exception as err:
                raise Exception("Error reading EEPROM.\n{}".format(err))
        return eeprom_data

    def read_id(self, pep_check=True):
        try:
            return self.read16(_REG_ID_LOW, crc_check=pep_check) | (self.read16(_REG_ID_HIGH, crc_check=pep_check) << 16)
        except Exception as err:
            raise Exception("Error reading sensor ID.\n{}".format(err))

    def read_i2c_address(self, pep_check=True):
        try:
            return self.read16(_REG_SLAVE_I2C_ADDRESS, crc_check=pep_check) & 0x007F
        except Exception as err:
            raise Exception("Error reading EEPROM I2C address.\n{}".format(err))

    def set_i2c_address(self, addr, eeprom_read_check=False, eeprom_write_time=_EEPROM_DEFAULT_TIME_MS):
        if self.address == 0:
            if (addr >= 0x08) and (addr <= 0x77):
                d = 0x3500 | addr       
                try:
                    time.sleep_ms(eeprom_write_time)
                    self.write16(_REG_SLAVE_I2C_ADDRESS, 0x0000, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                    time.sleep_ms(eeprom_write_time)
                except Exception as err:
                    raise Exception("Error erasing EEPROM I2C address.\n{}".format(err))
                else:
                    try:
                        self.write16(_REG_SLAVE_I2C_ADDRESS, d, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                        time.sleep_ms(eeprom_write_time)
                    except Exception as err:
                        raise Exception("Error writing EEPROM I2C address.\n{}".format(err))
            else:
                raise Exception("Error : new I2C address {:02x} out of range (0x01 <= address <= 0x7F).".format(addr))
        else:
            raise Exception("Current I2C address of MLX90615 should be 0x00 to avoid errors while setting the new EEPROM I2C address.")
    
    def read_emissivity(self, pep_check=True):
        try:
            d = self.read16(_REG_EMISSIVITY, crc_check=pep_check)
        except Exception as err:
            raise Exception("Error reading emissivity from EEPROM. {}".format(err))
        if (d >= 32768):
            d = 32768 - d
        return round(100*d/0x4000)

    def set_emissivity(self, value, eeprom_read_check=True, eeprom_write_time=_EEPROM_DEFAULT_TIME_MS):
        if (value >= 5) and (value <= 100):
            e = round((value*0x4000)/100)
            try:
                time.sleep_ms(eeprom_write_time)
                self.write16(_REG_EMISSIVITY, 0x0000, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                time.sleep_ms(eeprom_write_time)
            except Exception as err:
                raise Exception("Error erasing EEPROM emissivity.\n{}".format(err))
            else:
                try:
                    self.write16(_REG_EMISSIVITY, e, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                    time.sleep_ms(eeprom_write_time)
                except Exception as err:
                    raise Exception("Error writing EEPROM emissivity.\n{}".format(err))
        else:
            raise Exception("Error : emissivity value {} out of range (5 <= e <= 100).".format(value))
