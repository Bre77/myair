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
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_AUTO,
    HVAC_MODE_OFF,
    FAN_OFF,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_AUTO,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE,
)

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default='2025'): cv.string,
})

MYAIR_HVAC_MODES = {"heat":HVAC_MODE_HEAT, "cool":HVAC_MODE_COOL, "vent":HVAC_MODE_FAN_ONLY, "dry":HVAC_MODE_DRY}
HASS_HVAC_MODES = {v: k for k, v in MYAIR_HVAC_MODES.items()}

MYAIR_FAN_MODES = {"auto": FAN_AUTO, "low":FAN_LOW, "medium":FAN_MEDIUM, "high":FAN_HIGH}
HASS_FAN_MODES = {v: k for k, v in MYAIR_FAN_MODES.items()}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the myair platform."""
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

    entities = []
    if(coordinator.data):
        for _, acx in enumerate(coordinator.data):
            entities.append(MyAirAC(coordinator, async_set_data, acx))
            for _, zx in enumerate(coordinator.data[acx]['zones']):
                entities.append(MyAirZone(coordinator, async_set_data, acx, zx))
    async_add_entities(entities)
             

class MyAirAC(ClimateEntity):
    """MyAir AC unit"""

    def __init__(self, coordinator, async_set_data, acx):
        self.coordinator = coordinator
        self.async_set_data = async_set_data
        self.acx = acx

    @property
    def name(self):
        return self.coordinator.data[self.acx]['info']['name']

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        return self.coordinator.data[self.acx]['info']['setTemp']

    @property
    def target_temperature_step(self):
        return 1

    @property
    def max_temp(self):
        return 32

    @property
    def min_temp(self):
        return 16

    @property
    def hvac_mode(self):
        if(self.coordinator.data[self.acx]['info']['state'] == "on"):
            return MYAIR_HVAC_MODES.get(self.coordinator.data[self.acx]['info']['mode'],HVAC_MODE_OFF)
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF,HVAC_MODE_COOL,HVAC_MODE_HEAT,HVAC_MODE_FAN_ONLY,HVAC_MODE_DRY]

    @property
    def fan_mode(self):
        return MYAIR_FAN_MODES.get(self.coordinator.data[self.acx]['info']['fan'],FAN_OFF)
    
    @property
    def fan_modes(self):
        return [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC Mode and State"""
        if(hvac_mode == HVAC_MODE_OFF):
            await self.async_set_data({self.acx:{"info":{"state":"off"}}})
        else:
            await self.async_set_data({self.acx:{"info":{"state":"on", "mode": HASS_HVAC_MODES.get(hvac_mode)}}})

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode):
        """Set the Fan Mode"""
        await self.async_set_data({self.acx:{"info":{"state":"on", "fan": HASS_FAN_MODES.get(fan_mode)}}})

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs):
        """Set the Temperature"""
        temp = kwargs.get(ATTR_TEMPERATURE)
        await self.async_set_data({self.acx:{"info":{"setTemp":temp}}})

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class MyAirZone(ClimateEntity):

    def __init__(self, coordinator, async_set_data, acx, zx):
        self.coordinator = coordinator
        self.async_set_data = async_set_data
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return self.coordinator.data[self.acx]['zones'][self.zx]['name']

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        #if(self.coordinator.data[self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return self.coordinator.data[self.acx]['zones'][self.zx]['setTemp']
            

    @property
    def target_temperature_step(self):
        #if(self.coordinator.data[self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return 1

    @property
    def max_temp(self):
        #if(self.coordinator.data[self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return 32

    @property
    def min_temp(self):
        #if(self.coordinator.data[self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return 16

    @property
    def hvac_mode(self):
        if(self.coordinator.data[self.acx]['info']['state'] == "on"):
            return MYAIR_HVAC_MODES.get(self.coordinator.data[self.acx]['info']['mode'],HVAC_MODE_OFF)
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF,HVAC_MODE_COOL,HVAC_MODE_HEAT,HVAC_MODE_FAN_ONLY,HVAC_MODE_DRY]

    @property
    def fan_mode(self):
        if(self.coordinator.data[self.acx]['zones'][self.zx]['state'] == "open"):
            if(self.coordinator.data[self.acx]['zones'][self.zx]['value'] <= 20):
                return FAN_LOW
            elif (self.coordinator.data[self.acx]['zones'][self.zx]['value'] <= 60):
                return FAN_MEDIUM
            else:
                return FAN_HIGH
        else:
            return FAN_OFF

    @property
    def fan_modes(self):
        return [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]

    @property
    def supported_features(self):
        return SUPPORT_FAN_MODE

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC Mode and State"""
        if(hvac_mode == HVAC_MODE_OFF):
            await self.async_set_data({self.acx:{"info":{"state":"off"}}})
        else:
            await self.async_set_data({self.acx:{"info":{"state":"on", "mode": HASS_HVAC_MODES.get(hvac_mode)}}})

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode):
        """Set the Fan Mode"""
        await self.async_set_data({self.acx:{"zones":{self.zx:{"state":"open", "value": 50}}}})

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs):
        """Set the Temperature"""
        temp = kwargs.get(ATTR_TEMPERATURE)
        await self.async_set_data({self.acx:{"zones":{self.zx:{"setTemp":temp}}}})

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_update(self):
        await self.coordinator.async_request_refresh()