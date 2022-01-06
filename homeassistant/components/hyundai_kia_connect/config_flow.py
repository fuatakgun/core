"""Config flow for Hyundai / Kia Connect integration."""
from __future__ import annotations

import hashlib
import logging
from typing import Any

from hyundai_kia_connect_api import Token, VehicleManager
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_REGION, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import BRANDS, CONF_BRAND, DEFAULT_PIN, DOMAIN, REGIONS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_PIN, default=DEFAULT_PIN): str,
        vol.Required(CONF_REGION): vol.In(REGIONS),
        vol.Required(CONF_BRAND): vol.In(BRANDS),
    }
)


async def validate_input(hass: HomeAssistant, user_input: dict[str, Any]) -> Token:
    """Validate the user input allows us to connect."""
    api = VehicleManager.get_implementation_by_region_brand(
        user_input[CONF_REGION],
        user_input[CONF_BRAND],
    )
    token: Token = await hass.async_add_executor_job(
        api.login, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
    )

    if token is None:
        raise InvalidAuth

    return token


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hyundai / Kia Connect Bluelink."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            title = f"{BRANDS[user_input[CONF_BRAND]]} {REGIONS[user_input[CONF_REGION]]} {user_input[CONF_USERNAME]}"
            await self.async_set_unique_id(
                hashlib.sha256(title.encode("utf-8")).hexdigest()
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
