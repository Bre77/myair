This project has been integrated into Home Assistant Core now, see https://www.home-assistant.io/integrations/advantage_air/

# MyAir & e-zone Integration

A home assistant integration for Advantage Air "MyAir" and "e-zone" airconditioning control systems, which adds Climate, Motion, and Vent entities into Home Assistant

## Config

Look for the "MyAir & e-zone" integration under Configuration / Integrations, then set the URL address of your Tablet.

## Entities

### Climate
A climate entity will be created per AC unit. Additional climate entities will be created per zone only if they are temperature controlled, as reported by the API.

### Cover
A cover entity will be created for each zone that is not temperature controlled, allowing you to adjust the opening level from 0% to 100% in 5% increments.

### Sensor
A sensor entity will be created for the Air Filter, showing if it needs to be replaced.
Two sensor entity will be created for the 'time to on' and 'time to off' features. Use the myair.time_to service to change these.
A sensor entity will be created for each zone that is temperature controlled to show how open the damper is.
A sensor entity will be created for each zone that has a wireless temperature/motion sensors that reports its wireless RSSI.

### Binary Sensor
A binary sensor entity will be created for each zone that has a motion sensor.

## Services
A service named "myair.time_to" can be used to change the value of the sensor.xxx_time_to_on/off sensors.
