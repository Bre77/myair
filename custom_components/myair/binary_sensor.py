from .const import DOMAIN

from homeassistant.components.binary_sensor import BinarySensorEntity, DEVICE_CLASS_MOTION

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MyAir motion platform."""
    
    my = hass.data[DOMAIN][config_entry.data.get('url')]


    if('aircons' in my.coordinator.data):
        entities = []
        for _, acx in enumerate(my.coordinator.data['aircons']):
            for _, zx in enumerate(my.coordinator.data['aircons'][acx]['zones']):
                # Only add motion sensor when motion is enabled
                if(my.coordinator.data['aircons'][acx]['zones'][zx]['motionConfig'] == 0):
                    entities.append(MyAirZoneMotion(my, acx, zx))
        async_add_entities(entities)
    return True
             

class MyAirZoneMotion(BinarySensorEntity):

    def __init__(self, my, acx, zx):
        self.extend(my)
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['name']} Motion"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}-motion"

    @property
    def device_class(self):
        return DEVICE_CLASS_MOTION 

    @property
    def is_on(self):
        return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['motion']

    @property
    def device_state_attributes(self):
        return {'motionConfig': self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['motionConfig']}

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

    async def async_update(self):
        await self.coordinator.async_request_refresh()