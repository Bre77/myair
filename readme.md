# MyAir Integration

A home assistant integration for MyAir airconditioning control systems, which adds Climate, Motion, and Vent entities into Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Config

Add the following to your configuration.yaml
```yaml
myair:
    host: <IP ADDRESS of MyAir Tablet>
    port: 2025 (optional)
    ssl: false (optional)
```