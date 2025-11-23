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

    # update channel configuration and start acquisition process
    chan0.start_conversion() 
    time.sleep(chan0.conversion_time)
    
    volts = chan0.get_conversion_volts()
    print('Chan{}: Volts={}'.format(chan0.number, volts))
