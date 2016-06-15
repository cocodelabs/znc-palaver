---
Latest Version: 1.0.1
---

# Palaver ZNC Module

[![Build Status](https://img.shields.io/circleci/project/cocodelabs/znc-palaver/master.svg)](https://circleci.com/gh/cocodelabs/znc-palaver)

Palaver ZNC module provides push notifications to Palaver while Palaver is
disconnected from IRC.

##  When will I get notifications?

You will receive a push notification when any of the following rules are met:

* You get a private message directly to you.
* Any message which includes your current nickname.
* A message contains a mention keyword from the mention keywords in `Settings > Mentions`

Notifications will ONLY be sent if all your clients are disconnected, or marked
as away. You can use the [clientaway](http://wiki.znc.in/Clientaway) module to
mark a connected client as away.

This is so while you are on IRC on another device you wont receive many
notifications on your phone at the same time.

## Installation

### Download the module

#### Via Git (recommended)

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

### Compiling

```bash
$ make
```

### Installation the module

Copy the compile ZNC module to your ZNC settings:

```bash
$ cp palaver.so ~/.znc/modules
```

Now load the ZNC module:

    /msg *status loadmod palaver

### Upgrading

When upgrading the module to a newer version be sure to run
`/msg *status unloadmod palaver` before you copy the updated module into
place. Without doing this, you may experiance an issue where you will be
unable to load the update version correctly without restarting ZNC.

## Debugging

If you are having any problems with the module you can follow the
following steps to debug your setup.

1. Ensure you are running the latest version of the ZNC Palaver module and ZNC 1.6 or newer.
1. Check if your device has succsessfully registered with ZNC. You can run `/msg *palaver info` and it will let you know if your device is registered.
1. Run `/msg *palaver test` to send a test notification to your registered devices.
   
#### My device is registered, but I don't receive any push notifications

There may be a few reasons for this problem, you can run ZNC in debug mode
(`znc --debug`) while you send `/msg *palaver test` to find out more.
ZNC will then output why the notification failed to send.

##### Common reasons

###### SSL Handshake failure

This is most likely due to using older versions of OpenSSL. Upgrading to the latest version of OpenSSL and recompiling ZNC against the modern version of OpenSSL should solve your problem.

###### "Connect Failed. ERRNO [101]" or "Network is unreachable"

This error indicates that ZNC was unable to send the push notification due to the network being unreachable. This may be that caused by your operating system or ZNC being configured for IPv6 when your service provider does not support it.

To solve this problem you can force IPv4 connections in ZNC using:

```
/msg *status setbindhost 0.0.0.0
```

###### Caught regex error

This error indicates a problem with the C++ regex implementation in your C++
compiler. Older versions of GCC have buggy implementations of regex and are
incompatible with the module. GCC 4.9 or newer, and Clang are known to work.
Please upgrade to a modern version.
