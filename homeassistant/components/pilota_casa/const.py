"""Constants and helpers for the Pilota Casa integration."""

from typing import Final

DOMAIN: Final = "pilota_casa"

CONF_TRANSMITTER: Final = "transmitter"
CONF_DEVICE_ID: Final = "device_id"
CONF_CHANNEL: Final = "channel"
CONF_GROUP: Final = "group"
REPEAT_COUNT_LEARN: Final = 10
MIN_DEVICE_ID: Final = 0
MAX_DEVICE_ID: Final = 0xFFFF
MIN_GROUP: Final = 1
MAX_GROUP: Final = 4
MIN_CHANNEL: Final = 1
MAX_CHANNEL: Final = 4


def format_device_summary(device_id: int, group: int, channel: int) -> str:
    """Return a concise summary string for the configured device."""
    return f"ID {device_id} G {group} CH {channel}"
