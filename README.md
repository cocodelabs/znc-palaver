# Palaver ZNC Module

Palaver ZNC module provides push notifications. This `away` branch will notify you even if you are not marked as `/away`.

## Download

#### Via Git

```bash
$ git clone https://github.com/Palaver/znc-palaver
$ cd znc-palaver
$ git checkout away
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

Notifications will be sent even if you are not marked as away.

