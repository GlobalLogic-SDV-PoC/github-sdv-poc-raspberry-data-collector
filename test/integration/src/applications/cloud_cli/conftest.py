import uuid

import pytest
from src.applications.cloud_cli.cloud_provider import CloudProvider
from src.config.config import CONFIG


@pytest.fixture(scope="session")
def iot_thing():
    client = CloudProvider.get_provider(CONFIG.CLOUD_PROVIDER)
    client = client()

    thing_name = f"auto_test_{uuid.uuid4()}"

    client.init_cli().tear_up_thing(thing_name).connect_to_message_bus()

    yield client

    client.tear_down_thing().terminate()
