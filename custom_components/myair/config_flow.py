import logging
from aiohttp import request, ClientError

from .const import *
from homeassistant import config_entries
from homeassistant.core import callback


_LOGGER = logging.getLogger(__name__)

class MyAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, info):
        _LOGGER.info("MyAir Config Flow")
        if not info:
            _LOGGER.info("MyAir Form")
            return self._show_form()
        
        host = info.get(CONF_HOST)
        port = info.get(CONF_PORT)
        ssl = info.get(CONF_SSL)

        if ssl:
            url = f"https://{host}:{port}"
        else:
            url = f"http://{host}:{port}"

        try:
            async with request('GET', f"{url}/getSystemData") as resp:
                assert resp.status == 200
                data = await resp.json(content_type=None)
        except ClientError as err:
            _LOGGER.error(f"Unable to connect to MyAir: {err}")
            return self._show_form({"base": "connection_error"})

        if('aircons' not in data):
            return self._show_form({"base": "connection_error"})

        return self.async_create_entry(
            title=data['system']['name'],
            data=info,
        )


    @callback
    def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema = MYAIR_SCHEMA,
            errors=errors if errors else {},
            description_placeholders={
                CONF_HOST:'MyAir Tablet IP Address',
                CONF_PORT:'MyAir Tablet API Port',
                CONF_SSL:'SSL',
            }
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)