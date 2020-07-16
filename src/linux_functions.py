# linux_functions.py
# Implementations of the mouse/keyboard functions for linux systems

# utilize xdotool for this
import subprocess
import mouse_pos


def update_keys(pressed_buttons, packet, config):
    """ Updates key presses

        :param pressed_buttons:
            The Buttons object containing *currently* pressed keys
        
        :param packet:
            The incoming data
        
        :param config:
            The input configuration
    """
    # get the incoming and currently pressed keys
    incoming = list(packet)
    pressed = list(pressed_buttons)

    # iterate through the lists
    i = 0
    while i < incoming.__len__():
        # only look at keys that have different values
        if pressed[i] != incoming[i]:
            if i == 7 or i == 8:
                pass
            else:
                if pressed[i]:
                    # print(config[i], "is released")   # for debug
                    subprocess.call(["xdotool","keyup",config[i]])
                else:
                    #print(config[i], "is pressed")  # for debug
                    subprocess.call(["xdotool","keydown",config[i]])
        # increment the index
        i += 1
    
    return


def update_mouse(incoming):
    """ Updates the mouse position

        :param incoming:
            The incoming data
    """

    # cast to list type
    incoming = list(incoming)

    # get the joystick positions
    new_x_coord = incoming[7]
    new_y_coord = incoming[8]

    # get the change
    tup = mouse_pos.get_mouse_pos(new_x_coord, new_y_coord)
    
    # drive the mouse
    subprocess.call(["xdotool", "mousemove_relative", "--", tup[0].__str__(), tup[1].__str__()])

    return
