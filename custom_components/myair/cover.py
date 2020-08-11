from .const import *

from homeassistant.const import (
    STATE_OPEN,
    STATE_CLOSED,
)

from homeassistant.components.cover import (
    CoverEntity,
    DEVICE_CLASS_DAMPER,
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    ATTR_POSITION,
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up MyAir cover platform."""
    
    coordinator = hass.data[DOMAIN]['coordinator']

    if('aircons' in coordinator.data):
        entities = []
        for _, acx in enumerate(coordinator.data['aircons']):
            for _, zx in enumerate(coordinator.data['aircons'][acx]['zones']):
                if('value' in coordinator.data['aircons'][acx]['zones'][zx]):
                    entities.append(MyAirZoneDamper(hass, acx, zx))
        async_add_entities(entities)
    return True
             

class MyAirZoneDamper(CoverEntity):

    def __init__(self, hass, acx, zx):
        self.coordinator = hass.data[DOMAIN]['coordinator']
        self.async_set_data = hass.data[DOMAIN]['async_set_data']
        self.device = hass.data[DOMAIN]['device']
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['name']} Duct"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}-vent"

    @property
    def device_class(self):
        return DEVICE_CLASS_DAMPER

    @property
    def supported_features(self):
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION

    @property
    def is_closed(self):
        return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == MYAIR_ZONE_CLOSE

    @property
    def is_opening(self):
        return False

    @property
    def is_closing(self):
        return False

    @property
    def current_cover_position(self):
        if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == MYAIR_ZONE_OPEN):
            return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['value']
        else:
            return 0

    @property
    def icon(self):
        return ["mdi:fan-off","mdi:fan"][self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == MYAIR_ZONE_OPEN]

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return self.device

    async def async_open_cover(self, **kwargs):
        await self.async_set_data({self.acx:{"zones":{self.zx:{"state":MYAIR_ZONE_OPEN, "value": 100}}}})
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs):
        await self.async_set_data({self.acx:{"zones":{self.zx:{"state":MYAIR_ZONE_CLOSE}}}})
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs):
        position = round(kwargs.get(ATTR_POSITION)/5)*5
        if(position == 0):
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":MYAIR_ZONE_CLOSE}}}})
        else:
            await self.async_set_data({self.acx:{"zones":{self.zx:{"state":MYAIR_ZONE_OPEN, "value": position}}}})

        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()