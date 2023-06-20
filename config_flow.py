from homeassistant import config_entries
from .const import DOMAIN


class ApartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
     async def async_step_user(self, info):
        data_schema = {
            vol.Required("URL"): str,
        }

        if info is not None:
            self.data = info
            return self.async_create_entry(
                title="Title of the entry",
                data={
                    "url": user_input["URL"]
            },
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema)
        )