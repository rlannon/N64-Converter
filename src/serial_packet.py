"""
N64 Controller
serial_packet.py
Copyright 2020 Riley Lannon

The SerialPacket class, which holds data for serial packets (and allows us to handle them)
"""

class Buttons:
    def __init__(self):
        self.l = False
        self.r = False
        self.z = False
        self.d_up = False
        self.d_down = False
        self.d_left = False
        self.d_right = False
        self.x_axis = 0
        self.y_axis = 0
        self.a = False
        self.b = False
        self.c_up = False
        self.c_down = False
        self.c_left = False
        self.c_right = False
        self.start = False
    
    def update(self, packet):
        self.l = bool(packet[0])
        self.r = bool(packet[1])
        self.z = bool(packet[2])
        self.d_up = bool(packet[3])
        self.d_down = bool(packet[4])
        self.d_left = bool(packet[5])
        self.d_right = bool(packet[6])
        self.x_axis = int.from_bytes([packet[7]], byteorder="big", signed=True) if type(packet) == bytes else packet[7]
        self.y_axis = int.from_bytes([packet[8]], byteorder="big", signed=True) if type(packet) == bytes else packet[8]
        self.a = bool(packet[9])
        self.b = bool(packet[10])
        self.c_up = bool(packet[11])
        self.c_down = bool(packet[12])
        self.c_left = bool(packet[13])
        self.c_right = bool(packet[14])
        self.start = bool(packet[15])
    
    def __iter__(self):
        yield self.l
        yield self.r
        yield self.z
        yield self.d_up
        yield self.d_down
        yield self.d_left
        yield self.d_right
        yield self.x_axis
        yield self.y_axis
        yield self.a
        yield self.b
        yield self.c_up
        yield self.c_down
        yield self.c_left
        yield self.c_right
        yield self.start
    
    def __list__(self):
        return [self.l, self.r, self.z, self.d_up, self.d_down, self.d_left, \
            self.d_right, self.x_axis, self.y_axis, self.a, self.b, self.c_up, \
                self.c_down, self.c_left, self.c_right, self.start]


class SerialPacket:
    # Static members
    MAGIC_NUMBER_LOW_INDEX = 0
    MAGIC_NUMBER_HIGH_INDEX = 1
    MAGIC_NUMBER_WIDTH = 2
    DATA_BEGIN_INDEX = 2
    CHECKSUM_HIGH_INDEX = 18
    CHECKSUM_LOW_INDEX = 19
    CHECKSUM_WIDTH = 2
    PACKET_WIDTH = 20

    def __init__(self):
        self.data = Buttons()
    
    def update(self, packet):
        # get the header and checksum; make sure the data is usable
        header = [packet[self.MAGIC_NUMBER_LOW_INDEX], packet[self.MAGIC_NUMBER_HIGH_INDEX]]
        checksum = int.from_bytes([packet[self.CHECKSUM_HIGH_INDEX], packet[self.CHECKSUM_LOW_INDEX]], byteorder="little")

        # todo: turn the thrown headers into specific exception classes so they may be handled better

        if header != [0x23, 0xC0]:
            raise Exception("Invalid header")
        
        data_sum = 0
        for i in range(self.DATA_BEGIN_INDEX, len(packet) - self.CHECKSUM_WIDTH):
            data_sum += 0 if packet[i] == 0 else 1
        
        if data_sum != checksum:
            print("found: ", data_sum)
            print("checksum: ", checksum)
            raise Exception("Invalid checksum")

        # update the packet
        self.buttons.update(packet[self.DATA_BEGIN_INDEX:self.CHECKSUM_HIGH_INDEX])
    
    @property
    def buttons(self):
        return self.data

    @staticmethod
    def size():
        return SerialPacket.PACKET_WIDTH
    
    @staticmethod
    def magic_number_size():
        return SerialPacket.MAGIC_NUMBER_WIDTH
