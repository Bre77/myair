#import logging
#import voluptuous as vol
#import json

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
from homeassistant.components.climate import ClimateEntity
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

#_LOGGER = logging.getLogger(__name__)

MYAIR_HVAC_MODES = {"heat":HVAC_MODE_HEAT, "cool":HVAC_MODE_COOL, "vent":HVAC_MODE_FAN_ONLY, "dry":HVAC_MODE_DRY}
HASS_HVAC_MODES = {v: k for k, v in MYAIR_HVAC_MODES.items()}

MYAIR_FAN_MODES = {"auto": FAN_AUTO, "low":FAN_LOW, "medium":FAN_MEDIUM, "high":FAN_HIGH}
HASS_FAN_MODES = {v: k for k, v in MYAIR_FAN_MODES.items()}
FAN_SPEEDS = {FAN_LOW: 30, FAN_MEDIUM: 60, FAN_HIGH: 100}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up MyAir climate platform."""
    
    coordinator = hass.data[DOMAIN]['coordinator']

    if('aircons' in coordinator.data):
        entities = []
        for _, acx in enumerate(coordinator.data['aircons']):
            entities.append(MyAirAC(hass, acx))
            for _, zx in enumerate(coordinator.data['aircons'][acx]['zones']):
                entities.append(MyAirZone(hass, acx, zx))
        async_add_entities(entities)
    return True            

class MyAirAC(ClimateEntity):
    """MyAir AC unit"""

    def __init__(self, hass, acx):
        self.coordinator = hass.data[DOMAIN]['coordinator']
        self.async_set_data = hass.data[DOMAIN]['async_set_data']
        self.device = hass.data[DOMAIN]['device']
        self.acx = acx

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['info']['name']}"

    @property
    def unique_id(self):
        return f"{self.acx}"

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        return self.coordinator.data['aircons'][self.acx]['info']['setTemp']

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
        if(self.coordinator.data['aircons'][self.acx]['info']['state'] == "on"):
            return MYAIR_HVAC_MODES.get(self.coordinator.data['aircons'][self.acx]['info']['mode'],self.coordinator.data['aircons'][self.acx]['info']['mode'])
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF,HVAC_MODE_COOL,HVAC_MODE_HEAT,HVAC_MODE_FAN_ONLY,HVAC_MODE_DRY]

    @property
    def fan_mode(self):
        return MYAIR_FAN_MODES.get(self.coordinator.data['aircons'][self.acx]['info']['fan'],FAN_OFF)
    
    @property
    def fan_modes(self):
        return [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    @property
    def device_state_attributes(self):
        return self.coordinator.data['aircons'][self.acx]['info']

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return self.device

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

    def __init__(self, hass, acx, zx):
        self.coordinator = hass.data[DOMAIN]['coordinator']
        self.async_set_data = hass.data[DOMAIN]['async_set_data']
        self.device = hass.data[DOMAIN]['device']
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['name']}"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}"

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['measuredTemp']

    @property
    def target_temperature(self):
        #if(self.coordinator.data['aircons'][self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['setTemp']
            

    @property
    def target_temperature_step(self):
        #if(self.coordinator.data['aircons'][self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return 1

    @property
    def max_temp(self):
        #if(self.coordinator.data['aircons'][self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return 32

    @property
    def min_temp(self):
        #if(self.coordinator.data['aircons'][self.acx]['info']['myZone'] == 0):
        #    raise NotImplementedError
        #else:
        return 16

    @property
    def hvac_mode(self):
        if(self.coordinator.data['aircons'][self.acx]['info']['state'] == "on"):
            return MYAIR_HVAC_MODES.get(self.coordinator.data['aircons'][self.acx]['info']['mode'],HVAC_MODE_OFF)
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF,HVAC_MODE_COOL,HVAC_MODE_HEAT,HVAC_MODE_FAN_ONLY,HVAC_MODE_DRY]

    @property
    def fan_mode(self):
        if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == "open"):
            if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['value'] <= (FAN_SPEEDS[FAN_LOW]+10)):
                return FAN_LOW
            elif (self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['value'] <= (FAN_SPEEDS[FAN_MEDIUM]+10)):
                return FAN_MEDIUM
            else:
                return FAN_HIGH
        else:
            return FAN_OFF

    @property
    def fan_modes(self):
        return [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH]

    @property
    def device_state_attributes(self):
        return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return self.device

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
        if(fan_mode == FAN_OFF):
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":"close"}}}})
        else:
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":"open", "value": FAN_SPEEDS[fan_mode]}}}})

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
