import time
import serial
import struct
from collections import namedtuple



# Identify new response packet
SYNC_BYTE = b'\xA5'
SYNC_BYTE2 = b'\x5A'

STOP = b'\x25'
RESET = b'\x40'

#scan types
SCAN = b'\x20'


EXPRESS_SCAN = b'\x82'
EXPRESS_SCAN_SIZE = 84
EXPRESS_SCAN_RESPONSE = 130


#A2M8 constants:

#PWM freq, min 24500, typical 25000, max = 25500
MOTOR_MAX_PWM = 1023
DEFAULT_MOTOR_PWM = 450 #450
SET_PWM_BYTE = b'\xF0'


DESCRIPTOR_LEN = 7

class RPLidarException(Exception):
    '''exception class'''

####################### ????????????????   vad satte jag som trame??
def _process_express_scan(data, new_angle, trame):
    new_scan = (new_angle < data.start_angle) & (trame == 1)
    angle = (data.start_angle + (
            (new_angle - data.start_angle) % 360
            )/32*trame - data.angle[trame-1]) % 360
    distance = data.distance[trame-1]
    return new_scan, None, angle, distance


class RPLidar(object):
    '''test'''    

    def __init__(self, lidarSerial):
        self._serial = None
        self.port = lidarSerial
        self.baudrate = 115200
        self.timeout = 3
        self._motor_speed = DEFAULT_MOTOR_PWM
        self.scanning = [False, 0]      
        self.express_trame = 32      ########### varför?
        self.express_data = False    ####### bug om den inte är false
        self.motor_running = None    ####### bug om inte är None
        self.connect()
        

    def connect(self):
        if self._serial != None:
            self.disconnect()
        try:
            self._serial = serial.Serial(
                self.port, self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout)
        except serial.SerialException as err:
            raise RPLidarException('failed to connect to sensor, err: %s ', err)

    def disconnect(self):
        if self._serial == None:
            return
        self._serial.close()

    def stop_motor(self):
        self._set_pwm(0)
        time.sleep(0.001)
        ######
        self._serial.setDTR(True)
        ######
        self.motor_running = False


    def start_motor(self):
        #####
        self._serial.setDTR(False)
        ####
        self._set_pwm(self._motor_speed)
        self.motor_running = True

    def stop_lidar(self):
        self.stop()
        self.stop_motor()
        self.disconnect()


    def reset(self):
        self._send_command(RESET)
        time.sleep(2)
        self.clean_input()

    def clean_input(self):
        if self.scanning[0]:
            return 'cant clean_input when running scan'
        self._serial.flushInput()
        self.express_trame = 32
        self.express_data = False

    def stop(self):
        self._send_command(STOP)
        time.sleep(2)
        self.scanning[0] = False
        self.clean_input()

  
    def start(self):    #start(self, scan_type='normal'):
        if self.scanning[0]:
            return 'already scanning'
        # Tells sensor what scan we want
        # we are not using the extended version since 
        # the legacy 4k sample rate is fine for our uses
                                                #working mode, 0 ,0 ,0 ,0
        self._send_payload_command(EXPRESS_SCAN, b'\x00\x00\x00\x00\x00')

        dsize, is_single, dtype = self._read_descriptor() ##### is_single, dtype för debugging
   
        self.scanning = [True, dsize]



    def _set_pwm(self, pwm):
        payload = struct.pack('<H', pwm)        ##packeterar om till bytes
        self._send_payload_command(SET_PWM_BYTE, payload)

    @property
    def motor_speed(self):
        return self._motor_speed

    @motor_speed.setter
    def motor_speed(self, pwm):
        assert(0 <= pwm <= MOTOR_MAX_PWM)
        self.motor_speed = pwm
        if self.motor_running:
            self._set_pwm(self._motor_speed)

    def _read_descriptor(self):
        '''returns size, is_single, dtype'''
        descriptor = self._serial.read(DESCRIPTOR_LEN)
        if len(descriptor) != DESCRIPTOR_LEN:
            raise RPLidarException('Descriptor lenght not same')
        elif not descriptor.startswith(SYNC_BYTE + SYNC_BYTE2):
            raise RPLidarException('Bad descriptor start bytes')
        return (descriptor[2], ##########################
                (descriptor[-2] == 0),  #################
                descriptor[-1])######################

    def _read_response(self, dsize):
        '''reads response packet with lenght of 'dsize' bytes'''
        while self._serial.inWaiting() < dsize: #bytes in recieve buffer < dsize
            time.sleep(0.001) #fixable in another way?

        # while 1:
        #     if self._serial.inWaiting() < dsize:
        #         break

        data = self._serial.read(dsize)
        return data

    def _send_payload_command(self, command, payload):
        '''Sends command with payload(message) to sensor'''
        #returns a bytes object containing values
        size = struct.pack('B', len(payload))
        message = SYNC_BYTE + command + size + payload
        checksum = 0
        for v in struct.unpack('B'*len(message), message):
            checksum ^= v 
        message += struct.pack('B', checksum) ### fattar typ hur denna funkar, oklart med ^= dock
        self._serial.write(message)


    def _send_command(self, command):
        message = SYNC_BYTE + command
        self._serial.write(message)


    def iter_measures(self, max_buf_meas=3000):
        try:
            self.start_motor()
            if not self.scanning[0]:
                self.start()
            while True:
                dsize = self.scanning[1]
                if max_buf_meas:
                    data_in_buf = self._serial.inWaiting()
                    if data_in_buf > max_buf_meas:
                        self.stop()
                        self.stop_motor()
                        self.disconnect()
                        raise RPLidarException('buffer overflow')
                        self.stop()
                        self.start()
                
                if self.express_trame == 32:
                    self.express_trame = 0
                    if not self.express_data:
                        self.express_data = ExpressPacket.from_string(self._read_response(dsize))
                    self.express_old_data = self.express_data
                    self.express_data = ExpressPacket.from_string(
                                        self._read_response(dsize))
                self.express_trame += 1
                yield _process_express_scan(self.express_old_data,
                                            self.express_data.start_angle,
                                            self.express_trame)
        except KeyboardInterrupt:
            self.stop_lidar()

    def iter_scans(self, max_buf_meas=3000, min_len=5):
        try:
            scan_list = []
            iterator = self.iter_measures(max_buf_meas)
            for new_scan, quality, angle, distance in iterator:
                if new_scan:
                    if len(scan_list) > min_len: # and old_scan_angle > angle:
                        #######################################
                        ## old_sacn < new_scan = yield scan
                        #######################################
                        yield scan_list
                    scan_list = []
                if distance > 0:
                    scan_list.append((angle ,distance))
        except KeyboardInterrupt:
            self.stop_lidar()


