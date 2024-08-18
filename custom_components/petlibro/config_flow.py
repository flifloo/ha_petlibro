"""Config flow for Petlibro integration."""

from __future__ import annotations

import logging
from typing import Any, Mapping

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_REGION, CONF_EMAIL, CONF_PASSWORD, CONF_API_TOKEN
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

    token: str
    email: str
    region: str

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match({CONF_EMAIL: user_input[CONF_EMAIL]})

            if not (error := await self._validate_input(user_input)):
                return self.async_create_entry(title=user_input[CONF_EMAIL], data={
                    CONF_REGION: user_input[CONF_REGION],
                    CONF_EMAIL: user_input[CONF_EMAIL],
                    CONF_API_TOKEN: self.token
                })

            errors["base"] = error

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        """Handle a reauthorization flow request."""
        self.email = entry_data[CONF_EMAIL]
        self.region = entry_data[CONF_REGION]
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Handle user's reauth credentials."""
        errors = {}
        if user_input:
            entry_id = self.context["entry_id"]
            if entry := self.hass.config_entries.async_get_entry(entry_id):
                user_input = user_input | {CONF_EMAIL: self.email, CONF_REGION: self.region}
                if not (error := await self._validate_input(user_input)):
                    self.hass.config_entries.async_update_entry(
                        entry,
                        data={
                            CONF_EMAIL: self.email,
                            CONF_REGION: self.region,
                            CONF_API_TOKEN: self.token
                            },
                    )
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    return self.async_abort(reason="reauth_successful")

                errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            description_placeholders={CONF_EMAIL: self.email, CONF_REGION: self.region},
            errors=errors,
        )

    async def _validate_input(self, data: dict[str, Any]) -> str:
        """Validate the user input allows us to connect.

        Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
        """
        try:
            api = PetLibroAPI(async_get_clientsession(self.hass), self.hass.config.time_zone, data[CONF_REGION])
            self.token = await api.login(data[CONF_EMAIL], data[CONF_PASSWORD])
        except PetLibroCannotConnect:
            return "cannot_connect"
        except PetLibroInvalidAuth:
            return "invalid_auth"
        except Exception as e:
            _LOGGER.exception("Unexpected exception: %s", e)
            return "unknown"
        return ""
