# Palaver ZNC Module

[![Build Status](https://img.shields.io/circleci/project/cocodelabs/znc-palaver/master.svg)](https://circleci.com/gh/cocodelabs/znc-palaver)

Palaver ZNC module provides push notifications.

## Download

#### Via Git

```bash
$ git clone https://github.com/Palaver/znc-palaver
$ cd znc-palaver
```

#### Via wget

```bash
$ wget https://github.com/Palaver/znc-palaver/archive/master.zip
$ unzip master.zip
$ cd znc-palaver-master
```

## Compiling

```bash
$ make
```

## Installation

Copy the compile ZNC module to your ZNC settings:

```bash
$ cp palaver.so ~/.znc/modules
```

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

