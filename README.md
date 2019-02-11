# MCP342x
Simple class based access to the MCP342x series A/D converters in Python

## quick example:

    import time                                                                                           
    import mcp342x                                                                           

    # get access to a specific device on a bus                                                             
    i2c_bus_number = 1
    device_address = 0x68
    my_adc = mcp342x.Mcp342x(i2c_bus_number, device_address)

    # add an input channel to the device                                                                   
    first_channel_number = 0
    first_input = mcp342x.Mcp3426Channel(my_adc, first_channel_number)

    #configure channel for 12bit continuous mode and exercise it                                           
    print('continuous mode')
    first_input.sps = 240
    first_input.gain = 1
    first_input.continuous = True
    
    first_input.start_conversion() # update device with current channel state and start acquisition        
    time.sleep(first_input.conversion_time)
    volts = first_input.get_volts()
    print('Chan{}: Volts={}'.format(first_input.channel_number, volts))
   
## Notes
 * Uses smbus2
 * Expected to work with the MCP3425, MCP3426, MCP3427, and MCP3428 devices.
 * Tested with an MCP3426, primarily in continuous mode, on a raspberry pi.
 * Naming conventions follow the Microchip [data sheet](http://ww1.microchip.com/downloads/en/DeviceDoc/22226a.pdf) as best as possible.
 * Module does not call time.sleep().  Timing is the responsibility of the application.
 * Raises ConversionNotReadyError if the not ready flag is found set while reading a conversion.
 
 ## Todo
  * look into passing a smbus2 instance rather than a bus number to Mcp342x. 
  * identify differences in the MCP3422 group of devices and add overrides for those if possible.
