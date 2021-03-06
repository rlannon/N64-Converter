# win_functions.py
# Implementations of the mouse/kbd functions for Windows

import mouse_pos

# win32 input modules
import pydirectinput
import win32api, win32con   # included in pypiwin32

# set pydirectinput's failsafe to false; we aren't using it to drive the mouse
pydirectinput.FAILSAFE = False


def update_keys(pressed_buttons, packet, config):
    """ Updates key presses

        :param pressed_buttons:
            The Buttons object containing currently pressed buttons (as of last controller update)
        
        :param packet:
            The packet of data we are handling
        
        :param config:
            The input configuration
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


def update_mouse(incoming, use_absolute, base_pos):
    """ Updates the mouse based on the current joystick position, assuming the mouse input is to be buffered on Project64
    
        :param incoming:
            The incoming data we are handling (a Buttons object)
    """

    # cast to list type
    incoming = list(incoming)

    # get the joystick positions
    new_x_coord = incoming[7]
    new_y_coord = incoming[8]

    # act based on the mode
    tup = base_pos
    WIN32FLAGS = win32con.MOUSEEVENTF_MOVE
    if use_absolute:
        tup = mouse_pos.get_absolute_pos(new_x_coord, new_y_coord, base_pos)
        WIN32FLAGS += win32con.MOUSEEVENTF_ABSOLUTE
    else:
        # get the position
        tup = mouse_pos.get_mouse_pos(new_x_coord, new_y_coord)
    
    # use the win32api to move the mouse position with a direct input event
    win32api.mouse_event(WIN32FLAGS, tup[0], tup[1], 0)
