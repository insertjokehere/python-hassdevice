import os
import logging
import ssl
import paho.mqtt.client as mqtt

try:
    TLS_VERSION = ssl.PROTOCOL_TLS
except AttributeError:
    TLS_VERSION = ssl.PROTOCOL_TLSv1

logger = logging.getLogger(__name__)


class SimpleMQTTHost:

    CONFIGURABLE_OPTIONS = [
        "mqtt_client_id",
        "mqtt_username",
        "mqtt_password",
        "mqtt_host",
        "mqtt_port",
        "mqtt_tls_cacert",
        "mqtt_tls_certfile",
        "mqtt_tls_keyfile",
        "discovery_prefix",
        "node_id"
    ]

    def __init__(self):
        self.mqtt_client = None
        self.discovery_prefix = "homeassistant"
        self.node_id = None

        self.mqtt_client_id = ""

        self.mqtt_username = None
        self.mqtt_password = None

        self.mqtt_host = "localhost"
        self.mqtt_port = 1883

        self.mqtt_tls_cacert = None
        self.mqtt_tls_certfile = None
        self.mqtt_tls_keyfile = None

        self._connected = False
        self._pending_devices = []

    def add_device(self, device):
        if self._connected:
            device.connect(self.mqtt_client, self.discovery_prefix, self.node_id)
        else:
            self._pending_devices.append(device)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            while len(self._pending_devices) > 0 and self._connected:
                device = self._pending_devices.pop()
                self.add_device(device)
        else:
            logger.warning("Connection error: {}".format(rc))

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False

    def start(self, block=True):
        if self.mqtt_client is None:
            self.mqtt_client = mqtt.Client(
                client_id=self.mqtt_client_id,
                clean_session=self.mqtt_client_id == ""
            )

            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect

            if self.mqtt_username is not None:
                self.mqtt_client.username_pw_set(
                    self.mqtt_username, self.mqtt_password
                )

            if self.mqtt_tls_cacert is None and self.mqtt_tls_certfile is not None:
                logger.warning("mqtt_tls_cacert not set, ignoring mqtt_tls_certfile setting")
            elif self.mqtt_tls_cacert is not None:
                self.mqtt_client.tls_set(
                    ca_certs=self.mqtt_tls_cacert,
                    keyfile=self.mqtt_tls_keyfile,
                    certfile=self.mqtt_tls_certfile,
                    tls_version=TLS_VERSION
                )

        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port)

        if block:
            self.mqtt_client.loop_forever()
        else:
            self.mqtt_client.loop_start()

    def stop(self):
        if self.mqtt_client is not None:
            self.mqtt_client.loop_stop()

    def configure_from_args(self, args):
        vargs = vars(args)
        for arg in self.CONFIGURABLE_OPTIONS:
            if arg in vargs and vargs[arg] is not None:
                setattr(self, arg, vargs[arg])

    def configure_from_env(self, prefix=""):
        for arg in self.CONFIGURABLE_OPTIONS:
            arg = prefix + arg.upper()
            if arg in os.environ:
                setattr(self, arg, os.environ[arg])

    def configure_from_docker_secrets(self):
        for arg in self.CONFIGURABLE_OPTIONS:
            spath = os.path.join('/run/secrets', arg)
            if os.path.exists(spath):
                value = open(spath).read().strip()
                setattr(self, arg, value)

    @classmethod
    def add_argparse_params(cls, parser):
        parser.add_argument("--mqtt-client-id", default=None, required=False)
        parser.add_argument("--mqtt-username", default=None, required=False)
        parser.add_argument("--mqtt-password", default=None, required=False)
        parser.add_argument("--mqtt-host", default=None, required=False)
        parser.add_argument("--mqtt-port", default=None, type=int, required=False)
        parser.add_argument("--mqtt-tls-cacert", default=None, required=False)
        parser.add_argument("--mqtt-tls-certfile", default=None, required=False)
        parser.add_argument("--mqtt-tls-keyfile", default=None, required=False)

        parser.add_argument("--discovery-prefix", default=None, required=False)
        parser.add_argument("--node-id", default=None, required=False)
