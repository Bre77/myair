import voluptuous as vol
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
)

DOMAIN = "myair"
MYAIR_ZONE_OPEN = "open"
MYAIR_ZONE_CLOSE = "close"
MYAIR_PLATFORMS = ['climate','binary_sensor','sensor','cover']
MYAIR_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default='2025'): int,
    vol.Optional(CONF_SSL, default=False): bool,
})
MYAIR_YAML_SCHEMA = vol.Schema({DOMAIN: MYAIR_SCHEMA}, extra=vol.ALLOW_EXTRA)