#### frankenstein från typ 4 olika sdks
class ExpressPacket(namedtuple('express_packet',
                               'distance angle new_scan start_angle')):
    sync1 = 0xa
    sync2 = 0x5
    sign = {0: 1, 1: -1}

    @classmethod
    def from_string(cls, data):
        packet = bytearray(data)

        if (packet[0] >> 4) != cls.sync1 or (packet[1] >> 4) != cls.sync2:
            raise ValueError('try to parse corrupted data ({})'.format(packet))

        checksum = 0
        for b in packet[2:]:
            checksum ^= b
        if checksum != (packet[0] & 0b00001111) + ((
                        packet[1] & 0b00001111) << 4):
            raise ValueError('Invalid checksum ({})'.format(packet))

        new_scan = packet[3] >> 7
        start_angle = (packet[2] + ((packet[3] & 0b01111111) << 8)) / 64

        d = a = ()
        for i in range(0,80,5):
            d += ((packet[i+4] >> 2) + (packet[i+5] << 6),)
            a += (((packet[i+8] & 0b00001111) + ((
                    packet[i+4] & 0b00000001) << 4))/8*cls.sign[(
                     packet[i+4] & 0b00000010) >> 1],)
            d += ((packet[i+6] >> 2) + (packet[i+7] << 6),)
            a += (((packet[i+8] >> 4) + (
                (packet[i+6] & 0b00000001) << 4))/8*cls.sign[(
                    packet[i+6] & 0b00000010) >> 1],)
        return cls(d, a, new_scan, start_angle)
    



