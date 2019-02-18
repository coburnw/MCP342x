''' mc3426 a/d converter'''

import smbus2

# I2C address of the device
DEFAULT_ADDRESS = 0x68
REFERENCE_VOLTAGE = 2.048

# MCP3425/6/7/8 Configuration Command Set
CMD_CONVERSION_MASK = 0x80
CMD_CONVERSION_READY = 0x00 # Conversion Complete: 0=data ready, 1=not_finished.
CMD_CONVERSION_INITIATE = 0x80 # Initiate a new conversion(One-Shot Conversion mode only)

CMD_CHANNEL_MASK = 0x60
CMD_CHANNEL_OFFSET = 5
CMD_CHANNEL_1 = 0x00 # Mux Channel-1
CMD_CHANNEL_2 = 0x20 # Mux Channel-2
CMD_CHANNEL_3 = 0x40 # Mux Channel-3
CMD_CHANNEL_4 = 0x60 # Mux Channel-4

CMD_MODE_MASK = 0x10
CMD_MODE_CONTINUOUS = 0x10 # Continuous Conversion Mode
CMD_MODE_ONESHOT = 0x00 # One-Shot Conversion Mode

CMD_SPS_MASK = 0x0C
CMD_SPS_240 = 0x00 # 240 SPS (12-bit)
CMD_SPS_60 = 0x04 # 60 SPS (14-bit)
CMD_SPS_15 = 0x08 # 15 SPS (16-bit)
CMD_SPS_3_75 = 0x0C # 3.75 SPS (18-bit)

CMD_GAIN_MASK = 0x03
CMD_GAIN_1 = 0x00 # PGA Gain = 1V/V
CMD_GAIN_2 = 0x01 # PGA Gain = 2V/V
CMD_GAIN_4 = 0x02 # PGA Gain = 4V/V
CMD_GAIN_8 = 0x03 # PGA Gain = 8V/V

class ConversionNotReadyError(Exception):
    '''ConversionNotReady exception: devices conversion value is not current.
    Maybe you are requesting data faster than the device can acquire.'''
    pass

class ChannelMixin(object):
    '''access a/d through a channel object'''
    def __init__(self, device, channel_number):
        '''
        channel mixin. non variety specific routines for channel.
        device is an initialized mcp342x instance
        channel_number is the zero referenced mux channel number to access
        '''

        #create out local variables
        super().__setattr__("_device", None)
        super().__setattr__("_config", None)
        super().__setattr__("_channel_number", None)
        super().__setattr__("_pga_gain", None)
        super().__setattr__("_sample_rate", None)
        super().__setattr__("_max_code", None)

        self._config = 0

        self._device = device
        self._channel(channel_number)

        self.pga_gain = 1
        self.sample_rate = 240
        self.continuous = True
        return

    def __setattr__(self, attr, value):
        if not hasattr(self, attr): # would this create a new attribute?
            raise AttributeError(": {} has no attribute {}".format('ChannelMixin', attr))
        super().__setattr__(attr, value)

    @property
    def config(self):
        '''peek into current config settings for this channel.  for help in debug'''
        return self._config

    @property
    def is_active(self):
        '''returns true if the mux is set to this channel'''
        return self._device.active_channel == self._channel_number

    @property
    def channel(self):
        ''' returns the zero referenced mux channel this object controls'''
        return self._channel_number

    def _channel(self, number):
        ''' sets the mux channel for this object.  Override in device specific class'''
        raise NotImplementedError

    @property
    def sample_rate(self):
        ''' returns channel sample rate in samples per second'''
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, rate):
        ''' sets channel sample rate: 240, 60, or 15 sps'''
        self._config &= ~CMD_SPS_MASK
        if rate == 15:
            self._config |= CMD_SPS_15
            self._max_code = 32767
        elif rate == 60:
            self._config |= CMD_SPS_60
            self._max_code = 8191
        elif rate == 240:
            self._config |= CMD_SPS_240
            self._max_code = 2047
        else:
            raise ValueError('Possible sample_rate settings are 15, 60, or 240 samples per second')
        self._sample_rate = rate
        return

    @property
    def pga_gain(self):
        ''' returns pga gain: 1, 2, 4, or 8'''
        return self._pga_gain

    @pga_gain.setter
    def pga_gain(self, gain):
        ''' sets pga gain for this channel: 1, 2, 4, or 8'''
        self._config &= ~CMD_GAIN_MASK
        if gain == 1:
            self._config |= CMD_GAIN_1
        elif gain == 2:
            self._config |= CMD_GAIN_2
        elif gain == 4:
            self._config |= CMD_GAIN_4
        elif gain == 8:
            self._config |= CMD_GAIN_8
        else:
            raise ValueError('Possible pga gain settings are 1, 2, 4, or 8')
        self._pga_gain = gain
        return

    @property
    def max_voltage(self):
        ''' returns the maximum usable input in volts for this channel '''
        return REFERENCE_VOLTAGE / self._pga_gain

    @property
    def lsb_voltage(self):
        ''' returns the resolution in volts for this channel '''
        return self.max_voltage / self._max_code

    @property
    def continuous(self):
        ''' returns true if current channel conversion mode is continuous, false if one-shot'''
        status = False
        if self._config & CMD_MODE_CONTINUOUS:
            status = True
        return status

    @continuous.setter
    def continuous(self, enabled):
        ''' sets channel conversion mode to continuous, false for one-shot'''
        self._config &= ~CMD_MODE_CONTINUOUS
        if enabled is True:
            self._config |= CMD_MODE_CONTINUOUS
        return

    @property
    def conversion_time(self):
        '''
        return estimated time in seconds to complete a single conversion
        assuming its present configuration
        '''
        return 1/self._sample_rate

    def start_conversion(self):
        '''
        Update device config register with our parameters and start conversion.
        If channel configured for continuous mode, conversions continue automatically
        If channel configured for one-shot mode (ie not continuous),
        trigger a single conversion and allow chip to enter low power mode.
        '''
        self._device.initiate_conversion(self._config)
        return True

    def get_conversion_raw(self):
        ''' returns the latest conversion in semi raw two's complement binary'''
        not_ready, raw = self._device.get_conversion(self._sample_rate)
        if not_ready:
            raise ConversionNotReadyError

        return raw

    def get_conversion_volts(self):
        ''' returns the latest conversion in Volts with pga settings applied'''
        raw_value = self.get_conversion_raw()
        volts = raw_value * self.lsb_voltage
        return volts

