"""Config flow for Powersoft Mezzo integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NAME,
)
from .mezzo_client import discover_amplifiers, MezzoClient

_LOGGER = logging.getLogger(__name__)


class MezzoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Powersoft Mezzo."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.discovered_devices = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - choose between discovery and manual."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["discovery", "manual"],
        )

    async def async_step_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle discovery step."""
        if user_input is not None:
            # User selected a discovered device
            host = user_input[CONF_HOST]

            # Check if already configured
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Verify we can connect
            try:
                client = MezzoClient(host, DEFAULT_PORT, DEFAULT_TIMEOUT)
                await client.connect()
                await client.disconnect()
            except Exception as err:
                _LOGGER.error("Failed to connect to %s: %s", host, err)
                return self.async_abort(reason="cannot_connect")

            return self.async_create_entry(
                title=user_input.get(CONF_NAME, f"Mezzo {host}"),
                data={
                    CONF_HOST: host,
                    CONF_PORT: DEFAULT_PORT,
                },
            )

        # Discover devices
        _LOGGER.info("Starting device discovery...")
        self.discovered_devices = await discover_amplifiers(timeout=5.0)

        if not self.discovered_devices:
            _LOGGER.warning("No devices discovered")
            return self.async_abort(reason="no_devices_found")

        # Build schema with discovered devices
        devices = {
            host: f"{info.get('model', 'Mezzo')} ({host})"
            for host, info in self.discovered_devices.items()
        }

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): vol.In(devices),
                vol.Optional(CONF_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="discovery",
            data_schema=schema,
            description_placeholders={
                "count": str(len(self.discovered_devices))
            },
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual configuration step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)

            # Check if already configured
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Try to connect
            try:
                client = MezzoClient(host, port, DEFAULT_TIMEOUT)
                await client.connect()
                await client.disconnect()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, f"Mezzo {host}"),
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                    },
                )
            except TimeoutError:
                _LOGGER.error("Timeout connecting to %s:%d", host, port)
                errors["base"] = "timeout"
            except ConnectionError as err:
                _LOGGER.error("Connection error to %s:%d: %s", host, port, err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected error connecting to %s:%d: %s", host, port, err)
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="manual",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return MezzoOptionsFlow(config_entry)


class MezzoOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Powersoft Mezzo."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_TIMEOUT,
                    default=self.config_entry.options.get(
                        CONF_TIMEOUT, DEFAULT_TIMEOUT
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=10.0)),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
