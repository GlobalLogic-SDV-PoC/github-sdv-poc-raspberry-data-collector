import re

import pytest
from py.xml import html
from src.applications.cloud_cli.conftest import iot_thing
from src.applications.services.data_collector.dc_service_provider import \
    DCServiceProvider
from src.applications.services.iot_bridge.iot_bridge_service_provider import \
    IotBridgeServiceProvider
from src.applications.services.ota_updater.ota_updater_service_provider import \
    OtaUpdaterServiceProvider
from src.config.config import CONFIG
from src.logger import SDVLogger
from src.enums.marks import FrameworkSpecific
from src.helpers.customize_marks import SDVMarks
from src.config.run_modes.modes_provider import ModesProvider
from src.testcase_management.test_results_adaptors.adaptors_provider import AdaptorsProvider
from src.artifacts_collectors.tests_artifact_collector import TestsArtifactCollector
import os



LOGGER = SDVLogger.get_logger("CONFTEST")


@pytest.fixture(scope="module")
def iot_bridge_iot_thing(iot_thing):
    iot_bridge_class = IotBridgeServiceProvider.get_service(
        platform=CONFIG.PLATFORM, cloud_provider=CONFIG.CLOUD_PROVIDER
    )
    iot_bridge_service = iot_bridge_class(
         thing_name=iot_thing.thing_name,
         certs_folder=iot_thing.certs_folder
    )
    iot_bridge_service.tear_up()

    yield iot_bridge_service, iot_thing

    iot_bridge_service.tear_down()

@pytest.fixture(scope="module")
def iot_bridge_ota_iot_thing(iot_bridge_iot_thing):
    iot_bridge_service, iot_thing = iot_bridge_iot_thing

    ota_class = OtaUpdaterServiceProvider.get_service(
        platform=CONFIG.PLATFORM, cloud_provider=CONFIG.CLOUD_PROVIDER
    )
    ota_service = ota_class()
    ota_service.tear_up()

    yield ota_service, iot_bridge_service, iot_thing

    ota_service.tear_down()




@pytest.fixture(scope="module")
def iot_bridge_dc_iot_thing(iot_bridge_iot_thing):
    iot_bridge_service, iot_thing = iot_bridge_iot_thing

    dc_class = DCServiceProvider.get_service(
        platform=CONFIG.PLATFORM, cloud_provider=CONFIG.CLOUD_PROVIDER
    )
    dc_service = dc_class()
    dc_service.tear_up()

    yield dc_service, iot_bridge_service, iot_thing

    dc_service.tear_down()


# === BEGIN Pytest html modifications === #
def pytest_html_report_title(report):
    """modifying the title  of html report"""
    report.title = f"SDV Testing report for Python-{CONFIG.PYTHON_VERSION}"


def pytest_html_results_table_header(cells):
    """meta programming to modify header of the result"""
    # removing old table headers
    # adding new headers
    cells.append(
        html.th("Python Version", class_="sortable pythonversion", col="pythonversion")
    )
    cells.append(html.th("Test Case", class_="sortable testcase", col="testcase"))
    del cells[3]  # remove links column


def pytest_html_results_table_row(report, cells):
    """orienting the data gotten from  pytest_runtest_makereport
    and sending it as row to the result"""
    cells.append(html.td(CONFIG.PYTHON_VERSION))
    cells.append(html.td(report.testcase))
    del cells[3]  # remove links column

# === END Pytest html modifications === #
def pytest_collection_modifyitems(config, items):
    for item in items:
        if CONFIG.PLATFORM == "dev" and FrameworkSpecific.SKIP_IF_DEV.value in item.keywords:
            skip_dev_env = pytest.mark.skip(reason="Functionality is not implemented in development environment")
            item.add_marker(skip_dev_env)

        if FrameworkSpecific.TO_BE_AUTOMATED.value in SDVMarks.get_list_of_marks(item):
            skip_as_not_automated = pytest.mark.skip(FrameworkSpecific.TO_BE_AUTOMATED.value)
            item.add_marker(skip_as_not_automated)


def pytest_collection_finish(session):
    run_mode = ModesProvider.get_mode(CONFIG.RUN_MODE)
    LOGGER.info(f"Start validation of tests for '{run_mode}' test run mode")
    for item in session.items:
        if run_mode.validate_test(item) is False:
            pytest.exit("Run mode validation failed")

    
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    if result.when == 'call':
        tc_adaptors = AdaptorsProvider.get_providers(CONFIG.TC_ADAPTERS)
        LOGGER.info(f"Test '{item.originalname}' - {result.outcome}")
        
        for adaptor in tc_adaptors:
            LOGGER.info(f"Trying to use '{adaptor}' test case management adaptor")
            adaptor.update_automation_status(item)
            adaptor.update_run_result(item)

        if CONFIG.ARTIFACTS_COLLECT is True:
            LOGGER.info(f"Trying to collect all the possible applcaitions artifcats")

            try:
                artifact_collectors = TestsArtifactCollector(
                    path=CONFIG.ARTIFACTS_FOLDER,
                    test_name = item.originalname
                )

                artifact_collectors.collect_pytest_logs(item._report_sections)
                
                for fixture in item.fixturenames:
                    objs = item.funcargs[fixture]
                    if isinstance(objs, tuple) is False:
                        objs = [objs]
                    
                    # TODO: Artifacts been overwritten since pytest keeps fixture more that once. needs to be insvetigated
                    for obj in objs:
                        if artifact_collectors.is_collectable(obj):
                            artifact_collectors.collect(obj)

                artifact_collectors.compress()
            except Exception as e:
                LOGGER.exception(e)

    testcase = str(item.function.__doc__)
    ids = re.search(r"\[(.*?)\]", str(item.keywords))
    if ids is not None:
        testcase = ids.group(1)

    result.testcase = testcase