"""Config flow for the Pilota Casa integration."""

from typing import Any

from rf_protocols.commands import ModulationType
from rf_protocols.commands.pilota_casa import PilotaCasaCommand
import voluptuous as vol

from homeassistant.components.radio_frequency import (
    async_get_transmitters,
    async_send_command,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er, selector

from .const import (
    CONF_CHANNEL,
    CONF_DEVICE_ID,
    CONF_GROUP,
    CONF_TRANSMITTER,
    DOMAIN,
    MAX_CHANNEL,
    MAX_DEVICE_ID,
    MAX_GROUP,
    MIN_CHANNEL,
    MIN_DEVICE_ID,
    MIN_GROUP,
    REPEAT_COUNT_LEARN,
)

_SAMPLE_COMMAND = PilotaCasaCommand(id=1, group=1, channel=1, on=True)
_CONF_DEVICE_RESPONDED = "device_responded"


class PilotaCasaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pilota Casa."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._device_data: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle collecting initial setup data."""
        try:
            transmitters = async_get_transmitters(
                self.hass,
                _SAMPLE_COMMAND.frequency,
                ModulationType.OOK,
            )
        except HomeAssistantError:
            return self.async_abort(reason="no_transmitters")

        if not transmitters:
            return self.async_abort(reason="no_compatible_transmitters")

        if user_input is not None:
            transmitter: str = user_input[CONF_TRANSMITTER]
            device_id: int = user_input[CONF_DEVICE_ID]
            group: int = user_input[CONF_GROUP]
            channel: int = user_input[CONF_CHANNEL]

            if not (MIN_DEVICE_ID <= device_id <= MAX_DEVICE_ID):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._async_user_schema(transmitters, user_input),
                    errors={CONF_DEVICE_ID: "invalid_device_id"},
                )
            if not (MIN_GROUP <= group <= MAX_GROUP):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._async_user_schema(transmitters, user_input),
                    errors={CONF_GROUP: "invalid_group"},
                )
            if not (MIN_CHANNEL <= channel <= MAX_CHANNEL):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._async_user_schema(transmitters, user_input),
                    errors={CONF_CHANNEL: "invalid_channel"},
                )

            registry = er.async_get(self.hass)
            entity_entry = registry.async_get(transmitter)
            assert entity_entry is not None
            await self.async_set_unique_id(
                f"{entity_entry.id}_{device_id}_{group}_{channel}"
            )
            self._abort_if_unique_id_configured()
            self._device_data = {
                CONF_TRANSMITTER: transmitter,
                CONF_DEVICE_ID: device_id,
                CONF_CHANNEL: channel,
                CONF_GROUP: group,
            }
            return await self.async_step_pairing_mode()

        return self.async_show_form(
            step_id="user",
            data_schema=self._async_user_schema(transmitters),
        )

    async def async_step_pairing_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask user to put the target device in pairing mode."""
        if user_input is None:
            return self.async_show_form(
                step_id="pairing_mode",
                data_schema=vol.Schema({}),
            )

        assert self._device_data is not None
        command = PilotaCasaCommand(
            id=self._device_data[CONF_DEVICE_ID],
            group=self._device_data[CONF_GROUP],
            channel=self._device_data[CONF_CHANNEL],
            on=True,
            frame_repeats=REPEAT_COUNT_LEARN,
        )
        await async_send_command(
            self.hass,
            self._device_data[CONF_TRANSMITTER],
            command,
        )
        return await self.async_step_pairing_result()

    async def async_step_pairing_result(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm whether the device responded to the learn command."""
        if user_input is not None:
            if user_input[_CONF_DEVICE_RESPONDED]:
                assert self._device_data is not None
                title = (
                    f"Pilota Casa ID {self._device_data[CONF_DEVICE_ID]} "
                    f"G {self._device_data[CONF_GROUP]} "
                    f"CH {self._device_data[CONF_CHANNEL]}"
                )
                return self.async_create_entry(
                    title=title,
                    data=self._device_data,
                )

            return self.async_show_form(
                step_id="pairing_mode",
                data_schema=vol.Schema({}),
                errors={"base": "no_response"},
            )

        return self.async_show_form(
            step_id="pairing_result",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        _CONF_DEVICE_RESPONDED,
                        default=False,
                    ): selector.BooleanSelector()
                }
            ),
        )

    def _async_user_schema(
        self,
        transmitters: list[str],
        user_input: dict[str, Any] | None = None,
    ) -> vol.Schema:
        """Build the one-step add form schema."""
        if user_input is None:
            user_input = {}

        return vol.Schema(
            {
                vol.Required(
                    CONF_TRANSMITTER,
                    default=user_input.get(CONF_TRANSMITTER, transmitters[0]),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(include_entities=transmitters),
                ),
                vol.Required(
                    CONF_DEVICE_ID,
                    default=user_input.get(CONF_DEVICE_ID, 1),
                ): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Coerce(int),
                ),
                vol.Required(
                    CONF_GROUP,
                    default=user_input.get(CONF_GROUP, 1),
                ): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Coerce(int),
                ),
                vol.Required(
                    CONF_CHANNEL,
                    default=user_input.get(CONF_CHANNEL, 1),
                ): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Coerce(int),
                ),
            }
        )
