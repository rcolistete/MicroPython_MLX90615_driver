# MicroPython (and CircuitPython) MLX90615 driver module

[MicroPython](http://micropython.org/) and [CircuitPython](https://circuitpython.org/) driver for 
[MLX90615 IR temperature sensor](https://www.melexis.com/en/product/mlx90615/), with features :  
- reading all the RAM registers, i. e., ambient/object temperature and raw IR data;
- reading and setting of all configurations in EEPROM registers, including PWM;
- checking the PEC (Packet Error Code, based on CRC-8) for each reading, as default;
- use of I2C (SMBus);
- PWM to I2C function;
- sleep and wake functions.

### 1) MLX90615
From Melexis product page :

>  The MLX90615 is a miniature infrared thermometer for non-contact temperature measurements.

>  With its small size, this infrared thermometer is especially suited for medical applications like ear or forehead thermometers or other applications where "small things make a big difference".

>  The infrared thermometer comes factory calibrated with a digital SMBus output giving full access to the measured temperature in the complete temperature range(s) with a resolution of 0.02 °C. The sensor achieves an accuracy of ±0.2°C within the relevant medical temperature range. The user can choose to configure the digital output to be PWM.

> Factory calibrated in wide temperature range: -20 to 85°C for sensor temperature and -40 to 115°C for object temperature.

, e. g., human skin (0.95 <= e <= 0.98)

### 2) MicroPython driver definitions

These MicroPython driver for MLX90615 is optimised for low memory usage :  
- by using and returning integer values as possible, as float values allocate more RAM;
- documentation is outside the code;

| Constants | Description |
| -------- | ----------- |
| MLX90615_I2C_DEFAULT_ADDR | 0x5B (91 in decimal) is the I2C default (from factory) address writen in EEPROM |
| EEPROM_DEFAULT_TIME_MS | 50 is the time in ms (miliseconds) recommended after erasing/writing EEPROM |

All the functions can return error messagens using exceptions, so it is recommended to call them inside Micro(Python) [try/except](https://docs.python.org/3/tutorial/errors.html).

When the function has 'pec_check' (packet error code check) argument option, it is enabled by default and it checks the reading with a CRC-8, with error message for reading error.

| Function | Description |
| -------- | ----------- |
| MLX90615(i2c, address=0x5B) | class to construct an MLX90615 object. 'i2c' argument is I2C object created previously. 'address' option has default I2C address value 0x5B (91). |
| read_ambient_temp(pec_check=True) | reads the ambient temperature in the range [-40, 85] C, returning a integer 100x the Celsius degree value, so 2851 = 28.51 C. There is also error message for invalid value. |
| read_object_temp(pec_check=True) | reads the object temperature in the range [-40, 115] C, returning a integer 100x the Celsius degrees, so 3647 = 36.47 C. There is also error message for invalid value. |
| read_raw_ir_data(pec_check=True) | reads the raw IR data, returning a 16 bits integer. |
| read_id(pec_check=True) | reads the unique sensor ID, a 32 bits integer stored in EEPROM. |
| read_eeprom(pec_check=True) | reads the EEPROM returning a list of 16 values, each one a 16 bits integer. Very useful to save a backup of the EEPROM, including the factory calibration data. |
| read_emissivity(pec_check=True) | reads the emissivity stored in EEPROM, an integer from 5 to 100 corresponding to emissivity from 0.05 to 1.00. |
| set_emissivity(value, eeprom_read_check=True, eeprom_write_time=50) | sets the emissivity to EEPROM, accepting an integer from 5 to 100 corresponding to emissivity from 0.05 to 1.00. 'eeprom_read_check' option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_write_time' defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. With error messages for out of range of emissivity value and erasing/writing to EEPROM. | 
| read_i2c_addres(pec_check=True) | reads the I2C address stored in EEPROM, a 7 bits integer. |
| set_i2c_addres(addr, eeprom_read_check=False, eeprom_write_time=50) | **(EXPERIMENTAL*)** sets the I2C address stored in EEPROM, a 7 bits integer, in the range of [0x08, 0x77] (8 to 119 in decimal).'eeprom_read_check' option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_write_time' defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. With error messages for using current I2C address <> 0, out of range of EEPROM I2C address value and erasing/writing to EEPROM. |
| read16(register, crc_check=True) | reads any MLX90615 register : EEPROM range is 0x10-0x1F, RAM range is 0x25-0x27 (see the [MLX90615 datasheet, sections 8.3.3 and 8.3.4](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)). The 'crc_check' argument option, enabled by default, checks the reading with a CRC-8, with error message when the CRC-8 doesn't match the PEC (Packet Error Code). | 
| write16(register, data, read_check=True, eeprom_time=50) | writes to any MLX90615 register : EEPROM range is 0x10-0x1F, RAM range is 0x25-0x27 (see the [MLX90615 datasheet, sections 8.3.3 and 8.3.4](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)). The 'read_check' argument option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_time' defines the write time in ms after EEPROM writing, the recommended and default value is 50 ms. With error messages for out of range of emissivity value and erasing/writing to EEPROM. With error message if the reading value after writing doesn't check.

( * ) : **writing to I2C address in EEPROM is risky** because sometimes (3-10%) there is an error while erasing/writing to the EEPROM, rendering the I2C connection to MLX90615 unstable.

### 3) Examples

#### 3.1) Initialization

Beware that MLX90615 I2C bus frequency should be in the range of 10-100 kHz (see the [section '8.4.7 Timing specification' of the MLX90615 datasheet](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)).
I2C frequencies lower than 100 kHz are usually needed for longer cables connecting the microcontroller to the MLX90615 sensor.

If MLX90615 sensor is on a break-out board, it usually has pull-up resistors for I2C SDA and SCL pins. 
But the microcontroller internal pull-up or even external resistors may be needed depending on the lenght of cable connecting to the MLX90615, electromagnetic interference from the environment, etc.

###### 3.1.1) [Pyboard (Lite) v1.x](http://docs.micropython.org/en/latest/pyboard/quickref.html#i2c-bus)
```
import machine
import mlx90615
i2c = machine.I2C(scl='X9', sda='X10', freq=100000)   # Software I2C
i2c.scan()   # returns : [91]  
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.2) [Pyboard D](https://pybd.io/hw/pybd_sfxw.html) and link above
```
import machine
import mlx90615
machine.Pin('EN_3V3').on()
machine.Pin('PULL_SCL', machine.Pin.OUT, value=1)     # 5.6k pull-up, if needed
machine.Pin('PULL_SDA', machine.Pin.OUT, value=1)     # 5.6k pull-up, if needed
i2c = machine.I2C(scl='X9', sda='X10', freq=100000)   # Software I2C
i2c.scan()   # Output : [91]
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.3) [ESP8266](http://docs.micropython.org/en/latest/esp8266/quickref.html#i2c-bus)
```
import machine
import mlx90615
i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5), freq=100000)   # Software I2C
i2c.scan()   # Output : [91]
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.4) [ESP32](http://docs.micropython.org/en/latest/esp32/quickref.html#i2c-bus)
```
import machine
import mlx90615
i2c = machine.I2C(sda=machine.Pin(21), scl=machine.Pin(22), freq=100000)   # Software I2C
i2c.scan()   # Output : [91]
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.5) [Pycom boards like LoPy4](https://docs.pycom.io/firmwareapi/pycom/machine/i2c/)
```
import machine
import mlx90615
i2c = machine.I2C(2, I2C.MASTER, baudrate=100000)   # Software I2C
i2c.scan()   # Output : [91]
irsensor = mlx90615.MLX90615(i2c)
```

#### 3.2) Reading the MLX90615 IR temperature
```
irsensor.read_raw_ir_data()    # Output : 108       # IR raw data with no physical unit
irsensor.read_ambient_temp()   # Output : 3059      # i.e., 30.59 C
irsensor.read_object_temp()    # Output : 3621      # i.e., 36.21 C
```

#### 3.3) Reading the MLX90615 configuration
It is recommended that the ID and EEPROM data of each MLX90615 unit be saved (in a file like spreadsheet, etc) 
as a backup. Because the EEPROM includes the factory calibration data which is different for earch sensor unit, the EEPROM registers can be written by mistake, the EEPROM can become corrupted, etc.
```
irsensor.read_id()            # Output : 7623496   # 32 bits unique ID
irsensor.read_eeprom()        # Output : [13659, 2499, 5321, 15892, 24768, 13658, 17180, 8209, 73, 32786, 7504, 616, 6765, 14908, 21320, 116]
```
Factory default values are emissivity = 1.00 and I2C address = 0x5B (91 in decimal) :
```
irsensor.read_emissivity()    # Output : 100       # e = 1.00
irsensor.read_i2c_address()   # Output : 91 
```

#### 3.4) Setting the MLX90615 configuration
[Emissivity depends on the material type](https://www.optotherm.com/emiss-table.htm), so it should be set to correctly measure the object temperature :
```
irsensor.set_emissivity(97)   # e = 0.97
```
The current I2C address of MLX90615 should be 0x00 to avoid errors while setting the new I2C address in EEPROM :
```
irsensor = mlx90615.MLX90615(i2c, address=0x00)
irsensor.set_i2c_address(0x5C)
irsensor.read_i2c_address()      # Output : 92        # 92 = 0x5C, checked
```

### 4) Benchmarks

| Microcontroller | Import RAM usage (kB) | Import time (ms) | [Simple] Import RAM usage (kB) | [Simple]  Import time (ms) | Time to read object temp (ms) | Time to read object temp without PEC (ms) |   
|:------|:-----:|:-----:|:----:|:----:|:-----:|:----:|
| Pyboard v1.1    | - | - | - |  - | - | - |
| Pyboard Lite    | - | - | - |  - | - | - |
| Pyboard D SF2W  | - | - | - |  - | - | - |
| Pyboard D SF6W  | - | - | - |  - | - | - |
| BBC Micro:bit   | - | - | 2.0 | 400 |  10 | 3.0 |
| ESP8266         | - | - | - |  - | - | - |
| ESP32           | - | - | - |  - | - | - |
| ESP32 PSRAM     | - | - | - |  - | - | - |
| ESP32 PSRAM     | - | - | - |  - | - | - |
| LoPy v1 (Pycom) | - | - | - |  - | - | - |
| LoPy4 (Pycom)   | - | - | - |  - | - | - |
| Sipeed MAix BiT | - | - | - |  - | - | - |
| Adafruit CLUE   | - | - | - |  - | - | - |
| ItsyBitsy M4    | - | - | - |  - | - | - | 

### 5) References

Other MLX90615 drivers :
1. ['Arduino library for MLX90615 module from Seeed-Studio'](https://github.com/Seeed-Studio/Digital_Infrared_Temperature_Sensor_MLX90615) has some features like optional SoftI2cMaster library, PEC/CRC-8 checking and writing to EEPROM registers;
2. ['mlx90615-on-raspberryPi from paulvha'](https://github.com/paulvha/mlx90615-on-raspberryPi) is a C driver and interactive software for Raspberry Pi, with many features and excelent documentation complementing the official MLX96015 documentation, like citation of the time delay needed after erasing/writing to the MLX90615 EEPROM;
3. ['A minimal Arduino library for Melexis MLX90615' from skiselev](https://github.com/skiselev/MLX90615) has only some reading functions;
4. [MLX90615 library functions from Melexis](https://github.com/melexis/mlx90615-library) is a reference C++ driver with many features and good documentation;


