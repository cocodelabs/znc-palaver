# Palaver ZNC Module

Palaver ZNC module provides push notifications.

## Compiling

    znc-buildmod palaver.cpp

## Installation

Copy the compile ZNC module to your ZNC settings:

    $ cp palaver.so ~/.znc/modules

Now load the ZNC module:

    /msg *status loadmod palaver

