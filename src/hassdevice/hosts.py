import os
import logging

import paho.mqtt.client as mqtt

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

    def add_device(self, device):
        device.connect(self.mqtt_client, self.discovery_prefix, self.node_id)

    def start(self, block=True):
        if self.mqtt_client is None:
            self.mqtt_client = mqtt.Client(
                client_id=self.mqtt_client_id,
                clean_session=self.mqtt_client_id == ""
            )

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
                    certfile=self.mqtt_tls_certfile
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
            if arg in vargs:
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
                value = open(spath).read().decode('utf-8').strip()
                setattr(self, arg, value)

    @classmethod
    def add_argparse_params(cls, parser):
        parser.add_argument("--mqtt-client-id", default="", required=False)
        parser.add_argument("--mqtt-username", default=None, required=False)
        parser.add_argument("--mqtt-password", default=None, required=False)
        parser.add_argument("--mqtt-host", default="localhost", required=False)
        parser.add_argument("--mqtt-port", default=1883, type=int, required=False)
        parser.add_argument("--mqtt-tls-cacert", default=None, required=False)
        parser.add_argument("--mqtt-tls-certfile", default=None, required=False)
        parser.add_argument("--mqtt-tls-keyfile", default=None, required=False)

        parser.add_argument("--discovery-prefix", default="homeassistant", required=False)
        parser.add_argument("--node-id", default=None, required=False)
