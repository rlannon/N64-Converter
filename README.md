# N64-Converter

An Arduino project to create an N64-USB adapter (for use in emulators).

## About this project

The N64 joystick can be kind of a pain in an emulator; using digital signals for an analog device means choppy movements and an inability to make fine adjustments, which can make some games frustrating to play. Some people find ways to configure the mouse and keyboard to allow the mouse to offer this analog capability, while others simply buy USB N64 controllers and call it a day. However, sometimes, these controllers often require special drivers that may not be installed. If you're like me, and have an Arduino and some N64 controllers lying around (but want to play games in an emulator for a variety of reasons), why not just make an N64 to USB converter?

This project is designed for the Arduino Uno, but should work on (or be easily adapted for) a variety of models.

## Getting Started

This project utilizes the Arduino to interpret the N64 controller signals and Python to convert those signals into actual key presses and mouse movement on the host computer. This project currently only works on Windows (tested on Project64) and is currently being adapted to allow use within Linux (tested on Mupen64Plus). Simply connect the controller, along with the signal LEDs, to the Arduino as specified below, and connect to the host via a USB cable. When the Python script starts, it will automatically search for the Arduino and establish a serial connection, so the Arduino should be connected before the Python script is run.

### Device Driver

The controller for the N64 operates in quite a complicated fashion, and requires very specific timings in order to allow communication to be possible. Unfortunately, these timings must be so precise that even C is too slow (or inaccurate). As such, we need a driver written (at least mostly) in assembly. Luckily, someone has already done that for us. In order for the Arduino program to work, you will need to include [this library by pothos](https://github.com/pothos/arduino-n64-controller-library). A future version of this project may utilize a custom, reworked device driver, but for the time being, pothos' will suffice.

### Communication with host

The Arduino Uno doesn't offer much by way of communication with the host computer. However, it does allow for serial communication when plugged in with a USB, which is exactly how this library communicates with the included python scripts. The port will be automatically selected based on whichever port the Arduino is plugged into.

### Keyboard Controller

In order to work in emulators, the program must create keyboard and mouse events that can be directly detected by the emulator. This is not possible when using existing cross-platform keyboard and mouse libraries such as `pyautogui`; while such events are simulated, they cannot be hooked by the emulator, and as such, the emulator cannot be controlled by the script.

Currently, the Windows version relies on the Win32API and [`pydirectinput`](https://pypi.org/project/PyDirectInput/). The Linux version relies on [`xdotool`](http://manpages.ubuntu.com/manpages/trusty/man1/xdotool.1.html) and `subprocess`.

### Wiring

The N64 controller must be connected to the Arduino via +3.3V (**not** 5V, as this may fry the controller board), GND, and digital pin 2 (this may be modified in the code, I just chose pin 2). The wiring to the controller looks like this (looking at the plug head on, with the flat side on bottom and 'Nintendo' facing up):

      /------------\
     / O    O     O \
    | GND Data +3.3V |
    |________________|

The included code for the Arduino also drives a few LEDs to indicate various status information. These LEDs, the `WAIT_PIN` and the `READY_PIN`, are by default wired to pins 4 and 7, respectively, but this can be changed in the code by altering the appropriate macros.

## Using the Converter

To use, simply:

* Upload the `.ino` file to your Arduino
* Connect the controller and LEDs to the board as described
* Connect the Arduino to your computer via USB
* Run the Python script `comm.py`

Everything in the Python script should happen automatically; it will try to find and connect to the Arduino and establish a serial connection, fixing any issues it can as they arise.

If the inputs `L + R + Z + D_DOWN + C_DOWN` are detected, the Python script will not drive the mouse and keyboard, effectively disabling the controller. Once it detects a start button press, the controller will be re-enabled. The script will also send `'d'` to the Arduino over serial when disabled, and `'r'` when re-enabled so that the Arduino can change the LEDs.

The program will, in the future, allow the emulator and configuration schemes to be specified. For now, however, keep in mind:

* On Mupen64Plus, it is recommended that you use a mouse scaling factor of 1.0/1.0 for best results
* On Project64, absolute position should be specified as the script can't establish a base position with the relative option
* This has only been tested with an Arduino Uno on the following systems/emulators:
  * Windows 10 with Project64
  * Ubuntu 18 wth Mupen64Plus

## Known Issues

This project is far from perfect. While communicating with the host using serial might not necessarily be the *optimal* way to do things, it is the only way possible on the Arduino Uno (as it can't really act as an HID-compliant device, unless I'm mistaken -- in which case, let me know, please!). Some known issues at the time are:

* The Arduino library does not currently wait to finish initialization until an N64 controller is connected; if none is plugged in to start, there is no guarantee it will work and a reset is required
* Due to the way the joystick controls the mouse, slight fluttering can occur when moving the stick slowly
