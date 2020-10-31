# MCP342x
Simple class based access to the MCP342x series A/D converters in Python

Includes classes for the MCP3425, MCP3426, MCP3427, and MCP3428

## quick example:

    import time                                                                                           
    import mcp342x                                                                           

    # get access to a specific device on a bus                                                             
    i2c_bus_number = 1
    device_address = 0x68
    my_adc = mcp342x.Mcp3426(i2c_bus_number, device_address)

    # add an input channel to the device                                                                   
    channel_number = 0
    first_input = mcp342x.Channel(my_adc, channel_number)

    #configure channel for 12bit continuous mode and exercise it                                           
    print('continuous mode')
    first_input.sample_rate = 240
    first_input.pga_gain = 1
    first_input.continuous = True
    
    first_input.start_conversion() # update device with current channel state and start acquisition        
    time.sleep(first_input.conversion_time)
    volts = first_input.get_conversion_volts()
    print('Chan{}: Volts={}'.format(first_input.number, volts))

## Dependencies
 * Uses smbus2

## Notes
 * Tested with both an MCP3426 and MCP3428, primarily in continuous mode, on a raspberry pi zero w.
 * Naming conventions follow the Microchip [data sheet](http://ww1.microchip.com/downloads/en/DeviceDoc/22226a.pdf) as best as possible.
 * Module does not call time.sleep().  Timing is the responsibility of the application.
 * Raises I2CBussError with some help on i2c related OSError.
 * Raises ConversionNotReadyError if the not ready flag is found set while reading a conversion.
 
 ## Todo
  * look into passing a smbus2 instance rather than a bus number to Mcp342x. 
  * identify differences in the MCP3422 group of devices and add overrides for those if possible.
