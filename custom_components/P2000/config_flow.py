from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_PROVINCIE, CONF_DISCIPLINES

PROVINCES = [
    "All",
    "Groningen",
    "Friesland",
    "Drenthe",
    "Overijssel",
    "Flevoland",
    "Gelderland",
    "Utrecht",
    "Noord-Holland",
    "Zuid-Holland",
    "Zeeland",
    "Noord-Brabant",
    "Limburg"]

DISCIPLINES = [
    "brandweer",
    "politie",
    "ambulance"
    ]

class P2000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for P2000."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="P2000-online.net", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_PROVINCIE): vol.In(PROVINCES),
            vol.Required(CONF_DISCIPLINES): vol.All(
                vol.Length(min=5), vol.In(DISCIPLINES)
            ),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
