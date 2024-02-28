import pytest

from src.logger import SDVLogger
from src.helpers.customize_marks import SDVMarks
from src.enums.marks import Type, Priority, Suite, Tasks, FrameworkSpecific
import time


LOGGER = SDVLogger.get_logger(f"test-{Suite.OTA_UPDATER}")


tc_test_data = [
    # pytest.param('203647640528.dkr.ecr.eu-west-1.amazonaws.com/raspberry-demo', id="SDV-125 Positive int temp"), 403
    # pytest.param('s3://raspberry-demo-build-artifacts/raspberry-demo/package/raspberry-demo-6d032f157281f9a60ef85810e065665a6697a024.tar', id="SDV-125 Positive int temp"), Error response from daemon: 404 page not found
    pytest.param('https://raspberry-demo-build-artifacts.s3.eu-west-1.amazonaws.com/raspberry-demo/package/raspberry-demo-6d032f157281f9a60ef85810e065665a6697a024.tar?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAS62SYMPIIGYCFGWD%2F20230705%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Date=20230705T134019Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=6c330ae627455683769a709084cc31697168945a88d98a02105af104c25b3e4a', id="SDV-128 OTA updater"),
]

@SDVMarks.link(Tasks.TASK_127)
@SDVMarks.add(Type.INTEGRATION, Priority.P1, Suite.OTA_UPDATER)
@pytest.mark.parametrize("url", tc_test_data)
def test_ota_positive(iot_bridge_ota_iot_thing, url):
    ota_service, iot_bridge_service, iot_thing = iot_bridge_ota_iot_thing

    update_qr = ota_service.config.source_conf["update_topic"]
    
    iot_thing.subscribe_to_topic(update_qr)
    signed_url = iot_thing.get_ota_service_test_package()
    msg_to_send = {"bucketUrl": signed_url}
    iot_thing.publish_message(update_qr, msg_to_send)

    msg = f'Download image: download url {url}'
    assert ota_service.expects_log_message(msg, timeout=10)
    
    msg = 'Download image: done.'
    assert ota_service.expects_log_message(msg, timeout=10)

    msg = "[updater] Updating running docker container"
    assert ota_service.expects_log_message(msg, timeout=10)
