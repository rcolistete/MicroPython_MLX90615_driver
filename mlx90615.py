"""
MicroPython driver for MLX90615 IR temperature I2C sensor :
https://github.com/rcolistete/MicroPython_MLX90615_driver
Version: 0.1.9 @ 2020/04/26
Author: Roberto Colistete Jr. (roberto.colistete at gmail.com)
License: MIT License (https://opensource.org/licenses/MIT)
"""

__version__ = '0.1.9'


import time
import machine


MLX90615_I2C_DEFAULT_ADDR = const(0x5B)
EEPROM_DEFAULT_TIME_MS = const(50)     # erase/write EEPROM time in ms

_REG_SLAVE_I2C_ADDRESS = const(0x10)   # EEPROM register - slave I2C address
_REG_PWM_TMIN = const(0x10)            # EEPROM register - PWM temperature minimum
_REG_PWM_TRANGE = const(0x11)          # EEPROM register - PWM temperature range
_REG_CONFIG = const(0x12)              # EEPROM register - Config
_REG_EMISSIVITY = const(0x13)          # EEPROM register - Emissivity
_REG_ID_LOW = const(0x1E)              # EEPROM register - ID number low
_REG_ID_HIGH = const(0x1F)             # EEPROM register - ID number high
_REG_RAW_IR_DATA = const(0x25)         # RAM register - raw IR data register
_REG_AMBIENT_TEMP = const(0x26)        # RAM register - ambient temperature register
_REG_OBJECT_TEMP  = const(0x27)        # RAM register - object temperature register 
_REG_SLEEP = const(0xC6)               # Sleep command


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

    def write16(self, register, data, read_check=True, eeprom_time=EEPROM_DEFAULT_TIME_MS):
        lsb = data & 0x00FF
        msb = data >> 8        
        crc = self._crc8(0, self.address << 1)
        crc = self._crc8(crc, register)
        crc = self._crc8(crc, lsb)
        crc = self._crc8(crc, msb)
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

    def read_raw_ir_data(self, pec_check=True):
        try:
            d = self.read16(_REG_RAW_IR_DATA, crc_check=pec_check)
        except Exception as err:
            raise Exception("Error reading raw IR data.\n{}".format(err))
        else:
            return d

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

    def read_emissivity(self, pec_check=True):
        try:
            d = self.read16(_REG_EMISSIVITY, crc_check=pec_check)
        except Exception as err:
            raise Exception("Error reading emissivity from EEPROM. {}".format(err))
        if (d >= 32768):
            d = 32768 - d
        return round(100*d/0x4000)

    def set_emissivity(self, value, eeprom_read_check=True, eeprom_write_time=EEPROM_DEFAULT_TIME_MS):
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

    def read_i2c_address(self, pec_check=True):
        try:
            return self.read16(_REG_SLAVE_I2C_ADDRESS, crc_check=pec_check) & 0x007F
        except Exception as err:
            raise Exception("Error reading EEPROM I2C address.\n{}".format(err))

    def set_i2c_address(self, addr, eeprom_read_check=False, eeprom_write_time=EEPROM_DEFAULT_TIME_MS):
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

    def sleep(self):
        crc = self._crc8(0, self.address << 1)
        crc = self._crc8(crc, _REG_SLEEP)
        self.buf[0] = crc
        self.i2c.writeto_mem(self.address, _REG_SLEEP, self.buf)
        self.i2c.stop()

    def wake(self, scl_pin):
        p = machine.Pin(scl_pin, machine.Pin.OUT)
        p.value(0)
        time.sleep_ms(50)
        self.i2c.start()
        time.sleep_ms(500)
        if ((self.address >= 0x08) and (self.address <= 0x77)) and (not (self.address in self.i2c.scan())):
            raise Exception("I2C has not restarted with MLX90615 I2C address {:02x}.".format(self.address))

    def pwm_to_i2c(self, scl_pin):
        p = machine.Pin(scl_pin, machine.Pin.OUT)
        p.value(0)
        time.sleep_ms(100)
        self.i2c.start()
        if ((self.address >= 0x08) and (self.address <= 0x77)) and (not (self.address in self.i2c.scan())):
            raise Exception("I2C has not restarted with MLX90615 I2C address {:02x}.".format(self.address))
            
    def set_pwm_tmin_trange(self, tmin=0x355B, trange=0x09C3, eeprom_read_check=False, eeprom_write_time=EEPROM_DEFAULT_TIME_MS):
        if self.address == 0:
            try:
                time.sleep_ms(eeprom_write_time)
                self.write16(_REG_PWM_TMIN, 0x0000, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                time.sleep_ms(eeprom_write_time)
                self.write16(_REG_PWM_TRANGE, 0x0000, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                time.sleep_ms(eeprom_write_time)
            except Exception as err:
                raise Exception("Error erasing EEPROM PWM TMIN/TRANGE.\n{}".format(err))
            else:
                try:
                    self.write16(_REG_PWM_TMIN, tmin, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                    time.sleep_ms(eeprom_write_time)
                    self.write16(_REG_PWM_TRANGE, trange, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                    time.sleep_ms(eeprom_write_time)
                except Exception as err:
                    raise Exception("Error writing EEPROM PWM TMIN/TRANGE.\n{}".format(err))
        else:
            raise Exception("Current I2C address of MLX90615 should be 0x00 to avoid errors while setting the new EEPROM PWM TMIN/TRANGE.")

    def set_pwm_mode(self, pwm=False, pwm_fast=False, pwm_object=True, eeprom_read_check=True, eeprom_write_time=EEPROM_DEFAULT_TIME_MS):
        try:
            d = self.read16(_REG_CONFIG)
        except Exception as err:
            raise Exception("Error reading config register from EEPROM. {}".format(err))
        else:
            d &= 0xFFF8
            if not pwm:
                d |= 0x0001
            if pwm_fast:
                d |= 0x0002
            if not pwm_object:
                d |= 0x0004               
            try:
                time.sleep_ms(eeprom_write_time)
                self.write16(_REG_CONFIG, 0x0000, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                time.sleep_ms(eeprom_write_time)
            except Exception as err:
                raise Exception("Error erasing EEPROM config register.\n{}".format(err))
            else:
                try:
                    self.write16(_REG_CONFIG, d, read_check=eeprom_read_check, eeprom_time=eeprom_write_time)
                    time.sleep_ms(eeprom_write_time)
                except Exception as err:
                    raise Exception("Error writing EEPROM config register.\n{}".format(err))
