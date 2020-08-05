from .const import (
    DOMAIN,
)

from homeassistant.components.binary_sensor import BinarySensorEntity, DEVICE_CLASS_MOTION

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up MyAir motion platform."""
    
    coordinator = hass.data[DOMAIN]['coordinator']

    if(coordinator.data):
        entities = []
        for _, acx in enumerate(coordinator.data):
            for _, zx in enumerate(coordinator.data[acx]['zones']):
                if('motion' in coordinator.data[acx]['zones'][zx]):
                    entities.append(MyAirZoneMotion(coordinator, acx, zx))
        async_add_entities(entities)
             

class MyAirZoneMotion(BinarySensorEntity):

    def __init__(self, coordinator, acx, zx):
        self.coordinator = coordinator
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return f"{self.coordinator.data[self.acx]['zones'][self.zx]['name']} Motion"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}-motion"

    @property
    def device_class(self):
        return DEVICE_CLASS_MOTION 

    @property
    def is_on(self):
        return self.coordinator.data[self.acx]['zones'][self.zx]['motion']

    @property
    def device_state_attributes(self):
        return {'motionConfig': self.coordinator.data[self.acx]['zones'][self.zx]['motionConfig']}

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

    async def async_update(self):
        await self.coordinator.async_request_refresh()