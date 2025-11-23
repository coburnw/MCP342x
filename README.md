# MCP342x
Simple class based access to Microchip's MCP342x series
A/D converters in Python

Includes classes for the MCP3425, MCP3426, MCP3427, and MCP3428

# Install
 * ''git clone https://github.com/coburnw/MCP342x''
 * ''pip install smbus2'' # or smbus3
 * ''cd MCP342x''
 * ''pip install -e .''
  
## quick example:

```python
import time
import smbus3 as smbus

import mcp342x

# specify bus and our device address
i2c_bus_number = 1
device_address = 0x68

with smbus.SMBus(i2c_bus_number) as smbus:
    # create an ADC instance of our specific chip
    adc = mcp342x.Mcp3426(smbus, device_address)

    # add an input channel to the device
    channel_number = 0
    chan0 = mcp342x.Channel(adc, channel_number)

    #configure channel for 12bit, continuous mode 
    chan0.sample_rate = 240
    chan0.pga_gain = 1
    chan0.continuous = True

    # update channel configuration and start acquisition
    chan0.start_conversion()
    time.sleep(chan0.conversion_time)
    
    volts = chan0.get_conversion_volts()
    print('Chan{}: Volts={}'.format(chan0.number, volts))
```

## Dependencies
 * Uses smbus2 or smbus3

## Notes
 * Tested with both an MCP3426 and MCP3428, primarily in continuous
 mode, on a raspberry pi zero w.
 * Naming conventions follow the Microchip
 [data sheet](http://ww1.microchip.com/downloads/en/DeviceDoc/22226a.pdf)
 as best as possible.
 * Module does not call time.sleep().  Timing is the responsibility
 of the application.
 * Raises I2CBussError with some help on i2c related OSError.
 * Raises ConversionNotReadyError if the not ready flag is found
 set while reading a conversion.
 
 ## Todo
  * identify differences in the MCP3422 group of devices and add
  overrides for those if possible.
