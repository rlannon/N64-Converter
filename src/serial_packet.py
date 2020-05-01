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
        self.x_axis = int.from_bytes([packet[7]], byteorder="big", signed=True)
        self.y_axis = int.from_bytes([packet[8]], byteorder="big", signed=True)
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
    def __init__(self):
        self.data = Buttons()
    
    def update(self, packet):
        # todo: checksum stuff
        try:
            checksum = int.from_bytes([packet[16], packet[17]], byteorder="little")
        except Exception as e:
            print(e)
        
        self.buttons.update(packet)
    
    @property
    def buttons(self):
        return self.data
