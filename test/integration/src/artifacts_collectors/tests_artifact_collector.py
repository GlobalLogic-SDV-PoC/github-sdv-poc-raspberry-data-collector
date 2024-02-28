from src.logger import SDVLogger
import os
from src.helpers.helpers import append_to_file, write_to_file


LOGGER = SDVLogger.get_logger("TestsArtifactCollector")


class TestsArtifactCollector:

    def __init__(self, path, test_name) -> None:
        self.path = path
        self.test_name = test_name
        self.test_artifact_folder = os.path.join(self.path, self.test_name)

    def compress(self):
        LOGGER.info(f"Compressing folder '{self.test_artifact_folder}'")
        pass

    def collect(self, app):
        LOGGER.info(f"Collecting artifacts into '{self.test_artifact_folder}'")

        return app.collect_artifacts(self.test_artifact_folder)

    def collect_pytest_logs(self, logs: list):
        
        # form context
        context = {}
        for _ in logs:
            stage = _[0]
            pipe = _[1]
            log = _[2]
            context[stage] = {}
            context[stage][pipe] = log

        LOGGER.info(context)
        filename = f'pytest_logs_{self.test_name}.log'
        path = os.path.join(self.test_artifact_folder, filename)
        LOGGER.info(f"Collect pytest logs into '{path}'")
        
        write_to_file(path, f"======PyTest logs for '{self.test_name}'======\n\n")
        for stage_name, stages in context.items():
            append_to_file(path, f'=={stage_name}')
            append_to_file(path, '\n')
            for pipe_name, log in stages.items():
                append_to_file(path, f'={pipe_name}')
                append_to_file(path, '\n')
                append_to_file(path, log)
                append_to_file(path, '\n\n')

        return self

    def is_collectable(self, item):
        LOGGER.info(f"Check if '{item}' has artifacts to collect")
        res = False
        try:
            res = item.HAS_ARTIFACTS_TO_COLLECT
        except:
            pass

        if res is True:
            LOGGER.info(f"'{item}' has artifacts to collect")
        else:
            LOGGER.info("Nothing to collect")

        return res