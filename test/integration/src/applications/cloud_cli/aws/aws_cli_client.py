import json
import os
import subprocess
import time
import uuid

import boto3
from botocore import client
from awscrt import mqtt
from src.applications.cloud_cli.aws import mqtt_connection_builder
from src.applications.cloud_cli.base_cloud_client import BaseCloudClient
from src.config.config import CONFIG
from src.helpers.helpers import extract_from_dictionary
from src.logger import SDVLogger

LOGGER = SDVLogger.get_logger("AWS_CLIENT")


class AWSCliClient(BaseCloudClient):
    THING_TYPE = "base-platform-client"
    THING_GROUP_ARN = "arn:aws:iot:eu-west-1:203647640528:thinggroup/model_alpha"
    THING_POLICY_NAME = "iot_upload_file"
    ENDPOINT = "a2vups147zkgmn-ats.iot.eu-west-1.amazonaws.com"

    def __init__(self) -> None:
        super().__init__()
        self.thing = None
        self.certs = None
        self.certs_folder = None
        self.mqtt_client_id = str(uuid.uuid4())
        self.mqtt_connection = None
        self.mqtt_message_loop = {}
        self.cli_client = boto3.client("iot")
        self.s3_client = boto3.client("s3", config=client.Config(signature_version='s3v4'))

    @property
    def thing_name(self):
        return self.thing["thingName"]

    @staticmethod
    def ecr_login():
        LOGGER.info("Performing docker loging")
        cmd = f"aws ecr get-login-password --region {CONFIG.AWS_REGION} | docker login --username AWS --password-stdin {CONFIG.Account_ID}.dkr.ecr.{CONFIG.AWS_REGION}.amazonaws.com"
        LOGGER.info(f"Trying to loging with {cmd} command")
        raw_output = subprocess.run(
            args=cmd, check=True, capture_output=True, shell=True
        )
        LOGGER.info(f"Raw output: {raw_output}")

    def init_cli(self):
        LOGGER.info("Initializing AWS CLI ")
        self.ecr_login()
        return self


    def tear_up_thing(self, name):
        LOGGER.info("IOT Thing tear up")

        self.create_thing(
            name
        ).add_thing_to_group().create_certs().attach_policy_to_cert().attach_cert_to_thing().generate_certs_files(
            CONFIG.IOTBRIDGE_AWS_CERTS_FOLDER
        )
        return self

    def tear_down_thing(self):
        LOGGER.info("IOT Thing tear down")

        self.detach_policy_from_cert().detach_cert_from_thing().delete_certs().delete_thing()
        return self

    def create_thing(self, name):
        LOGGER.info(f"Creating thing with '{name}' name")
        self.thing = self.cli_client.create_thing(
            thingName=name,
            thingTypeName=self.THING_TYPE,
        )
        LOGGER.info(f"'{self.thing['thingName']}' thing created")

        return self

    def add_thing_to_group(self):
        LOGGER.info(
            f"Adding thing '{self.thing['thingName']}' to a '{AWSCliClient.THING_GROUP_ARN}' group"
        )
        self.cli_client.add_thing_to_thing_group(
            thingGroupArn=AWSCliClient.THING_GROUP_ARN,
            thingName=self.thing["thingName"],
        )
        return self

    def delete_thing(self):
        LOGGER.info(f"Deletting thing '{self.thing['thingName']}'")

        self.cli_client.delete_thing(
            thingName=self.thing["thingName"],
        )
        self.thing = None

        return self

    def create_certs(self):
        LOGGER.info("Creating certificates")

        self.certs = self.cli_client.create_keys_and_certificate(setAsActive=True)
        LOGGER.info(f"Certificates created. Payload {self.certs}")

        return self

    def delete_certs(self):
        LOGGER.info("Trying to remove certs")

        LOGGER.info(f"Set state to INACTIVE for cert '{self.certs['certificateId']}'")
        self.cli_client.update_certificate(
            certificateId=self.certs["certificateId"], newStatus="INACTIVE"
        )

        LOGGER.info(f"Removing cert '{self.certs['certificateId']}'")
        self.cli_client.delete_certificate(
            certificateId=self.certs["certificateId"], forceDelete=False
        )
        self.certs = None

        return self

    def generate_certs_files(self, path_prefix):
        LOGGER.info(f"Creating certificates files in folder {path_prefix}")

        if self.certs is None:
            raise Exception(
                "Cannot generate certificates because they are not generated. Create them first"
            )

        certs_to_generate = {
            "certificate.pem.crt": ["certificatePem"],
            "private.pem.key": ["keyPair", "PrivateKey"],
        }

        if not os.path.exists(path_prefix):
            os.makedirs(path_prefix)

        for cert_name, dict_path in certs_to_generate.items():
            content = extract_from_dictionary(self.certs, dict_path)
            path = os.path.join(path_prefix, cert_name)

            f = open(path, "w")
            f.write(content)
            f.close()
            LOGGER.info(f"File {path} created")

        self.certs_folder = os.path.abspath(path_prefix)

        return self

    def attach_policy_to_cert(self):
        LOGGER.info(
            f"Attach policy '{AWSCliClient.THING_GROUP_ARN}' to a cert {self.certs['certificateArn']}"
        )
        self.cli_client.attach_policy(
            policyName=AWSCliClient.THING_POLICY_NAME,
            target=self.certs["certificateArn"],
        )

        return self

    def detach_policy_from_cert(self):
        LOGGER.info(
            f"Detach policy '{AWSCliClient.THING_POLICY_NAME}' from  a cert'{self.certs['certificateArn']}'"
        )
        self.cli_client.detach_policy(
            policyName=AWSCliClient.THING_POLICY_NAME,
            target=self.certs["certificateArn"],
        )

        return self

    def attach_cert_to_thing(self):
        LOGGER.info(
            f"Attach cert '{self.certs['certificateArn']}' to a thing {self.thing['thingName']}"
        )
        self.cli_client.attach_thing_principal(
            thingName=self.thing["thingName"], principal=self.certs["certificateArn"]
        )

        return self

    def detach_cert_from_thing(self):
        LOGGER.info(
            f"Detach cert '{self.certs['certificateArn']}' from a thing {self.thing['thingName']}"
        )
        self.cli_client.detach_thing_principal(
            thingName=self.thing["thingName"], principal=self.certs["certificateArn"]
        )

        return self

    def get_ota_service_test_package(self):
        target_s3_link = 'raspberry-demo docker build'
        LOGGER.info(f"Get signed url for '{target_s3_link}'")
        target_http_link = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'raspberry-demo-build-artifacts',
                'Key': 'raspberry-demo/package/raspberry-demo-6d032f157281f9a60ef85810e065665a6697a024.tar'
            },
            ExpiresIn=3600)

        return target_http_link

    def connect_to_message_bus(self):
        # Callback when connection is accidentally lost.
        def on_connection_interrupted(connection, error, **kwargs):
            LOGGER.error("Connection interrupted. error: {}".format(error))

        try:
            LOGGER.info(
                f"Connecting to AWS IOT MQTT endpoint '{AWSCliClient.ENDPOINT}' with Client Id '{self.mqtt_client_id}'"
            )
            self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=AWSCliClient.ENDPOINT,
                cert_filepath=os.path.join(self.certs_folder, "certificate.pem.crt"),
                pri_key_filepath=os.path.join(self.certs_folder, "private.pem.key"),
                client_id=self.mqtt_client_id,
                on_connection_interrupted=on_connection_interrupted,
            )

            connect_future = self.mqtt_connection.connect()
            # Future.result() waits until a result is available
            connect_future.result()
            LOGGER.info("Connected!")
        except Exception as e:
            LOGGER.exception(e)

        return self

    def subscribe_to_topic(self, message_topic):
        def on_message_received(topic, payload, dup, qos, retain, **kwargs):
            try:
                payload = payload.decode('utf-8')
                LOGGER.info(
                    "Received message from topic '{}': {}".format(topic, payload)
                )

                if self.mqtt_message_loop.get(topic) is None:
                    self.mqtt_message_loop[topic] = []

                self.mqtt_message_loop[topic].append(payload)
            except Exception as e:
                LOGGER.exception(e)

        try:
            LOGGER.info(f"Subscribing to topic '{message_topic}'...")
            subscribe_future, _ = self.mqtt_connection.subscribe(
                topic=message_topic,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=on_message_received,
            )

            subscribe_result = subscribe_future.result()
            self.mqtt_message_loop[message_topic] = []
            LOGGER.info(f"Subscribed with {str(subscribe_result['qos'])}")
        except Exception as e:
            LOGGER.exception(e)

        return self

    def list_messages(self):
        return self.mqtt_message_loop

    def publish_message(self, message_topic, message, repeat=1):
        try:
            LOGGER.info(f"Publishing message to topic '{message_topic}': {message}")
            message_json = json.dumps(message)
            for _ in range(repeat):
                self.mqtt_connection.publish(
                    topic=message_topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE
                )
                LOGGER.info("Message sent")
        except Exception as e:
            LOGGER.exception(e)

    def expects_message(self, topic, message, strict=False, timeout=10):
        message = str(message)

        if strict is False:
            message = self.convert_to_non_strict_message(message)
        
        timeout = time.time() + timeout
        while time.time() < timeout:
            msgs = self.mqtt_message_loop.get(topic)
            if msgs is None or len(msgs) == 0:
                LOGGER.info(f"No messages in topic '{topic}'. Waiting for messages")
                time.sleep(1)
                continue

            for msg in msgs:
                if strict is False:
                    msg = self.convert_to_non_strict_message(msg)

                    LOGGER.info(message)
                    LOGGER.info(msg)
                    if message in msg:
                        LOGGER.info(f"Message '{message}' retrieved")
                        return message
                else: 
                    if message == msg:
                        LOGGER.info(f"Message '{message}' retrieved")
                        return message
            time.sleep(1)

        # raise TimeoutError(f"Timeout limit reached. No '{message}' message retrived")
        LOGGER.error(f"Timeout limit reached. No '{message}' message retrived")

    def terminate(self):
        try:
            LOGGER.info("Disconecting from AWS IOT")
            disconnect_future = self.mqtt_connection.disconnect()
            disconnect_future.result()
            LOGGER.info("Disconnected!")
        except Exception as e:
            LOGGER.exception(e)
