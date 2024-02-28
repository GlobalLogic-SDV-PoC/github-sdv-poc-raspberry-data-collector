import pytest

from src.logger import SDVLogger
from src.helpers.customize_marks import SDVMarks
from src.enums.marks import Type, Priority, Suite, Tasks, FrameworkSpecific

LOGGER = SDVLogger.get_logger(f"test-{Suite.DATA_COLLECTOR}")


temp_testdata = [
    pytest.param('temp', 100, id="SDV-125 Positive int temp"),
    pytest.param('temp', 99.99999, id="SDV-125 Positive double temp"),
    pytest.param('temp', 0, id="SDV-125 Zero temp"),
    pytest.param('temp', -1, id="SDV-125 Negative int temp"),
    pytest.param('temp', -11.11111, id="SDV-125 Negative double temp"),
    pytest.param('temp', "NaN", id="SDV-125 NaN temp"),
]

@SDVMarks.link(Tasks.TASK_125)
@SDVMarks.add(Type.INTEGRATION, Priority.P1, Suite.DATA_COLLECTOR)
@pytest.mark.parametrize("topic, test_data", temp_testdata)
def test_temp_positive(iot_bridge_dc_iot_thing, topic, test_data):
    dc_service, iot_bridge_service, iot_thing = iot_bridge_dc_iot_thing

    root = dc_service.config.source_conf["collectors"]
    topic_name_qr = root["root_query"] + '/' + topic
    topic_name_send = root["root_send"] + '/' + topic
    
    iot_thing.subscribe_to_topic(topic_name_qr)
    iot_thing.subscribe_to_topic(topic_name_send)
    dc_service.config.generate_dc_temp_file(test_data)

    msg_body = {'msg': f"trigger the '{topic_name_qr}' query"}
    iot_thing.publish_message(topic_name_qr, msg_body)

    expected_message = {topic: dc_service.config.expected_temp_value}
    assert iot_thing.expects_message(topic_name_send, expected_message, strict=False, timeout=10)


ram_testdata = [
    pytest.param('ram', 100, id="SDV-126 Positive int ram"),
]

@SDVMarks.link(Tasks.TASK_126)
@SDVMarks.add(Type.INTEGRATION, Priority.P1, Suite.DATA_COLLECTOR)
@pytest.mark.parametrize("topic, test_data", ram_testdata)
def test_ram_positive(iot_bridge_dc_iot_thing, topic, test_data):
    dc_service, iot_bridge_service, iot_thing = iot_bridge_dc_iot_thing

    root = dc_service.config.source_conf["collectors"]
    topic_name_qr = root["root_query"] + '/' + topic
    topic_name_send = root["root_send"] + '/' + topic
    
    iot_thing.subscribe_to_topic(topic_name_qr)
    iot_thing.subscribe_to_topic(topic_name_send)
    dc_service.config.generate_dc_ram_file(test_data)

    msg_body = {'msg': f"trigger the '{topic_name_qr}' query"}
    iot_thing.publish_message(topic_name_qr, msg_body)

    expected_message = {topic: dc_service.config.expected_temp_value}
    assert iot_thing.expects_message(topic_name_send, expected_message, strict=False, timeout=10)


@SDVMarks.link(Tasks.TASK_127)
@SDVMarks.add(Type.INTEGRATION, Priority.P1, Suite.DATA_COLLECTOR)
def test_test(iot_thing):
    pass