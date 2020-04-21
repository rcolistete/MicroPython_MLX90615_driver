# MicroPython MLX90615 driver module

[MicroPython](http://micropython.org/) driver for [MLX90615 IR temperature sensor](https://www.melexis.com/en/product/mlx90615/).

### MLX90615
From Melexis product page :

>  The MLX90615 is a miniature infrared thermometer for non-contact temperature measurements.

>  With its small size, this infrared thermometer is especially suited for medical applications like ear or forehead thermometers or other applications where "small things make a big difference".

>  The infrared thermometer comes factory calibrated with a digital SMBus output giving full access to the measured temperature in the complete temperature range(s) with a resolution of 0.02 °C. The sensor achieves an accuracy of ±0.2°C within the relevant medical temperature range. The user can choose to configure the digital output to be PWM.

> Factory calibrated in wide temperature range: -20 to 85°C for sensor temperature and -40 to 115°C for object temperature.

### Driver Functions

All the functions can return error messagens using exceptions, so it is recommended to call them inside Python/MicroPython [try/except](https://docs.python.org/3/tutorial/errors.html).

When the function has 'pec_check' (packet error code check) option, it is enabled by default and it checks the reading with a CRC-8, with error message for reading error.

| Function | Description |
| -------- | ----------- |
| read_ambient_temp(pec_check=True) | reads the ambient temperature in the range [-40, 85] C, returning a integer 100x the Celsius degree value, so 2851 = 28.51 C. There is also error message for invalid value. |
| read_object_temp(pec_check=True) | reads the object temperature in the range [-40, 115]C, returning a integer 100x the Celsius degrees, so 3647 = 36.47 C. There is also error message for invalid value. |
| read_raw_ir_data(pec_check=True) | reads the raw IR data, returning a 16 bits integer. |
| read_id(pec_check=True) | reads the unique sensor ID, a 32 bits integer stored in EEPROM. |
| read_eeprom(pec_check=True) | reads the EEPROM returning a list of 16 values, each one a 16 bits integer. |
| read_emissivity(pec_check=True) | reads the emissivity stored in EEPROM, an integer from 0 to 100 corresponding to 0.0 to 1.0. |
| set_emissivity(value, eeprom_read_check=True, eeprom_write_time=_EEPROM_DEFAULT_TIME_MS) | sets the emissivity to EEPROM, an integer from 5 to 100 corresponding to 0.05 to 1.00. 'eeprom_read_check' option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_write_time' defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. With error messages for out of range of emissivity value and erasing/writing to EEPROM. | 
| read_i2c_addres(pec_check=True) | reads the I2C address stored in EEPROM, a 7 bits integer. |
| set_i2c_addres(addr, eeprom_read_check=False, eeprom_write_time=EEPROM_DEFAULT_TIME_MS) | sets the I2C address stored in EEPROM, a 7 bits integer, in the range of [0x08, 0x77] (8 to 119 in decimal).'eeprom_read_check' option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_write_time' defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. With error messages for using current I2C address <> 0, out of range of EEPROM I2C address value and erasing/writing to EEPROM. |

### Examples

### Benchmarks

### References

Other MLX90615 drivers :


