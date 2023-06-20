# apart_concept_ha

Custom component for APrart Concept 1 amplifiers for Homeassistant

This is VERY BAD code as I don't really know python and I don't think HASS have done a good job documenting stuff. They just keep making it more complex with config flows and stuff.

Requires either an RS232 port on your HASS host or better yet a (decent) RS232 serial server

## Example config section
```
media_player:
  - platform: apart_concept_ha
    url: socket://10.0.2.50:4000
    name: "Garden Amp"
    scan_interval: 5
```
