# mouse_pos.py
# A module to calculate mouse position

import sys

def read_current_mouse_position():
    """ Reads the current mouse position on the user's screen

        :returns:
            A tuple with the (x, y) coordinates of the cursor
    """
    import pyautogui
    pyautogui.FAILSAFE = False
    return pyautogui.position() 


def get_mouse_pos(new_x_coord, new_y_coord):
    """ Gets the updated mouse position

        :param new_x_coord:
            The new x coordinate as reported by the controller
        
        :param new_y_coord:
            The new y coordinate as reported by the controller
    """

    x_change = 0
    y_change = 0
    
    # if the joystick returned to its default position (0,0), stop mouse movement
    if not (new_x_coord == 0 and new_y_coord == 0):
        if new_x_coord == 0:
            x_change = 0
        else:
            x_change = new_x_coord

        if new_y_coord == 0:
            y_change = 0
        else:
            y_change = -new_y_coord
    
    return (int(x_change), int(y_change))


def get_absolute_pos(x, y, base):
    """ Returns the absolute mouse position based on the mouse position of the joystick

        :param x:
            The new x
        
        :param y:
            The new y
        
        :param base:
            A tuple containing the base position
    """

    new_x = base[0] + int(x / 2)
    new_y = base[1] - int(y / 2)

    return (new_x, new_y)
