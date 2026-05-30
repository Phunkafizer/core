"""Common fixtures for Pilota Casa tests."""

import pytest

from homeassistant.components.pilota_casa.const import (
    CONF_CHANNEL,
    CONF_DEVICE_ID,
    CONF_GROUP,
    CONF_TRANSMITTER,
    DOMAIN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry
from tests.components.radio_frequency.common import MockRadioFrequencyEntity

TRANSMITTER_ENTITY_ID = "radio_frequency.test_rf_transmitter"


@pytest.fixture
def mock_config_entry(
    hass: HomeAssistant,
    mock_rf_entity: MockRadioFrequencyEntity,
) -> MockConfigEntry:
    """Return a mock config entry for Pilota Casa setup."""
    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(TRANSMITTER_ENTITY_ID)
    assert entity_entry is not None

    return MockConfigEntry(
        domain=DOMAIN,
        title="Pilota Casa ID 4660 G 1 CH 1",
        data={
            CONF_TRANSMITTER: TRANSMITTER_ENTITY_ID,
            CONF_DEVICE_ID: 4660,
            CONF_GROUP: 1,
            CONF_CHANNEL: 1,
        },
        unique_id=f"{entity_entry.id}_4660_1_1",
    )


@pytest.fixture
async def init_pilota_casa(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """Set up Pilota Casa integration."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
