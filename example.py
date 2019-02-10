'''
example program for accessing a microchip MCP342x series delta sigma a2d converters.
Note that the MCP342x library makes no effort to syncronize with the sample rate of
the converter.  All timing is the responsibility of the application.
'''

import time
import mcp342x

if __name__ == '__main__':

    # get access to a specific device on a bus
    i2c_bus_number = 1
    device_address = 0x68
    my_adc = mcp342x.Mcp342x(i2c_bus_number, device_address)

    # add an input channel to the device
    first_channel_number = 0
    first_input = mcp342x.Mcp3426Channel(my_adc, first_channel_number)

    # add a second input channel to the device
    second_channel_number = 1
    second_input = mcp342x.Mcp3426Channel(my_adc, second_channel_number)

    # the mcp3426 only has two inputs, try adding a third
    #third_channel_number = 2
    #third_input = mcp342x.MCP3426_Channel(my_adc, third_channel_number)

    #configure channel for 12bit continuous mode and exercize it
    print('continuous mode')
    first_input.sps = 240
    first_input.gain = 1
    first_input.continuous = True
    first_input.start_conversion() # update device with current channel state and start acquisition
    try:
        for i in range(0, 5):
            time.sleep(first_input.conversion_time)
            volts = first_input.get_volts()
            print('Chan{}: Volts={}'.format(first_input.channel_number, volts))

    except mcp342x.ConversionNotReady:
        print('conversion not ready.  try waiting a bit longer between samples')

    # configure channel for 16bit one shot mode and exercise it.
    print('single shot mode')
    first_input.sps = 15
    first_input.gain = 1
    first_input.continuous = False
    try:
        for i in range(0, 5):
            first_input.start_conversion()  # start a single acquisition
            time.sleep(1)
            volts = first_input.get_volts()
            print('Chan{}: Volts={}'.format(first_input.channel_number, volts))

    except mcp342x.ConversionNotReady:
        print('conversion not ready.  try waiting a bit longer between samples')
