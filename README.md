# Palaver ZNC Module

Palaver ZNC module provides push notifications.

## Compiling

    znc-buildmod palaver.cpp

## Installation

Copy the compile ZNC module to your ZNC settings:

    $ cp palaver.so ~/.znc/modules

Now load the ZNC module:

    /msg *status loadmod palaver

##  When will I get notifications?

You will be mentioned when any of the following rules are met:

* You get a private message directly to you.
* Any message which includes your current nickname.
* A message contains a mention keyword from the mention keywords in `Settings > Mentions`

Notifications will only be sent if all your clients are disconnected, or marked
as away. You can use the [clientaway](http://wiki.znc.in/Clientaway) module to
mark a connected client as away.

