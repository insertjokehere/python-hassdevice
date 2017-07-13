import pytest
from unittest import mock

import hassdevice
import hassdevice.devices
import hassdevice.hosts


class FakeMessage:
    def __init__(self, payload):
        self.payload = payload.encode('utf-8')


def test_switch_base_topic():
    with pytest.raises(ValueError):
        switch1 = hassdevice.devices.Switch("foo", "bar")
        switch1.base_topic

    switch2 = hassdevice.devices.Switch("foo", "bar")
    switch2.discovery_prefix = "homeassistant"
    assert switch2.base_topic == "homeassistant/switch/bar"

    switch3 = hassdevice.devices.Switch("foo", "bar")
    switch3.discovery_prefix = "homeassistant"
    switch3.node_id = "testserver"
    assert switch3.base_topic == "homeassistant/switch/testserver/bar"


@mock.patch('hassdevice.devices.Switch.on_state_change')
def test_state_change(mock_state_change):
    sw = hassdevice.devices.Switch("foo", "bar")
    sw._state = sw.payload_on
    sw._on_command(None, None, FakeMessage(sw.payload_off))
    assert mock_state_change.call_count == 1


@mock.patch('hassdevice.devices.Switch.on_state_change')
def test_state_change_no_update(mock_state_change):
    sw = hassdevice.devices.Switch("foo", "bar")
    sw._state = sw.payload_off
    sw._on_command(None, None, FakeMessage(sw.payload_off))
    assert mock_state_change.call_count == 0
