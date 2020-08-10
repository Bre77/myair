"""MyAir climate integration."""

from datetime import timedelta
import logging
import json

from .const import *

from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
)

from homeassistant.helpers import device_registry, collection, entity_component
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

CONFIG_SCHEMA = MYAIR_YAML_SCHEMA

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up MyAir."""
    
    _LOGGER.debug("Setting up MyAir")

    return True

async def async_setup_entry(hass, config_entry):
    #config[DOMAIN]
    host = config_entry.get(CONF_HOST)
    port = config_entry.get(CONF_PORT)
    ssl = config_entry.get(CONF_SSL)
    session = async_get_clientsession(hass)

    if ssl:
        uri_scheme = "https://"
    else:
        uri_scheme = "http://"

    async def async_update_data():
        try:
            resp = await session.get(f"{uri_scheme}{host}:{port}/getSystemData")
            #assert resp.status == 200
            return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error getting MyAir data: {err}")

    async def async_set_data(data):
        try:
            resp = await session.get(f"{uri_scheme}{host}:{port}/setAircon", params={'json':json.dumps(data)}) 
            return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error setting MyAir data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="MyAir",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    device = {
        "identifiers": {(DOMAIN, coordinator.data['system']['mid'])},
        "name": coordinator.data['system']['name'],
        "manufacturer": "Advantage Air",
        "model": coordinator.data['system']['tspModel'],
        "sw_version": coordinator.data['system']['myAppRev'],
    }

    hass.data[DOMAIN] = {
        'coordinator': coordinator,
        'async_set_data': async_set_data,
        'device': device,
    }
    
    # Load Platforms
    for platform in MYAIR_PLATFORMS:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(platform, DOMAIN, {}, config_entry)
        )

    _LOGGER.warn("Setup Input Number platform")

    #if('aircons' in coordinator.data):
    #    entities = []
    #    for _, acx in enumerate(coordinator.data['aircons']):
    #        for _, zx in enumerate(coordinator.data['aircons'][acx]['zones']):
    #            if('value' in coordinator.data['aircons'][acx]['zones'][zx]):
    #                _LOGGER.info("Setup Input Number class")
    #                entities.append(MyAirZoneVentInputNumber(hass, acx, zx))
    #    async_add_entities(entities)
    #return True

    return True