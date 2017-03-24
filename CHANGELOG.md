# Changelog for Palaver ZNC Module

## Master

### Enhancements

- Push notifications are now sent for CTCP ACTIONs (`/me` messages).
- Support for FreeBSD has been added.
- Push notifications are no longer sent for NOTICEs that are received before
  registering with the IRC server.

  For example, the following NOTICEs will not send push notifications while
  connecting:

  - Looking up your hostname...
  - Checking Ident
  - Found your hostname
  - Got Ident response

### Bug Fixes

- We now detect when building the module with an unsupported compiler and will
  now produce an error. This detects compilers that do not have a correct regex
  implementation.
- Prevents stripping colour codes from messages incoming IRC messages.
- ZNC will no longer send push notifications to backgrounded Palaver devices.


## 1.0.1

### Bug Fixes

- Fixes a timing issue where the push notification may not be sent due to ZNC
  disconnecting from the push notification server before the request was
  processed.


## 1.0.0

Initial version.
