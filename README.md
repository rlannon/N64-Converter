# N64-Converter

An Arduino project to create an N64-USB adapter (for use in emulators).

## About this project

The N64 joystick can be kind of a pain in an emulator; using digital signals for an analog device means choppy movements and an inability to make fine adjustments, which can make some games frustrating to play. Some people find ways to configure the mouse and keyboard to allow the mouse to offer this analog capability, while others simply buy USB N64 controllers and call it a day. However, sometimes, these controllers often require special drivers that may not be installed. If you're like me, and have an Arduino and some N64 controllers lying around (but want to play games in an emulator for a variety of reasons), why not just make an N64 to USB converter?

This project is designed for the Arduino Uno, but should work on (or be easily adapted for) a variety of models.

## Getting Started

This project utilizes the Arduino to interpret the N64 controller signals and Python to convert those signals into actual key presses and mouse movement on the host computer. This project currently only works on Windows, as due to the way it must drive the keyboard and mouse to be able to work in emulators (by creating events and sending direct input to the system, rather than simulating input which is what most Python keyboard/mouse libraries do), it uses the Win32 API. I intend on developing Linux- and Mac-friendly versions as well, though that will happen after I get the Windows version up and running.

### Device Driver

The controller for the N64 operates in quite a complicated fashion, and requires very specific timings in order to allow communication to be possible. Unfortunately, these timings must be so precise that even C is too slow. As such, we need a driver written (at least mostly) in assembly. Luckily, someone has already done that for us. In order for the Arduino program to work, you will need to include [this library by pothos](https://github.com/pothos/arduino-n64-controller-library). A future version of this project may utilize a custom, reworked device driver, but for the time being, pothos' will suffice.

### Communication with host

The Arduino Uno doesn't offer much by way of communication with the host computer. However, it does allow for serial communication when plugged in with a USB, which is exactly how this library communicates with the included python scripts. The port will be automatically selected based on whichever port the Arduino is plugged into.

### Keyboard Controller

Once the Arduino gets the button data from the controller, it sends it to the host computer where the included python script can interpret the data and control the keyboard and mouse movements. These events are direct input events and utilize the Win32 API. Using other Python libraries to drive the keyboard and mouse may work for many applications, but not videogames and emulators, which often hook keyboard and mouse inputs directly and so will not respond to simulated inputs such as those generated by Pynput or PyAutoGUI.

### Wiring

The N64 controller must be connected to the Arduino via +3.3V (**not** 5V, as this may fry the controller board), GND, and digital pin 2 (this may be modified in the code, I just chose pin 2). The wiring to the controller looks like this (looking at the plug head on, with the flat side on bottom and 'Nintendo' facing up):

      /------------\
     / O    O     O \
    | GND Data +3.3V |
    |________________|

## Known Issues

This project is far from perfect. While communicating with the host using serial might not necessarily be the *optimal* way to do things, it is the only way possible on the Arduino Uno (as it can't really act as an HID-compliant device, unless I'm mistaken -- in which case, let me know, please!). Some known issues at the time are:

* The Arduino library does not currently wait to finish initialization until an N64 controller is connected; if none is plugged in to start, there is no guarantee it will work and a reset is required
* Some button presses may not register, or may be finnicky, when utilizing the joystick at the same time. The only time I have run into this issue is playing TLoZ: Majora's Mask on Project64, but it has been a consistent problem in that game with the A button (but no others). I have not yet determined whether it is an issue with my controller, in the controller driver, or in the Python code
