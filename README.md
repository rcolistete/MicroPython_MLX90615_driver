# MicroPython MLX90615 driver module

[MicroPython](http://micropython.org/) driver for [MLX90615 IR temperature sensor](https://www.melexis.com/en/product/mlx90615/).

### 1) MLX90615
From Melexis product page :

>  The MLX90615 is a miniature infrared thermometer for non-contact temperature measurements.

>  With its small size, this infrared thermometer is especially suited for medical applications like ear or forehead thermometers or other applications where "small things make a big difference".

>  The infrared thermometer comes factory calibrated with a digital SMBus output giving full access to the measured temperature in the complete temperature range(s) with a resolution of 0.02 °C. The sensor achieves an accuracy of ±0.2°C within the relevant medical temperature range. The user can choose to configure the digital output to be PWM.

> Factory calibrated in wide temperature range: -20 to 85°C for sensor temperature and -40 to 115°C for object temperature.

, e. g., human skin (0.95 <= e <= 0.98)

### 2) Driver Functions

All the functions can return error messagens using exceptions, so it is recommended to call them inside Micro(Python) [try/except](https://docs.python.org/3/tutorial/errors.html).

When the function has 'pec_check' (packet error code check) argument option, it is enabled by default and it checks the reading with a CRC-8, with error message for reading error.

| Function | Description |
| -------- | ----------- |
| read_ambient_temp(pec_check=True) | reads the ambient temperature in the range [-40, 85] C, returning a integer 100x the Celsius degree value, so 2851 = 28.51 C. There is also error message for invalid value. |
| read_object_temp(pec_check=True) | reads the object temperature in the range [-40, 115] C, returning a integer 100x the Celsius degrees, so 3647 = 36.47 C. There is also error message for invalid value. |
| read_raw_ir_data(pec_check=True) | reads the raw IR data, returning a 16 bits integer. |
| read_id(pec_check=True) | reads the unique sensor ID, a 32 bits integer stored in EEPROM. |
| read_eeprom(pec_check=True) | reads the EEPROM returning a list of 16 values, each one a 16 bits integer. Very useful to save a backup of the EEPROM, including the factory calibration data. |
| read_emissivity(pec_check=True) | reads the emissivity stored in EEPROM, an integer from 5 to 100 corresponding to emissivity from 0.05 to 1.00. |
| set_emissivity(value, eeprom_read_check=True, eeprom_write_time=EEPROM_DEFAULT_TIME_MS) | sets the emissivity to EEPROM, accepting an integer from 5 to 100 corresponding to emissivity from 0.05 to 1.00. 'eeprom_read_check' option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_write_time' defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. With error messages for out of range of emissivity value and erasing/writing to EEPROM. | 
| read_i2c_addres(pec_check=True) | reads the I2C address stored in EEPROM, a 7 bits integer. |
| set_i2c_addres(addr, eeprom_read_check=False, eeprom_write_time=EEPROM_DEFAULT_TIME_MS) | **(EXPERIMENTAL*)** sets the I2C address stored in EEPROM, a 7 bits integer, in the range of [0x08, 0x77] (8 to 119 in decimal).'eeprom_read_check' option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_write_time' defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. With error messages for using current I2C address <> 0, out of range of EEPROM I2C address value and erasing/writing to EEPROM. |
| read16(register, crc_check=True) | reads any MLX90615 register : EEPROM range is 0x10-0x1F, RAM range is 0x25-0x27 (see the [MLX90615 datasheet, sections 8.3.3 and 8.3.4](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)). The 'crc_check' argument option, enabled by default, checks the reading with a CRC-8, with error message when the CRC-8 doesn't match the PEC (Packet Error Code). | 
| write16(register, data, read_check=True, eeprom_time=EEPROM_DEFAULT_TIME_MS) | writes to any MLX90615 register : EEPROM range is 0x10-0x1F, RAM range is 0x25-0x27 (see the [MLX90615 datasheet, sections 8.3.3 and 8.3.4](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)). The 'read_check' argument option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_time' defines the write time in ms after EEPROM writing, the recommended and default value is 50 ms. With error messages for out of range of emissivity value and erasing/writing to EEPROM. With error message if the reading value after writing doesn't check.

( * ) : **writing to I2C address in EEPROM is risky** because sometimes (3-10%) there is an error while erasing/writing to the EEPROM, rendering the I2C connection to MLX90615 unstable.

### 3) Examples

#### 3.1) Initialization

Beware that MLX90615 I2C bus frequency should be in the range of 10-100 kHz (see the [section '8.4.7 Timing specification' of the MLX90615 datasheet](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)).
I2C frequencies lower than 100 kHz are usually needed for longer cables connecting the microcontroller to the MLX90615 sensor.

If MLX90615 sensor is in a break-out board, it usually has pull-up resistors for I2C SDA and SCL pins. 
But the microcontroller internal pull-up or external resistors may be needed depending on the lenght of cable connecting to the MLX90615, electromagnetic interference from the environment, etc.

###### 3.1.1) Pyboard v1.1
```
from machine import Pin
import machine
i2c = machine.I2C(scl='X9', sda='X10', freq=100000)   # Software I2C
i2c.scan()   # returns : [91]  
import mlx90615
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.2) Pyboard D
```
from machine import Pin
import machine
machine.Pin('EN_3V3').on()
Pin('PULL_SCL', Pin.OUT, value=1)     # 5.6k pull-up, if needed
Pin('PULL_SDA', Pin.OUT, value=1)     # 5.6k pull-up, if needed
i2c = machine.I2C(scl='X9', sda='X10', freq=100000)   # Software I2C
i2c.scan()   # Output : [91]
import mlx90615
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.3) ESP8266
```
from machine import Pin
import machine
i2c = machine.I2C(sda=Pin(4), scl=Pin(5), freq=100000)   # Software I2C
i2c.scan()   # Output : [91]
import mlx90615
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.4) ESP32
```
from machine import Pin
import machine
i2c = machine.I2C(sda=Pin(21), scl=Pin(22), freq=100000)   # Software I2C
i2c.scan()   # Output : [91]
import mlx90615
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.5) Pycom boards like LoPy4
```
import machine
i2c = machine.I2C(2, I2C.MASTER, baudrate=100000)   # Software I2C
i2c.scan()   # Output : [91]
import mlx90615
irsensor = mlx90615.MLX90615(i2c)
```

