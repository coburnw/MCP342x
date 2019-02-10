# MCP342x
Simple class based access to the MCP342x series A/D converters in Python

    import time                                                                                           
    import smbus2                                                                                         
    from mcp342x import mcp342x                                                                           

    bus = 1       #i2c buss number
    addr = 0x68   #default address of the chip
    
    # connect to the hardware
    adc = mcp342x.MCP342x(bus, addr)
    
    # get channel object for the first channel and configure it
    ntc_input = mcp342x.MCP3426_Channel(adc, 0)
    ntc_input.sps = 15
    ntc_input.gain = 1
    ntc_input.continuous = True

    # get first channel voltage 
    not_ready, volts = ntc_input.get_volts()
    if not_ready:
        print('device not ready')
    else:
        print('ntc volts: {}'.format(volts))
        
