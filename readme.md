# MyAir & e-zone Integration

A home assistant integration for Advantage Air "MyAir" and "e-zone" airconditioning control systems, which adds Climate, Motion, and Vent entities into Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Config

Look for the "MyAir & e-zone" integration under Configuration / Integrations, then set the IP address of your Tablet.

## Entities

### Climate
A single climate entity will be created per AC unit. Additional climate entities will be created per zone only if they are temperature controlled, as reported by the API.

### Cover
A cover entity will be created for each zone that is not temperature controlled, allowing you to adjust the opening level from 0% to 100% in 5% increments.

### Sensor
A sensor entity will be created for each zone that is temperature controlled to show how open the damper is.
A sensor entity will be created for each zone that has a wireless temperature/motion sensors that reports its RSSI.

### Binary Sensor
A sensor entity will be created for each zone that has a motion sensor.