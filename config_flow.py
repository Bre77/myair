from homeassistant import config_entries
from .const import DOMAIN

import voluptuous as vol

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_host(self, info):
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="host", data_schema=vol.Schema({vol.Required("host"): str})
        )