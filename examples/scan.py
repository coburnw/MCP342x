import time
import cmd
import subprocess

import smbus3 as smbus
import mcp342x

# specify bus and our device address
i2c_bus_number = 1
device_address = 0x68

addr_list = [0x68, 0x69, 0x6a, 0x6b, 0x6c]

class Shell(cmd.Cmd):
    intro = 'phorp scanner'
    prompt = 'scan: '

    def __init__(self, smbus, *kwargs):
        super().__init__(*kwargs)
        self.smbus = smbus

        self.board_index = 0
        self.channels = None

        self.config_board(0)

        return

    def config_board(self, index):
        self.channels = []
        adc = mcp342x.Mcp3428(self.smbus, addr_list[index])
        
        for i in range(1, 5):
            # add an input channel to the device
            chan = mcp342x.Channel(adc, 4-i)
            
            #configure channel for 14bit, continuous mode 
            chan.sample_rate = 60
            chan.pga_gain = 1
            chan.continuous = False
            self.channels.append(chan)

        return
    
    def emptyline(self):
        self.do_chan(None)

        return False
    
    def do_reset(self, arg):
        ''' reset to first board in chain '''
        self.board_index = 0
        self.config_board(self.board_index)

        return False
        
    def do_next(self, arg):
        ''' advance to the next board '''
        self.board_index += 1
        
        try:
            self.config_board(self.board_index)
        except IndexError:
            print('end of list')
            self.board_index -= 1
            return False

        self.do_chan(None)
        
        return False

    def do_chan(self, arg):
        ''' scan adc channel values '''

        for chan in self.channels:
            chan.start_conversion() 
            time.sleep(chan.conversion_time)
        
            volts = chan.get_conversion_volts() * 1000
            print('chan 0x{:x}.{} = {}mV'.format(chan._device._address, 4-chan.number, round(volts,1)))

        print(chan.lsb_voltage, 8191*chan.lsb_voltage, (8192-16384)*chan.lsb_voltage)
        
        return False

    def do_bus(self, arg):
        ''' scan i2c bus for devices '''
        results = subprocess.run(['i2cdetect', '-y', '1'])
        # print(results)

        print()
        print('defined boards: ', end='')
        for addr in addr_list:
            print('0x{:x}, '.format(addr), end='')

        print()
        
        return False
        
    def do_exit(self, arg):
        return True

        
if __name__ == '__main__':
    
    with smbus.SMBus(i2c_bus_number) as smbus:
        shell = Shell(smbus)

        shell.cmdloop()
