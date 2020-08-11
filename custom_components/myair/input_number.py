import logging

from .const import *

from homeassistant.const import (
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_ICON,
)
from homeassistant.components.input_number import (
    InputNumber,
    CONF_INITIAL,
    CONF_MIN,
    CONF_MAX,
    CONF_STEP,
    CONF_MODE,
    MODE_SLIDER,
    ATTR_INITIAL,
    ATTR_VALUE,
    ATTR_MIN,
    ATTR_MAX,
    ATTR_STEP,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up MyAir input platform."""
    
    coordinator = hass.data[DOMAIN]['coordinator']
    _LOGGER.info("Setup Input Number platform")

    if('aircons' in coordinator.data):
        entities = []
        for _, acx in enumerate(coordinator.data['aircons']):
            for _, zx in enumerate(coordinator.data['aircons'][acx]['zones']):
                if('value' in coordinator.data['aircons'][acx]['zones'][zx]):
                    _LOGGER.info("Setup Input Number class")
                    entities.append(MyAirZoneVentInputNumber(hass, acx, zx))
        async_add_entities(entities)
    return True
             
class MyAirZoneVentInputNumber(InputNumber):
    def __init__(self, hass, acx, zx):
        _LOGGER.info("Input Number class created")
        self.editable = True
        self.coordinator = hass.data[DOMAIN]['coordinator']
        self.device = hass.data[DOMAIN]['device']
        self.async_set_data = hass.data[DOMAIN]['async_set_data']
        self.acx = acx
        self.zx = zx
        self._config = {
            CONF_MIN: 0,
            CONF_MAX: 100,
            CONF_STEP: 5,
            ATTR_UNIT_OF_MEASUREMENT: '%',
            CONF_MODE: MODE_SLIDER,
        }

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['name']} Vent"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}-vent-input"

    @property
    def state(self):
        if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == 'open'):
            return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['value']
        else:
            return 0

    @property
    def icon(self):
        return ["mdi:fan-off","mdi:fan"][self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == 'open']

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return self.device

    async def async_set_value(self, value):
        """Set new value."""
        num_value = float(value)

        if num_value <= 0:
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":"close"}}}})
        elif num_value >= 100:
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":"open", "value": 100}}}})
        else:
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":"open", "value": num_value}}}})

        #self._current_value = num_value
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()