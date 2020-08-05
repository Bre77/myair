"""MyAir climate integration."""

from datetime import timedelta
import logging
import voluptuous as vol
import json

from .const import (
    DOMAIN,
)

from homeassistant.const import (
    ATTR_NAME,
    ATTR_TEMPERATURE,
    TEMP_CELSIUS,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    TEMP_CELSIUS,
)

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default='2025'): cv.string,
                vol.Optional(CONF_SSL, default=False): cv.boolean,
                vol.Optional('zones', default=True): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up MyAir."""
    
    host = config[DOMAIN].get(CONF_HOST)
    port = config[DOMAIN].get(CONF_PORT)
    ssl = config[DOMAIN].get(CONF_SSL)
    session = async_get_clientsession(hass)

    if ssl:
        uri_scheme = "https://"
    else:
        uri_scheme = "http://"

    async def async_update_data():
        try:
            resp = await session.get(f"{uri_scheme}{host}:{port}/getSystemData")
            #assert resp.status == 200
            return (await resp.json())['aircons']
        except Exception as err:
            raise UpdateFailed(f"Error getting MyAir data: {err}")

    async def async_set_data(data):
        try:
            resp = await session.get(f"{uri_scheme}{host}:{port}/setAircon", params={'json':json.dumps(data)}) 
            return (await resp.json())
        except Exception as err:
            raise UpdateFailed(f"Error updating MyAir setting: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="MyAir",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    
    hass.data[DOMAIN] = {
        'coordinator': coordinator,
        'async_set_data': async_set_data,
    }

    await coordinator.async_refresh()
    await hass.helpers.discovery.async_load_platform('climate', DOMAIN, {}, config)
    await hass.helpers.discovery.async_load_platform('binary_sensor', DOMAIN, {}, config)
    await hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config)

    return True