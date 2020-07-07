# mouse_pos.py
# A module to calculate mouse position

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
    
    return (int(x_change), int(y_change))