#### 3.2) Reading the MLX90615 IR temperature
```
irsensor.read_raw_ir_data()    # Output : 108       # IR raw data with no physical unit
irsensor.read_ambient_temp()   # Output : 3059      # i.e., 30.59 C
irsensor.read_object_temp()    # Output : 3621      # i.e., 36.21 C
```

#### 3.3) Reading the MLX90615 configuration
```
irsensor.read_id()            # Output : 7623496   # 32 bits unique ID
irsensor.read_eeprom()        # Output : [13659, 2499, 5321, 15892, 24768, 13658, 17180, 8209, 73, 32786, 7504, 616, 6765, 14908, 21320, 116]
irsensor.read_emissivity()    # Output : 100       # e = 1.00, default value
irsensor.read_i2c_address()   # Output : 91        # 91 = 0x5B, default I2C address value    
```

#### 3.4) Setting the MLX90615 configuration
Emissivity should be set depending on the material type
```
irsensor.set_emissivity(97)   # e = 0.97
```
The current I2C address of MLX90615 should be 0x00 to avoid errors while setting the new EEPROM I2C address :
```
irsensor = mlx90615.MLX90615(i2c, address=0x00)
irsensor.set_i2c_address(0x5C)
irsensor.read_i2c_address()      # Output : 92        # 92 = 0x5C, checked
```

### 4) Benchmarks

### 5) References

Other MLX90615 drivers :



