# controller_config
# Contains the Configuration object

import sys
import json

keysym_to_windows = {
    "Control": "ctrl",
    "Shift": "shift",
    "Alt": "alt",
    "Control_L": "ctrlleft",
    "Shift_L": "shiftleft",
    "Alt_L": "altleft",
    "Control_R": "shiftright",
    "Shift_R": "shiftright",
    "Alt_R": "altright",
    "Return": "return",
    "Space": "space",
    "Up": "up",
    "Down": "down",
    "Left": "left",
    "Right": "right",
}

class Configuration:
    def __init__(self, path):
        """ Initializes the object using a configuration file, a text file containing JSON

            Each line of the file should utilize key:value pairs such that:
                * "key" is a string corresponds to a controller button, in all caps, from
                    Z
                    DUP
                    CDOWN
                    START
                    etc.
                * "value" is a string that corresponds to a key following the keysym convention
            See the sample configuration file for a demo
            Note that special keys will automatically be converted for windows/pydirectinput

            :param path:
                The path to the config file (a text file)
        """

        self.buttons = {
            "L":"",
            "R":"",
            "Z":"",
            "DUP":"",
            "DDOWN":"",
            "DLEFT":"",
            "DRIGHT":"",
            "A":"",
            "B":"",
            "CUP":"",
            "CDOWN":"",
            "CLEFT":"",
            "CRIGHT":"",
            "START":""
        }

        is_windows = sys.platform == 'win32'

        file = open(path, mode="r")
        if (file is None):
            raise Exception("Cannot open configuration file; using default")
        
        data = json.load(file)
        for k in self.buttons.keys():
            if k not in data.keys():
                raise Exception(f"No config found for button '{k}'")

            v = data[k]
            if is_windows and v in keysym_to_windows.keys():
                v = keysym_to_windows[v]
            
            self.buttons[k] = v
    
    def __list__(self):
        """ Returns the configuration as a list that the script can use
            The order of items is the same as the key order in self.buttons
            We just need to insert 0 at positions 7 and 8 for x and y
        """
        l = list(self.buttons.values())
        l.insert(7, 0)
        l.insert(8, 0)
        return l
