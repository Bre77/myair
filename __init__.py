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
    TEMP_CELSIUS,
)

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default='2025'): cv.string,
})

async def async_setup(hass, config):
    """Set up MyAir."""
    
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT,'2025')
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            resp = await session.get(f"http://{host}:{port}/getSystemData")
            #assert resp.status == 200
            return (await resp.json())['aircons']
        except Exception as err:
            raise UpdateFailed(f"Error getting MyAir data: {err}")

    async def async_set_data(data):
        try:
            resp = await session.get(f"http://{host}:{port}/setAircon", params={'json':json.dumps(data)}) 
            return (await resp.json())
        except Exception as err:
            raise UpdateFailed(f"Error updating MyAir setting: {err} {data}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="MyAir",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN] = {
        'coordinator': coordinator,
        'async_set_data': async_set_data,
    }

    await hass.helpers.discovery.async_load_platform ('climate', DOMAIN, {}, config)

    return True