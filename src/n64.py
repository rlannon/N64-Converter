"""
n64.py
The main file for the converter
Copyright 2020 Riley Lannon
"""

import sys
import comm
import argparse
import controller_config

if __name__ == "__main__":
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
    if sys.platform.startswith("win"):
        import win_functions

        update_keys = win_functions.update_keys
        update_mouse = win_functions.update_mouse

        # Give our custom Project64 config
        default_config = ['q','w','e','r','t','y','u',0,0,'i','o','a','s','d','f','g']
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        import linux_functions

        update_keys = linux_functions.update_keys
        update_mouse = linux_functions.update_mouse

        # Give defaults for Mupen64Plus
        default_config = ['x','c','z','w','s','a','d',0,0,'Shift_L','Control_L','i','k','j','l','Return']
    else:
        supported = False
        
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
            "-b",
            "--board",
            type=str,
            help="The board model you are using",
            default="uno"
        )
        parser.add_argument(
            '-a',
            '--absolute',
            action='store_true',
            help='Use the absolute mouse position (optimal performance; requires calibration)'
        )
        args = parser.parse_args()

        board_id = ""
        if args.board in vid_pid.keys():
            board_id = vid_pid[args.board]
        else:
            print("Board type not supported")
            exit()

        # Get our configuration, if one was supplied
        config = []
        if (args.config):
            try:
                cfg_obj = controller_config.Configuration(args.config)
                config = cfg_obj.__list__()
            except Exception as e:
                print("Error:", e)
                print("Using default configuration.")
                config = default_config
        else:
            config = default_config

        try:
            comm.run(config, update_keys, update_mouse, board_id, args.absolute)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print("Error:", e)
    else:
        print("Err: This platform is not supported")
