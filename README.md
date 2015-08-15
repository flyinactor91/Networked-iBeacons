# Networked-iBeacons
iBeacons whose values can be updated remotely by a controller

The beacon.py code has been tested simultaneously on a Pi and Edison being updated by controller.py, but it should work on any system that implements BlueZ.

[Video Demonstration](https://www.youtube.com/watch?v=XDeJwOefse8)

## Setup

To install BlueZ on the Pi and most Linux distros, follow this [guide at Adafruit](https://learn.adafruit.com/pibeacon-ibeacon-with-a-raspberry-pi/setting-up-the-pi). You'll also need a generic BLE USB dongle.

The Intel Edison comes with BlueZ installed and an onboard BLE antena, so the only setup is [turning BLE on](https://software.intel.com/en-us/articles/intel-edison-board-getting-started-with-bluetooth). However, you will need to remove 'sudo' from the commands in beacon.py.

## Usage

On the beacon side, run beacon.py on a network-enabled machine. You'll want to know its IP. It starts with default beacon values. When the beacon recieves new values from the controller, it saves those values to a storage csv which will be loaded next time instead of the defaults. You can also change 'listenIP' so that it will only accept updates from a single IP address for security reasons. By default, it will accept connections from any IP.

On the controller side, it sends updates to beacons based on the contents of a csv file. Each row contains the following fields (in order, comma-seperated, no header):
* IP address
* Company ID (hex)
* Area ID (int or hex)
* Unit ID (int or hex)
* Power (int or hex)

An example csv file is included. After going through the list, it displays an update report including the IP address of any beacons that failed in some way.
