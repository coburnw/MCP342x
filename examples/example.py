'''
example program for accessing a microchip MCP342x series delta sigma a2d converters.
Note that the MCP342x library makes no effort to syncronize with the sample rate of
the converter.  All timing is the responsibility of the application.
'''

import time
#import smbus2 as smbus
import smbus3 as smbus

import mcp342x

if __name__ == '__main__':

    # get access to a specific device on a bus
    i2c_bus_number = 1
    device_address = 0x68
    with smbus.SMBus(i2c_bus_number) as bus:
        my_adc = mcp342x.Mcp3428(bus, device_address)

        # add an input channel to the device
        channel_number = 1
        first_input = mcp342x.Channel(my_adc, channel_number)
        
        # add a second input channel to the device
        channel_number = 2
        second_input = mcp342x.Channel(my_adc, channel_number)
        
        # the mcp3426 only has two inputs, try adding a third
        #third_channel_number = 2
        #third_input = mcp342x.MCP3426_Channel(my_adc, third_channel_number)
        
        #configure channel for 12bit continuous mode and exercize it
        print('continuous mode')
        first_input.sample_rate = 240
        first_input.pga_gain = 1
        first_input.continuous = True
        first_input.start_conversion() # update device with current channel state and start acquisition
        try:
            print('exercising first channel...')
            for i in range(0, 5):
                time.sleep(first_input.conversion_time)
                volts = first_input.get_conversion_volts()
                print(' Chan{}: Volts={}'.format(first_input.number, volts))

            print('Chan{} is_active = {}'.format(first_input.number, first_input.is_active))
            print('Chan{} is_active = {}'.format(second_input.number, second_input.is_active))

        except mcp342x.ConversionNotReadyError:
            print('conversion not ready.  try waiting a bit longer between samples')

        # configure channel for 16bit one shot mode and exercise it.
        print('single shot mode')
        second_input.sample_rate = 15
        second_input.pga_gain = 8
        second_input.continuous = False
        try:
            for i in range(0, 5):
                second_input.start_conversion()  # start a single acquisition
                time.sleep(1)
                volts = second_input.get_conversion_volts()
                print(' Chan{}: Volts={}'.format(second_input.number, volts))

            print('Chan{} is_active = {}'.format(first_input.number, first_input.is_active))
            print('Chan{} is_active = {}'.format(second_input.number, second_input.is_active))

            print('attempt conversion_time - 10%')
            second_input.start_conversion()  # start a single acquisition
            time.sleep(second_input.conversion_time - second_input.conversion_time*0.1)
            volts = second_input.get_conversion_volts()
            print(' Chan{}: Volts={}'.format(second_input.number, volts))

        except mcp342x.ConversionNotReadyError:
            print('Exception: conversion not ready.  try waiting a bit longer between samples')
