"""

N64 Converter
comm.py
Copyright 2020 Riley Lannon

A file for interfacing between the Arduino and pyserial.
This will take the signals generated by the arduino (sent over serial) and convert them into mouse movements and keystrokes.

"""

# libraries
import argparse
import serial
import serial.tools.list_ports
import sys
import glob
import threading

import controller_config

# Define our VID:PID numbers for each board that we support
vid_pid = {
    "uno": "VID:PID=2341:0043"
}

# Create some named variables for functions
update_keys = None
update_mouse = None

# Create a default keyboard configuration, putting in 0 for mouse x and y (handled separately)
default_config = []

# Check to see the current platform; if we are on windows, load the windows module
# We also need to initialize our functions
supported = True
if sys.platform == "win32":
    import win_functions

    update_keys = win_functions.update_keys
    update_mouse = win_functions.update_mouse

    # Give our custom Project64 config
    default_config = ['q','w','e','r','t','y','u',0,0,'i','o','a','s','d','f','g']
elif sys.platform.startswith('linux'):
    import linux_functions

    update_keys = linux_functions.update_keys
    update_mouse = linux_functions.update_mouse

    # Give defaults for Mupen64Plus
    default_config = ['x','c','z','w','s','a','d',0,0,'Shift_L','Control_L','i','k','j','l','Return']
else:
    supported = False

# todo: the windows and linux modules can actually be condensed because the only difference
## between them is the drive functtion

# custom modules
import serial_packet

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


def main(config: list, board_id: str = ""):
    """ The main function, containing the actual driver loop

        :param config:
            The controller configuration, expressed as a Configuration object
    """

    # todo: if an Arduino isn't found, continue polling until we find it

    # we must first connect to the Arduino via serial
    # view which connections are available
    all_ports = serial_ports()
    listed_ports = list(serial.tools.list_ports.comports())
    
    # now, get one with an arduino connected to it
    arduino_port = ""
    for port in listed_ports:
        # Windows systems will report the arduino connected to the port,
        if "Arduino" in port.__str__():
            arduino_port = port.__str__()
            break
        # But on Linux systems, we may have to look for the board's VID:PID
        elif board_id in port.hwid:
            arduino_port = port.__str__()
            break
    if arduino_port == "":
        raise Exception("No Arduino detected")
    else:
        print("Found Arduino:",arduino_port)

    # get the actual name of the port (such as 'COM5' or 'COM7') that the OS expects
    to_connect_name = ""
    for port in all_ports:
        if port in arduino_port:
            to_connect_name = port
    if to_connect_name == "":
        raise Exception("Could not find port")
    else:
        print("Connected on port",to_connect_name)

    # connect to the serial port
    conn = serial.Serial(to_connect_name, 9600, timeout=3)
    if not conn.is_open:
        conn.open()
    
    # create the SerialPacket object to contain our incoming data
    packet = serial_packet.SerialPacket()

    # create an object to store controller data
    pressed_buttons = serial_packet.Buttons()

    # Reset the serial buffers
    conn.reset_input_buffer()
    conn.reset_output_buffer()
    print("Connected.")
    
    # allow us to enable and disable the controller from updating with key combos
    # for now, make it L+R+Z+D_DOWN+C_DOWN, as that's a very unusual/uncomfortable position
    # and make the re-enable the start button
    enabled = True
    
    # utilize a sentinel variable for the main loop
    quit = False

    # our main program loop -- this will process the arduino's serial data and drive the kbd/mouse
    while not quit:
        try:
            # set up keyboard and mouse threads
            # in order to allow combo joystick and button actions, they must be driven simultaneously
            kbd_thread = threading.Thread(target=update_keys, args=(pressed_buttons, packet.buttons, default_config))
            mouse_thread = threading.Thread(target=update_mouse, args=([packet.buttons]))   # note that since we have a list argument, we must encapsulate it with [] to avoid an error from 'threading'
            # note: absolute mouse position is also supported in some emulators, but this can be incredibly finnicky
            # # as such, I'm not touching it here (and threads will have to do!)

            # wait to read until we have enough data in the buffer (the size of one packet)
            if conn.in_waiting >= serial_packet.SerialPacket.size():
                # get the packet
                data = conn.read(serial_packet.SerialPacket.size());
                
                # update our packet information
                try:
                    # print(data)   # for debugging
                    packet.update(data)
                    if enabled and (packet.buttons.l and packet.buttons.r and packet.buttons.z and packet.buttons.d_down and packet.buttons.c_down):
                        enabled = False
                        # send a byte to the arduino (to control LED)
                        conn.write(b'd')
                    elif (not enabled) and packet.buttons.start:
                        enabled = True
                        # send a byte to the arduino (to control LED)
                        conn.write(b'r')
                except Exception as e:
                    # If we encountered a data error, reset our input buffer
                    print("An error was encountered when trying to data from the adapter; resetting the input buffer")
                    print("The specific error message was:", e)
                    fixed = False
                    while not fixed:
                        # check for a magic number, one byte at a time
                        # reading one at a time prevents us from being stuck in a loop where we are one byte off
                        val = conn.read(1)
                        if val == b'\x23':
                            val = conn.read(1)
                            if val == b'\xC0':
                                print("Data realigned")
                                fixed = True
                                # Ignore the rest of the data in the block and start fresh with the next one
                                val = conn.read(serial_packet.SerialPacket.size() - serial_packet.SerialPacket.magic_number_size())
                
                # perform our updates
                try:
                    # only perform updates if the controller is enabled -- else, ignore the events
                    if enabled:
                        # update the keystrokes and current button data
                        # update_keys(pressed_buttons, packet.buttons, default_config)
                        # update_mouse_absolute(zero_position, packet.buttons)
                        
                        # start the threads
                        kbd_thread.start()
                        mouse_thread.start()

                        # wait for the threads to finish
                        kbd_thread.join()
                        mouse_thread.join()

                        # update the list of currently pressed buttons
                        pressed_buttons.update(list(packet.buttons))
                except Exception as e:
                    print("An error occurred when trying to drive the kbd/mouse: ", e)
        except KeyboardInterrupt:
            quit = True
    
    # once we quit, close the connection
    print()
    print("Exiting...")
    conn.close()


if __name__ == "__main__":
    # ensure the platform is supported
    if supported:
        # parse CL arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c',
            '--config',
            type=str,
            help="The path to the config file you wish to use",
            default=""
        )
        parser.add_argument(
            '-b',
            '--board',
            type=str,
            help="The Arduino board model",
            required=True
        )
        args = parser.parse_args()

        board_id = ""
        if args.board in vid_pid.keys():
            board_id = vid_pid[args.board]
        else:
            print("Board type not supported")
            exit()

        config = []
        if (args.config):
            try:
                cfg_obj = controller_config.Configuration(args.config)
                config = cfg_obj.__list__()
            except Exception as e:
                print("Note:", e)
                config = default_config

        try:
            main(config)
        except Exception as e:
            print("Error:", e)
    else:
        print("Err: This platform is not supported")
