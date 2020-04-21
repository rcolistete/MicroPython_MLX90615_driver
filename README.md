# MicroPython MLX90615 driver module

[MicroPython](http://micropython.org/) driver for [MLX90615 IR temperature sensor](https://www.melexis.com/en/product/mlx90615/).

### MLX90615
From Melexis product page :

>  The MLX90615 is a miniature infrared thermometer for non-contact temperature measurements.

>  With its small size, this infrared thermometer is especially suited for medical applications like ear or forehead thermometers or other applications where "small things make a big difference".

>  The infrared thermometer comes factory calibrated with a digital SMBus output giving full access to the measured temperature in the complete temperature range(s) with a resolution of 0.02 °C. The sensor achieves an accuracy of ±0.2°C within the relevant medical temperature range. The user can choose to configure the digital output to be PWM.

> Factory calibrated in wide temperature range: -20 to 85°C for sensor temperature and -40 to 115°C for object temperature.

### Driver Functions

| Function | Description |
| -------- | ----------- |
| read_ambient_temp(pep_check=True)   | reads the ambient temperature, returning a integer 100x Celsius degrees, so 2851 = 28.51 C |
| read_object_temp(pep_check=True)   | reads the object temperature, returning a integer 100x Celsius degrees, so 3647 = 36.51 C |
