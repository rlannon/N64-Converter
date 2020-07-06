# win_functions.py
# Implementations of the mouse/kbd functions for Windows

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


def update_mouse(incoming):
    """ Updates the mouse based on the current joystick position, assuming the mouse input is to be buffered on Project64
    
        :param incoming:
            The incoming data we are handling (a Buttons object)
    """

    # cast to list type
    incoming = list(incoming)

    # get the joystick positions
    new_x_coord = incoming[7]
    new_y_coord = incoming[8]

    # if the joystick returned to its default position (0,0), stop mouse movement
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
        
        # use the win32api to move the mouse position with a direct input event
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x_change), int(y_change))
