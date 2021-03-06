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
import threading
from time import sleep

# todo: the windows and linux modules can actually be condensed because the only difference
## between them is the drive functtion

# custom modules
import serial_packet
import mouse_pos

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


def read_packet(con, enabled):
    """ Reads a single packet from the serial connection

        :param con:
            The serial connection
        
        :param packet:
            The incoming packet

        :param enabled:
            Whether the controller is enabled
        
        :returns:
            A tuple containing:
              * the SerialPacket object
              * whether the controller is enabled
    """

    # update our packet information
    data = con.read(serial_packet.SerialPacket.size());
    packet = serial_packet.SerialPacket()
    try:
        packet.update(data)
        if enabled and (packet.buttons.l and packet.buttons.r and packet.buttons.z and packet.buttons.d_down and packet.buttons.c_down):
            enabled = False
            # send a byte to the arduino (to control LED)
            con.write(b'd')
        elif (not enabled) and packet.buttons.start:
            enabled = True
            # send a byte to the arduino (to control LED)
            con.write(b'r')
    except Exception as e:
        # If we encountered a data error, reset our input buffer
        print("An error occurred:", e)
        fixed = False
        while not fixed:
            # check for a magic number, one byte at a time
            # reading one at a time prevents us from being stuck in a loop where we are one byte off
            val = con.read(1)
            if val == b'\x23':
                val = con.read(1)
                if val == b'\xC0':
                    print("Data realigned")
                    fixed = True
                    # Ignore the rest of the data in the block and start fresh with the next one
                    val = con.read(serial_packet.SerialPacket.size() - serial_packet.SerialPacket.magic_number_size())
    
    return (packet, enabled)


def run(config: list, update_keys, update_mouse, board_id: str, use_absolute: bool= False):
    """ The main function, containing the actual driver loop

        :param config:
            The controller configuration, expressed as a Configuration object
    """

    # todo: this continues to poll, but requires sleep(1) to get all ports
    # # why exactly is 1 the magic number? And is there a better way to do this?

    # we must first connect to the Arduino via serial
    # view which connections are available
    listed_ports = list(serial.tools.list_ports.comports())
    
    # now, get one with an arduino connected to it
    print("Searching for Arduino...")
    waited = False  # we will need to wait before we call serial_ports if we connect while the program is running
    arduino_port = ""
    while arduino_port == "":
        for port in listed_ports:
            # Windows systems will report the arduino connected to the port,
            if "Arduino" in port.__str__():
                arduino_port = port.__str__()
                break
            # But on Linux systems, we may have to look for the board's VID:PID
            elif board_id in port.hwid:
                arduino_port = port.__str__()
                break
        
        # if we didn't find a port, update the list
        if arduino_port == "":
            waited = True
            listed_ports = list(serial.tools.list_ports.comports())
    
    print("Found Arduino on port ",arduino_port,".",sep="")
    print("Connecting...")
    
    # if we had to wait for the user to connect the Arduino, sleep for a second
    # this is so serial_ports() can connect as a serial port
    if waited:
        sleep(1)
    
    # get the actual name of the port (such as 'COM5' or 'COM7') that the OS expects
    all_ports = serial_ports()
    to_connect_name = ""
    for port in all_ports:
        if port in arduino_port:
            to_connect_name = port
    if to_connect_name == "":
        raise Exception(f"Could not find port {port}")

    # connect to the serial port
    conn = serial.Serial(to_connect_name, 9600, timeout=3)
    if not conn.is_open:
        conn.open()
    print("Connected on port", to_connect_name, ".", sep="")
    
    # create the SerialPacket object to contain our incoming data
    packet = serial_packet.SerialPacket()

    # create an object to store controller data
    pressed_buttons = serial_packet.Buttons()

    # Reset the serial buffers
    conn.reset_input_buffer()
    conn.reset_output_buffer()

    # Calibrate the controller, if necessary
    base_pos = (0, 0)
    if use_absolute:
        print("Move the mouse to a good known zero point and hit start")
        calibrated = False
        while not calibrated:
            # Read the packet
            packet = read_packet(conn, True)[0]
            if (packet.buttons.start):
                base_pos = mouse_pos.read_current_mouse_position()
                print(f"Using {base_pos} as base position")
                calibrated = True
            continue
    
    # We are now ready to roll
    print("Ready.")

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
            mouse_thread = threading.Thread(target=update_mouse, args=(packet.buttons, use_absolute, base_pos))

            # wait to read until we have enough data in the buffer (the size of one packet)
            if conn.in_waiting >= serial_packet.SerialPacket.size():
                # get the packet
                # data = conn.read(serial_packet.SerialPacket.size());
                temp = read_packet(conn, enabled)
                packet = temp[0]
                enabled = temp[1]

                # perform our updates
                try:
                    # only perform updates if the controller is enabled -- else, ignore the events
                    if enabled:
                        # update the keystrokes and current button data
                        # update_keys(pressed_buttons, packet.buttons, default_config)
                        # update_mouse_absolute(zero_position, packet.buttons)
                        
                        # start the threads
                        #kbd_thread.start()
                        mouse_thread.start()
                        update_keys(pressed_buttons, packet.buttons, config)

                        # wait for the threads to finish
                        #kbd_thread.join()
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
