"""Config flow for Petlibro integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_REGION, CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .api import PetLibroAPI
from .exceptions import PetLibroCannotConnect, PetLibroInvalidAuth

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REGION): vol.In(["US"]),
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str
    }
)


class PetlibroConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Petlibro."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self._validate_input(user_input)
            except PetLibroCannotConnect:
                errors["base"] = "cannot_connect"
            except PetLibroInvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=user_input[CONF_EMAIL], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _validate_input(self, data: dict[str, Any]):
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """
        api = PetLibroAPI(async_get_clientsession(self.hass), self.hass.config.time_zone, data[CONF_REGION])

        await api.login(data[CONF_EMAIL], data[CONF_PASSWORD])
