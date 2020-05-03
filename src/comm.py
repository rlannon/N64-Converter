"""

N64 Converter
comm.py
Copyright 2020 Riley Lannon

A file for interfacing between the Arduino and pyserial.
This will take the signals generated by the arduino (sent over serial) and convert them into mouse movements and keystrokes.

"""

# libraries
import serial
import serial.tools.list_ports
import sys
import glob

# win32 input modules
import pydirectinput
import win32api, win32con

# custom modules
import serial_packet

# set pydirectinput's failsafe to false; we aren't using it to drive the mouse
pydirectinput.FAILSAFE = False

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def update_keys(pressed_buttons, packet, config):
    """ Updates which keys are being pressed
    """
    incoming = list(packet)
    pressed = list(pressed_buttons)

    i = 0
    while i < incoming.__len__():
        # we only need to make a change if the data aren't the same
        if pressed[i] != incoming[i]:
            # we will drive the mouse separately; skip these
            if i == 7 or i == 8:
                pass
            else:
                if pressed[i]:
                    # print(config[i], ": RELEASE", sep="") # for debug
                    pydirectinput.keyUp(config[i])
                else:
                    # print(config[i], ": PRESS", sep="")   # for debug
                    pydirectinput.keyDown(config[i])
        
        # increment the index
        i += 1

def update_mouse(pressed_buttons, packet):
    pressed = list(pressed_buttons)
    incoming = list(packet)

    # now, update the mouse
    # get the old and new coordinates
    old_x_coord = pressed[7]
    new_x_coord = incoming[7]
    old_y_coord = pressed[8]
    new_y_coord = incoming[8]

    # we only want to change the position of the mouse if the coordinate switches quadrants
    # otherwise, we want to change the *speed* at which we are driving it
    mouse_pos = win32api.GetCursorPos()
    
    # if the joystick returned to its default position, stop mouse movement
    if new_x_coord == 0 and new_y_coord == 0:
        pass
    else:
        y_change = 0
        x_change = 0

        if new_x_coord == 0:
            x_change = 0
        else:
            x_change = new_x_coord / 2
            if x_change == 0 and new_x_coord != 0:
                x_change = 1 if new_x_coord > 0 else -1

        if new_y_coord == 0:
            y_change = 0
        else:
            y_change = new_y_coord / 2
            if y_change == 0 and new_y_coord != 0:
                y_change = 1 if new_y_coord > 0 else -1
            y_change = -y_change
        
        # todo: prevent the failsafe from triggering by resetting the pointer or by disabling the failsafe mechanism
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x_change), int(y_change))

def main():
    # Create a default keyboard configuration, putting in 0 for mouse x and y (handled separately)
    # todo: allow user to supply their own configurations?
    default_config = ['q','w','e','r','t','y','u',0,0,'i','o','a','s','d','f','g']

    # we must first connect to the Arduino via serial
    # view which connections are available
    all_ports = serial_ports()

    listed_ports = list(serial.tools.list_ports.comports())
    arduino_port = ""

    for port in listed_ports:
        if "Arduino" in port.__str__():
            arduino_port = port.__str__()
            break

    if arduino_port == "":
        raise Exception("No Arduino detected")

    to_connect_name = ""
    for port in all_ports:
        if port in arduino_port:
            to_connect_name = port

    if to_connect_name == "":
        raise Exception("Could not find port")

    # connect to the serial port
    conn = serial.Serial(to_connect_name, 9600, timeout=3)
    if not conn.is_open:
        conn.open()

    
    # create the SerialPacket object
    packet = serial_packet.SerialPacket()

    # create an object to store controller data
    pressed_buttons = serial_packet.Buttons()

    # Reset the input buffer
    conn.reset_input_buffer();
    print("Connected.")

    # Our main loop
    quit = False
    num_cycles = 0
    while not quit:
        # read whole objects one at a time -- ensure that we can read the entire object
        if conn.in_waiting >= serial_packet.SerialPacket.size():
            # get the packet
            data = conn.read(serial_packet.SerialPacket.size());

            # update our packet information
            try:
                # print(data)   # for debugging
                packet.update(data)
            except Exception as e:
                # If we encountered a data error, reset our input buffer
                print("Invalid data (specific error was: ", e, "); resetting input buffer", sep="")
                fixed = False
                while not fixed:
                    # check for a magic number, one byte at a time
                    # reading one at a time prevents us from being stuck in a loop where weare one byte off
                    
                    # todo: this misalignment seems to be happening often...
                    # # check for a better fix than just handling the error each time
                    
                    val = conn.read(1)
                    if val == b'\x23':
                        val = conn.read(1)
                        if val == b'\xC0':
                            print("Data realigned")
                            fixed = True
                            val = conn.read(serial_packet.SerialPacket.size() - serial_packet.SerialPacket.magic_number_size())
            
            # perform our updates
            try:
                # update the keystrokes and current button data
                update_keys(pressed_buttons, packet.buttons, default_config)
                update_mouse(pressed_buttons, packet.buttons)
                
                # update the list of currently pressed buttons
                pressed_buttons.update(list(packet.buttons))
            except Exception as e:
                print("An error occurred when trying to drive the kbd/mouse: ", e)

if __name__ == "__main__":
    main()
