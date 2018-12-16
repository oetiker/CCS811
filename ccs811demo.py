"""
CCS811 Air Quality Sensor Example Code
Author: Sasa Saftic (sasa@infincube.si)
infincube d.o.o.
Date: June 8th, 2017
License: This code is public domain

Based on Sparkfuns Example code written by Nathan Seidle

Read the TVOC and CO2 values from the SparkFun CSS811 breakout board

A new sensor requires at 48-burn in. Once burned in a sensor requires
20 minutes of run in before readings are considered good.

Tested on Raspberry Pi Zero W

2018-12-16

Modified to work with the Omega2+
Tobias Oetiker <tobi@oetiker.ch>

"""

from OmegaExpansion import onionI2C
import time

CCS811_ADDR = 0x5B  # default I2C Address
CSS811_STATUS = 0x00
CSS811_MEAS_MODE = 0x01
CSS811_ALG_RESULT_DATA = 0x02
CSS811_RAW_DATA = 0x03
CSS811_ENV_DATA = 0x05
CSS811_NTC = 0x06
CSS811_THRESHOLDS = 0x10
CSS811_BASELINE = 0x11
CSS811_HW_ID = 0x20
CSS811_HW_VERSION = 0x21
CSS811_FW_BOOT_VERSION = 0x23
CSS811_FW_APP_VERSION = 0x24
CSS811_ERROR_ID = 0xE0
CSS811_APP_START = 0xF4
CSS811_SW_RESET = 0xFF


class CCS811:
    def __init__(self):
        self.i2c = onionI2C.OnionI2C(0)
        self.device = 0x5a
        self.tVOC = 0
        self.CO2 = 0

    def print_error(self):
        error = self.i2c.readBytes(self.device, CSS811_ERROR_ID,1)
        message = 'Error: '

        if error[0] & 1 << 5:
            message += 'HeaterSupply '
        elif error[0] & 1 << 4:
            message += 'HeaterFault '
        elif error[0] & 1 << 3:
            message += 'MaxResistance '
        elif error[0] & 1 << 2:
            message += 'MeasModeInvalid '
        elif error[0] & 1 << 1:
            message += 'ReadRegInvalid '
        elif error[0] & 1 << 0:
            message += 'MsgInvalid '

        print(message)

    def check_for_error(self):
        value = self.i2c.readBytes(self.device, CSS811_STATUS,1)
        return value[0] & 1 << 0

    def app_valid(self):
        value = self.i2c.readBytes(self.device, CSS811_STATUS,1)
        return value[0] & 1 << 4

    def set_drive_mode(self, mode):
        if mode > 4:
            mode = 4

        setting = self.i2c.readBytes(self.device, CSS811_MEAS_MODE,1)
        setting[0] &= ~(0b00000111 << 4)
        setting[0] |= (mode << 4)
        self.i2c.writeBytes(self.device, CSS811_MEAS_MODE, setting)

    def configure_ccs811(self): 
        hardware_id = self.i2c.readBytes(self.device, CSS811_HW_ID,1)

        if hardware_id[0] != 0x81:
            raise ValueError('CCS811 not found. Please check wiring.')

        if self.check_for_error():
            self.print_error()
            raise ValueError('Error at Startup.')

        if not self.app_valid():
            raise ValueError('Error: App not valid.')

        self.i2c.write(self.device, [CSS811_APP_START])
        time.sleep(0.1)

        if self.check_for_error():
            self.print_error()
            raise ValueError('Error at AppStart.')

        self.set_drive_mode(1)

        if self.check_for_error():
            self.print_error()
            raise ValueError('Error at setDriveMode.')

    def setup(self):
        print('Starting CCS811 Read')
        self.configure_ccs811()
        
#        result = self.get_base_line()
#
#        print("baseline for this sensor: 0x")
#        if result < 0x100:
#            print('0')
#        if result < 0x10:
#            print('0')
#        print(result)

    def get_base_line(self):
        a = self.i2c.readBytes(self.device, CSS811_BASELINE, 2)
        baselineMSB = a[0]
        baselineLSB = a[1]
        baseline = (baselineMSB << 8) | baselineLSB
        return baseline

    def data_available(self):
        value = self.i2c.readBytes(self.device, CSS811_STATUS,1)
        return value[0] & 1 << 3
 
    def run(self, write_to_file=False):

        self.setup()

        while True:
           if self.data_available():
                self.read_logorithm_results()
                print("CO2: %3dppm tVOC: %3d" % (self.CO2, self.tVOC))
                
           elif self.check_for_error():
                self.print_error()

           time.sleep(1)

    def read_logorithm_results(self):
        b = self.i2c.readBytes(self.device, CSS811_ALG_RESULT_DATA, 4)

        co2MSB = b[0]
        co2LSB = b[1]
        tvocMSB = b[2]
        tvocLSB = b[3]

        self.CO2 = (co2MSB << 8) | co2LSB
        self.tVOC = (tvocMSB << 8) | tvocLSB

c = CCS811()

c.run(True)