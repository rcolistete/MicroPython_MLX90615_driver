# MicroPython (and CircuitPython) driver module for MLX90615 infrared temperature sensor

[MicroPython](http://micropython.org/) and [CircuitPython](https://circuitpython.org/) drivers for 
[MLX90615 infrared temperature sensor](https://www.melexis.com/en/product/mlx90615/), with features :  
- reading all the RAM registers, i. e., ambient/object temperature and raw IR data;
- reading and setting of all configurations in EEPROM;
- checking the PEC (Packet Error Code, based on CRC-8) for each reading, as default;
- use of I2C (SMBus);
- enable/disable and configuration of PWM mode;
- sleep and wake functions;
- optional simplified versions with low memory usage.

These drivers for MLX90615 are optimised for low memory usage :  
- by using and returning integer values as possible, as float values would allocate more RAM;
- documentation is outside the code;
- the 'no-errors' version has no error checking for reading the sensor, nor error messages;
- the 'simple' version has just the most important functions.

### 1) MLX90615

The [Melexis MLX90615 infrared thermometer](https://www.melexis.com/en/product/mlx90615/) :  
- is a miniature infrared thermometer for non-contact temperature measurements;
- has small size and good accuracy, so it is especially suited for medical applications like ear or forehead thermometers;
- has I2C (SMBus) and PWM communication options;
- features PEC (Packet Error Code, based on CRC-8) for each data/EEPROM reading;
- usually consumes 1.5 mA in active mode using I2C, or 3 uA in low power/sleep mode;
- comes factory calibrated in wide temperature range, -20 to 85°C for ambient/sensor temperature and -40 to 115°C for object temperature, with a resolution of 0.02 °C;
- has factory calibrated accuracy of ±0.2°C for object temperature range 36-39°C and ±0.3°C for object temperature range 32-42°C, when ambient/sensor temperature is between 16-40°C;
- updates the temperature and raw IR data in RAM at a 2 Hz rate (0.5 s period);
- recommended object distance is <= 3 cm, like 2 cm, but not touching the sensor.

Boards with MLX90615 :  
- [SeeedStudio Grove MLX90615 Digital Infrared Temperature Sensor - US$9.00](https://www.seeedstudio.com/Grove-Digital-Infrared-Temperature-Sensor.html);
<img src="https://files.seeedstudio.com/wiki/Grove-Digital_Infrared_Temperature_Sensor/img/Grove%EF%BC%8DDigital_Infrared_Temperature_Sensor_2.jpg" alt="SeeedStudio Grove MLX90615 Digital Infrared Temperature Sensor" width="400"/>
- [GY-90615 Digital Infrared Temperature Sensor Module MLX90615 - Alibaba.com - US$7.80](https://www.alibaba.com/product-detail/GY-90615-Digital-Infrared-Temperature-Sensor_62403370264.html).
<img src="https://sc01.alicdn.com/kf/Hbc672028c02041b48e41a7a8983e9ba6m.jpg" alt="GY-90615" width="250"/>

### 2) MicroPython/CircuitPython driver definitions

The 'no-errors' version of the driver doesn't check the PEC (Packet Error Code, based on CRC-8) on each reading, doesn't read the value after writing to EEPROM to confirm, nor have specific error messages. Advantages : lower RAM usage, faster to import and a little bit to run the functions. Disadvantages : less robust, more difficult to debug errors.

The 'simple' version of the driver has just the most important functions : read ambient and object temperatures, read unique ID, read EEPROM and read of any register. Advantages : robust, lower RAM usage. Disadvantages : not possible to change MLX90615 configuration, less features.

The BBC Micro:bit version, even not the 'simple' one, is limited to fewer functions due to RAM limitations, so there are no sleep/wake, PWM and IIR filter functions.

The full version of the driver is described in the tables below.

| Constants | Description |
| -------- | ----------- |
| MLX90615_I2C_DEFAULT_ADDR | 0x5B (91 in decimal) is the I2C default (from factory) address writen in EEPROM |
| EEPROM_DEFAULT_TIME_MS | 50 is the time in ms (miliseconds) recommended after erasing/writing EEPROM |

All the functions can return error messagens using exceptions, so it is recommended to call them inside Micro(Python) [try/except](https://docs.python.org/3/tutorial/errors.html).

When the function has the argument option :  
- 'pec_check' (packet error code check), it is enabled by default and it checks the reading with a CRC-8, with error message for reading error;
- 'eeprom_read_check', if True it reads the value after writing to EEPROM to confirm;
- 'eeprom_write_time', it defines the erase/write time in ms before and after EEPROM operations, the recommended and default value is 50 ms. 

| Function | Description |
| -------- | ----------- |
| MLX90615(i2c, address=0x5B) | class to construct an MLX90615 object. 'i2c' argument is I2C object created previously. 'address' option has default I2C address value 0x5B (91). |
| read_ambient_temp(pec_check=True) | reads the ambient temperature in the range [-40, 85] C, returning a integer 100x the Celsius degree value, so 2851 = 28.51 C. There is also error message for invalid value. |
| read_object_temp(pec_check=True) | reads the object temperature in the range [-40, 115] C, returning a integer 100x the Celsius degrees, so 3647 = 36.47 C. There is also error message for invalid value. |
| read_raw_ir_data(pec_check=True) | reads the raw IR data, returning a 16 bits integer. |
| read_id(pec_check=True) | reads the unique sensor ID, a 32 bits integer stored in EEPROM. |
| read_eeprom(pec_check=True) | reads the EEPROM returning a list of 16 values, each one a 16 bits integer. Very useful to save a backup of the EEPROM, including the factory calibration data. See the [MLX90615 datasheet, section 8.3.3 and table 6](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615).|
| read_emissivity(pec_check=True) | reads the emissivity stored in EEPROM, an integer from 5 to 100 corresponding to emissivity from 0.05 to 1.00. |
| set_emissivity(value=100, eeprom_read_check=True, eeprom_write_time=50) | sets the emissivity to EEPROM, accepting an integer from 5 to 100 (default is 100) corresponding to emissivity from 0.05 to 1.00. With error messages for out of range of emissivity value and erasing/writing to EEPROM. | 
| read_i2c_addres(pec_check=True) | reads the I2C address stored in EEPROM, a 7 bits integer. |
| set_i2c_address(addr=0x5B, eeprom_read_check=False, eeprom_write_time=50) | sets 'addr' (default is 0x5B = 91) as the I2C address stored in EEPROM, a 7 bits integer, in the range of [0x08, 0x77] (8 to 119 in decimal). With error messages for using current I2C address <> 0, out of range of EEPROM I2C address value and erasing/writing to EEPROM. |
| read_iir_filter(pec_check=True) | reads the bits 12, 13 and 14 of EEPROM config register, returning a number from 1 to 7 (default is 1) corresponding to configurations of IIR (Infinite Impulse Response) digital filter. The IIR filter allows customization of the thermometer output in order to trade-off noise versus settling time, but the refresh rate of 2 Hz (0.5 s) of the data in the RAM remain constant. See the [MLX90615 datasheet, section 8.2 and table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| set_iir_filter(iir=1, eeprom_read_check=True, eeprom_write_time=50) | sets 'iir' value (1 to 7, default is 1) in bits 12, 13 and 14 of EEPROM config register corresponding to configurations of IIR (Infinite Impulse Response) digital filter. The IIR filter allows customization of the thermometer output in order to trade-off noise versus settling time, but the refresh rate of 2 Hz (0.5 s) of the data in the RAM remain constant. With error messages for erasing/writing to EEPROM. See the [MLX90615 datasheet, section 8.2 and table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| sleep() | enable the MLX90615 low power/sleep mode, disabling the sensor functions and saving approx. 1.5 mA. The I2C bus should not be used during the sleep mode. See the [MLX90615 datasheet, section 8.4.8](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| wake(scl_pin) | disable the MLX90615 low power/sleep mode, powering-up with default mode as defined by the EEPROM. 'scl_pin' is the definition of the I2C SCL pin. See the [MLX90615 datasheet, section 8.4.8](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| pwm_to_i2c(scl_pin) | switch to I2C mode if PWM is enabled. 'scl_pin' is the definition of the I2C SCL pin. But after power off/on the I2C or PWM mode will be chosen depending on the bit 0 of EEPROM config register. See the [MLX90615 datasheet, section 8.5.1](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| read_pwm_mode(pec_check=True) | reads the bit 0 of EEPROM config register, returning True if PWM mode is enabled, False if I2C mode is enabled (default). See the [MLX90615 datasheet, table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| set_pwm_mode(pwm=False, eeprom_read_check=True, eeprom_write_time=50) | sets 'pwm' (default is False) as communication mode  stored in bit 0 of EEPROM config register, True for PWM mode enabled, False for I2C mode enabled (default). With error messages for erasing/writing to EEPROM. This setting is used after power on. See the [MLX90615 datasheet, table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| read_pwm_fast(pec_check=True) | reads the bit 1 of EEPROM config register, returning True if PWM fast frequency (10 kHz)  is enabled, False if PWM slow frequency (1 kHz) is enabled (default). See the [MLX90615 datasheet, table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| set_pwm_fast(pwm_fast=False, eeprom_read_check=True, eeprom_write_time=50) | sets 'pwm_fast' (default is False) in bit 1 of EEPROM config register, True for PWM fast frequency (10 kHz) stored, False for PWM slow frequency (1 kHz). With error messages for erasing/writing to EEPROM. This setting is used after power on in PWM mode. See the [MLX90615 datasheet, table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| read_pwm_object_temp(pec_check=True) | reads the bit 2 of EEPROM config register, returning True if PWM output is for object temperature (default), False if it is for ambient temperature. See the [MLX90615 datasheet, table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| set_pwm_object_temp(object_temp=True, eeprom_read_check=True, eeprom_write_time=50) | sets 'object_temp' (default is True) in bit 2 of EEPROM config register, True for PWM output of object temperature, False for PWM output of ambient temperature. With error messages for erasing/writing to EEPROM. This setting is used after power on in PWM mode. See the [MLX90615 datasheet, table 7](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| read_pwm_tmin(pec_check=True) | reads the minimum temperature when PWM is used, the output scale is 0.02 K/LSB, so to convert to degrees Celsius the equation is: Tmin(C) = output × 0.02 − 273.15. Factory default is 0x355B corresponding to +0.03°C. See the [MLX90615 datasheet, sections 8.3.3, 8.3.4 and 8.6](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| set_pwm_tmin(tmin=0x355B, eeprom_read_check=True, eeprom_write_time=50) | sets 'tmin' (default is 0x355B corresponding to +0.03°C) as the minimum temperature when PWM is used. The scale is 0.02 K/LSB, so to convert to degrees Celsius the equation is: Tmin(C) = tmin × 0.02 − 273.15. With error messages for erasing/writing to EEPROM. This setting is used after power on in PWM mode. Beware that the 7 less significant bits of 'tmin' composes the I2C address stored in EEPROM. See the [MLX90615 datasheet, sections 8.3.3, 8.3.4 and 8.6](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| read_pwm_trange(pec_check=True) | reads the range for the temperature (Trange = Tmax – Tmin) when PWM is used, the output scale is 0.02 K/LSB, so to convert to degrees Celsius the equation is: Trange(C) = output × 0.02 − 273.15. Factory default is 0x09C4 corresponding to +49.98°C. See the [MLX90615 datasheet, sections 8.3.3, 8.3.4 and 8.6](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| set_pwm_trange(trange=0x09C3, eeprom_read_check=True, eeprom_write_time=50) | sets 'trange' (default is 0x09C3 corresponding to +49.98°C) as the range for the temperature (Trange = Tmax – Tmin) when PWM is used. The scale is 0.02 K/LSB, so to convert to degrees Celsius the equation is: Trange(C) = trange × 0.02 − 273.15. With error messages for erasing/writing to EEPROM. This setting is used after power on in PWM mode. See the [MLX90615 datasheet, sections 8.3.3, 8.3.4 and 8.6](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615). |
| read16(register, crc_check=True) | reads any MLX90615 register : EEPROM range is 0x10-0x1F, RAM range is 0x25-0x27 (see the [MLX90615 datasheet, sections 8.3.3 and 8.3.4](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)). The 'crc_check' argument option, enabled by default, checks the reading with a CRC-8, with error message when the CRC-8 doesn't match the PEC (Packet Error Code). | 
| write16(register, data, read_check=True, eeprom_time=50) | writes 'data' (16 bit integer number) to any MLX90615 register : EEPROM range is 0x10-0x1F, RAM range is 0x25-0x27 (see the [MLX90615 datasheet, sections 8.3.3 and 8.3.4](https://www.melexis.com/en/documents/documentation/datasheets/datasheet-mlx90615)). The 'read_check' argument option, enabled by default, reads the value after writing to EEPROM to confirm. 'eeprom_time' defines the write time in ms after EEPROM writing, the recommended and default value is 50 ms. With error messages for out of range of emissivity value and erasing/writing to EEPROM. With error message if the reading value after writing doesn't check. | 

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

###### 3.1.5) [BBC Micro:bit](https://microbit-micropython.readthedocs.io/en/latest/i2c.html)
```
from microbit import i2c
import mlx90615
i2c.scan()   # Output : [91]
irsensor = mlx90615.MLX90615(i2c)
```

###### 3.1.6) [Pycom boards like LoPy4](https://docs.pycom.io/firmwareapi/pycom/machine/i2c/)
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

Table for driver 'mlx90615.py' v0.2.1 with all features. '[simple]' means driver 'mlx90615_simple.py'/'mlx90615_microbit_simple.py' v0.2.1 with simple read functions :

| Microcontroller | Import RAM usage (kB) | Import time (ms) | [Simple] Import RAM usage (kB) | [Simple] Import time (ms) | Time to read object temp. (ms) | Time to read object temp. without PEC (ms) |   
|:------|:-----:|:-----:|:----:|:----:|:-----:|:----:|
| Pyboard v1.1    | - | - | - |  - | - | - |
| Pyboard Lite    | - | - | - |  - | - | - |
| Pyboard D SF2W  | 10.34 | 161.6 | 2.31 | 34.6 | 1.22 | 0.916 |
| Pyboard D SF6W  | - | - | - |  - | - | - |
| ESP8266         | - | - | - |  - | - | - |
| ESP32           | - | - | - |  - | - | - |
| ESP32 PSRAM     | - | - | - |  - | - | - |
| BBC Micro:bit   | - | - | 2.55 | 505.5 |  10.46 | 4.51 |
| LoPy v1         | - | - | - |  - | - | - |
| LoPy4           | - | - | - |  - | - | - |
| OpenMV M7       | - | - | - |  - | - | - |
| OpenMV H7       | - | - | - |  - | - | - |
| Sipeed MAix BiT | - | - | - |  - | - | - |
| ItsyBitsy M0    | - | - | - |  - | - | - | 
| ItsyBitsy M4    | - | - | - |  - | - | - | 
| Adafruit CLUE   | - | - | - |  - | - | - |

Table for driver 'mlx90615_microbit_no-errors.py' v0.2.1 without error checking. '[simple]' means driver 'mlx90615_simple_no-errors.py'/'mlx90615_microbit_simple_no-errors.py' v0.2.1 with simple read functions and without error checking :

| Microcontroller | Import RAM usage (kB) | Import time (ms) | [Simple] Import RAM usage (kB) | [Simple] Import time (ms) |  Time to read object temp. without PEC (ms) |   
|:------|:-----:|:-----:|:----:|:----:|:-----:|
| ESP8266         | - | - | - |  - | - |
| BBC Micro:bit   | 2.67 | 602 | 1.50 | 240 | 3.3 |
| ItsyBitsy M0    | - | - | - |  - | - | 

When not stated, using MicroPython v1.12 and default clock speed for the MicroPython/CircuitPython board.

### 5) References

MLX90615 documentation :
1. [official Melexis MLX90615 web page](https://www.melexis.com/en/product/mlx90615/), with datasheet, application notes, etc;
2. [Melexis Comparative Table of InfraRed Thermometer Family - MLX90614 and MLX90615](https://www.melexis.com/-/media/files/documents/product-flyers/quick-reference-infrared-temperature-sensors.pdf);
3. [Comparative table between the MLX90614 and the MLX90615](http://dtsheet.com/doc/1776025/comparative-table-between-the-mlx90614-and-the-mlx90615-d...).

MLX90615 tutorials :  
- [Grove - MLX90615 Digital Infrared Temperature Sensor - SeedStudio Wiki](https://wiki.seeedstudio.com/Grove-Digital_Infrared_Temperature_Sensor/), for Arduino;
- [MLX90615 infrared thermometer and Arduino - Arduino Learning](http://arduinolearning.com/code/mlx90615-infrared-thermometer-and-arduino.php).

Other MLX90615 drivers :
1. ['Arduino library for MLX90615 module from Seeed-Studio'](https://github.com/Seeed-Studio/Digital_Infrared_Temperature_Sensor_MLX90615) has some features like optional SoftI2cMaster library, PEC/CRC-8 checking and writing to EEPROM registers;
2. ['mlx90615-on-raspberryPi from paulvha'](https://github.com/paulvha/mlx90615-on-raspberryPi) is a C driver and interactive software for Raspberry Pi, with many features and excelent documentation complementing the official MLX96015 documentation, like citation of the time delay needed after erasing/writing to the MLX90615 EEPROM;
3. ['A minimal Arduino library for Melexis MLX90615' from skiselev](https://github.com/skiselev/MLX90615) has only some reading functions;
4. [MLX90615 library functions from Melexis](https://github.com/melexis/mlx90615-library) is a reference C++ driver with many features and good documentation.
