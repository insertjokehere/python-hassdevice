import json
import logging
import functools

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseDevice:

    def __init__(self, name, entity_id):
        """
        :param name: The display name to use in HomeAssistant
        :param entity_id: The entity_id to use in HomeAssistant
        """
        self.name = name
        self.entity_id = entity_id

        self.discovery_prefix = None
        self.node_id = None
        self.client = None

        self._state_values = {}
        self._state_topics = {}
        self._command_topics = {}

    @property
    def component(self):
        raise NotImplemented

    @property
    def _config(self):
        return {
            'name': self.name,
            'retain': self.retain
        }

    @property
    def config(self):
        cfg = self._config
        cfg.update(self.base_config)
        return cfg

    def add_state(self, name, state_topic=None, state_topic_key=None, command_topic=None, command_topic_key=None):
        """
        Adds a new state handler for the device.

        If state_topic and state_topic_key are not None:
        * Advertise state_topic in the device topic as state_topic_key
        * Add get_<name> function to the instance, that will return the current
          value of the state
        * Add set_<name> function to the instance, that will publish a new value
          to the broker

        If command_topic and command_topic_key are not None:
        * Will subscribe to command_topic
        * You should override on_<name>_change, will be called when a command is recieved
        """
        self._state_values[name] = None

        if state_topic is not None and state_topic_key is not None:
            self._state_topics[name] = state_topic
            setattr(self, "get_" + name, functools.partial(self._get_state, name))
            setattr(self, "set_" + name, functools.partial(self._set_state, name))

        if command_topic is not None and command_topic_key is not None:
            self._command_topics[name] = command_topic
            self._config[command_topic_key] = command_topic

    def _set_state(self, state_name, value):
        self._state_values[state_name] = value
        logger.debug("publishing {} to {}".format(
            value,
            self._state_topics[state_name]
        ))
        self.client.publish(
            self._state_topics[state_name],
            value,
            retain=self.retain
        )

    def _get_state(self, state_name):
        return self._state_values[state_name]

    def _expand_topic(self, topic):
        return '/'.join([self.base_topic, topic])

    @property
    def base_topic(self):
        if self.discovery_prefix is None:
            raise ValueError("Must call .connect() first")

        path = filter(lambda x: x is not None, [self.discovery_prefix, self.component, self.node_id, self.entity_id])
        return "/".join(path)

    @property
    def config_topic(self):
        return "/".join([self.base_topic, "config"])

    @property
    def retain(self):
        """
        Should the messages sent to the broker have the 'retain' flag set. Defaults to ``True``
        """
        return True

    def connect(self, mqtt_client, discovery_prefix="homeassistant", node_id=None):
        """
        Connect this device to an MQTT broker

        :param mqtt_client: A connected MQTT client
        :param discovery_prefix: The discovery prefix set in the HomeAssistant config
        :param node_id: Will be included in the MQTT topics if set
        """
        self.discovery_prefix = discovery_prefix
        self.node_id = node_id
        self.client = mqtt_client

        for name, topic in self._state_topics.items():
            self._config[name] = self._expand_topic(topic)

        for name, topic in self._command_topics.items():
            t = self._expand_topic(topic)
            self._config[name] = t
            self.client.message_callback_add(t, functools.partial(self._on_command, name))
            self.client.subscribe(t)

        self.client.publish(self.config_topic, json.dumps(self.config), retain=self.retain)
        logger.debug("Connected to broker, sent config {} to {}".format(
            self.config,
            self.config_topic
        ))

        self.on_connect()

    def on_connect(self):
        return

    def _on_command(self, state_name, client, userdata, message):
        new_state = message.payload.decode('utf-8')
        logger.debug("Got command for new state {} {}, current state {}".format(new_state, state_name, self._state_values[state_name]))

        if hasattr(self, 'is_valid_{}'.format(state_name)):
            is_valid = getattr(self, 'is_valid_{}'.format(state_name))
        else:
            is_valid = lambda x: True

        if hasattr(self, "on_{}_change".format(state_name)):
            on_change = hasattr(self, "on_{}_change".format(state_name))
        else:
            on_change = lambda x: None

        if new_state != self._state_values[state_name] and is_valid(new_state):
            on_change(new_state)
            self._state_values[state_name] = new_state


class Switch(BaseDevice):
    """
    An MQTT switch
    """

    def on_connect(self):
        self.add_state(
            "state",
            self.state_topic, "state_topic",
            self.command_topic, "command_topic"
        )

    @property
    def component(self):
        return "switch"

    @property
    def base_config(self):
        return {
            'payload_on': self.payload_on,
            'payload_off': self.payload_off
        }

    def is_valid_state(self, state):
        return state in [self.payload_on, self.payload_off]

    def on_state_change(self, new_state):
        """
        Called when a state update request is recieved from the broker

        :param new_state: The state to set
        """
        return

    @property
    def state_topic(self):
        return "/".join([self.base_topic, "state"])

    @property
    def command_topic(self):
        return "/".join([self.base_topic, "command"])

    @property
    def payload_on(self):
        """
        Payload to use to indicate the switch is on. Defaults to ``"ON"``
        """
        return "ON"

    @property
    def payload_off(self):
        """
        Payload to use to indicate the switch is off. Defaults to ``"OFF"``
        """
        return "OFF"


class Sensor(BaseDevice):
    """
    An MQTT sensor
    """

    def on_connect(self):
        self.add_state(
            "state",
            self.state_topic, "state_topic"
        )

    @property
    def component(self):
        return "sensor"

    @property
    def state_topic(self):
        return "/".join([self.base_topic, "state"])


class BinarySensor(Sensor):

    def __init__(self, name, entity_id, device_class="none"):
        super().__init__(name, entity_id)
        self.device_class = device_class

    @property
    def component(self):
        return "binary_sensor"

    @property
    def payload_on(self):
        """
        Payload to use to indicate the switch is on. Defaults to ``"ON"``
        """
        return "ON"

    @property
    def payload_off(self):
        """
        Payload to use to indicate the switch is off. Defaults to ``"OFF"``
        """
        return "OFF"

    @property
    def base_config(self):
        return {
            'payload_on': self.payload_on,
            'payload_off': self.payload_off,
            'device_class': self.device_class
        }

    def is_valid_state(self, state):
        return state in [self.payload_on, self.payload_off]
