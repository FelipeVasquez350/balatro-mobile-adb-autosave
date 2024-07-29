# balatro-mobile-adb-autosave
 An attempt to have a save-sync solution for the unofficial android version of Balatro

## Supported Platforms
Only tested on Linux for now, ~~might implement a Windows version in the future~~

Fuck it here's a docker container so i don't have to deal with Windows's paths & filesystem

>```bash
>  docker pull ghcr.io/felipevasquez350/balatro-mobile-adb-autosave:latest
>```

For running the docker image see [DOCKER.md](DOCKER.md) for more information

## WARNING
The following procedures require leaving `USB Debugging` ***allowed*** all the time, which is generally **NOT RECOMMENDED**, as it's a potential security issue and should be used at your own risk.

I'll elaborate a bit more on this, so:
- USB debugging *only* works when the device is physically connected via a usb cable to a pc and gets the authentication from the connected device
- Wireless debugging **requires** a connection with USB debugging beforehand, and only works when in WiFi mode, on the wifi network authorized from the device using a set of `adbkeys` previously authorized from the device.
- After a reboot, the authentication is automatically revoked for USB debugging, which requires a new manual connection

So the only reasonable way to become a serious security vulnerability is by either:
- having the pc connected via usb to be infected (already bad situation)
- having any device with access to your adbkeys in your wifi network infected (even worse)

## Requirements
- Steam version of Balatro on the computer running this service
- Android device with game installed using [blake502's balatro-mobile-maker](https://github.com/blake502/balatro-mobile-maker) (it has to be installed via ADB in order for this to work)
- Android device with developer options -> Wireless Debugging enabled (first attempt requires USB debugging)

See [SETUP.md](SETUP.md) for more information

## Use case
https://github.com/user-attachments/assets/b22b98cc-ddd6-41ca-8347-572f4ff58517