class Mcp3425Channel(ChannelMixin):
    '''MCP3425 specific channel parameters'''

    def _channel(self, number):
        ''' sets the mux channel for this object.'''
        self._config &= ~CMD_CHANNEL_MASK
        if number == 0:
            self._config |= CMD_CHANNEL_1
        else:
            raise ValueError('Possible MCP3425 channel numbers are 0')
        self._channel_number = number
        return

class Mcp3426Channel(ChannelMixin):
    '''MCP3426 specific channel parameters'''

    def _channel(self, number):
        ''' sets the mux channel for this object.'''
        self._config &= ~CMD_CHANNEL_MASK
        if number == 0:
            self._config |= CMD_CHANNEL_1
        elif number == 1:
            self._config |= CMD_CHANNEL_2
        else:
            raise ValueError('Possible MCP3426 channel numbers are 0 or 1')
        self._channel_number = number
        return

class Mcp3427Channel(ChannelMixin):
    '''MCP3427 specific channel parameters'''

    def _channel(self, number):
        ''' sets the mux channel for this object.'''
        self._config &= ~CMD_CHANNEL_MASK
        if number == 0:
            self._config |= CMD_CHANNEL_1
        elif number == 1:
            self._config |= CMD_CHANNEL_2
        else:
            raise ValueError('Possible MCP3426 channel numbers are 0 or 1')
        self._channel_number = number
        return

class Mcp3428Channel(ChannelMixin):
    '''MCP3428 specific channel parameters'''

    def _channel(self, number):
        ''' sets the mux channel for this object.'''
        self._config &= ~CMD_CHANNEL_MASK
        if number == 0:
            self._config |= CMD_CHANNEL_1
        elif number == 1:
            self._config |= CMD_CHANNEL_2
        elif number == 2:
            self._config |= CMD_CHANNEL_3
        elif number == 3:
            self._config |= CMD_CHANNEL_4
        else:
            raise ValueError('Possible MCP3426 channel numbers are 0, 1, 2, or 3')
        self._channel_number = number
        return

class Mcp342x(object):
    ''' hardware access to the chip'''
    def __init__(self, bus, address=DEFAULT_ADDRESS):
        '''bus is integer id of i2c bus, address is integer address of chip on that bus'''
        self._bus = smbus2.SMBus(bus)
        self._address = address
        self._config_cache = 0
        return

    @property
    def active_channel(self):
        ''' returns the current mux channel setting'''
        return (self._config_cache & CMD_CHANNEL_MASK) >> CMD_CHANNEL_OFFSET

    def initiate_conversion(self, config):
        ''' send conversion initiate command'''
        self._config_cache = config
        self._bus.write_byte(self._address, self._config_cache | CMD_CONVERSION_INITIATE)
        return True

    def get_conversion(self, rate):
        ''' get conversion if ready'''
        raw_adc = 0

        data = self._bus.read_i2c_block_data(self._address, self._config_cache, 3)
        status = data[2]
        if (status & CMD_CONVERSION_MASK) == CMD_CONVERSION_READY:
            not_ready = False
            #print('status={:0b}, data0={:0x}, data1={:0x}'.format(status, data[0], data[1]))
            if rate == 240:
                raw_adc = ((data[0] & 0x0F) * 256) + data[1]
                if raw_adc > 2047:
                    raw_adc -= 4096
            elif rate == 60:
                raw_adc = ((data[0] & 0x3F) * 256) + data[1]
                if raw_adc > 8191:
                    raw_adc -= 16384
            elif rate == 15:
                raw_adc = (data[0] * 256) + data[1]
                if raw_adc > 32767:
                    raw_adc -= 65536
            else:
                pass
        else:
            not_ready = True

        return not_ready, raw_adc
