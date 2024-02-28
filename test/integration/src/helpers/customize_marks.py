import allure
import pytest

from src.enums.marks import FrameworkSpecific, Priority, Tasks, Suite, Type
from src.logger import SDVLogger

logger = SDVLogger.get_logger("SDVMarks")


class SDVMarks:
    """
    More a namespace for methods that work with pytest marks
    """

    @staticmethod
    def to_be_automated():
        """
        This decorator adds 'to be automated' marker to the test which will be skipped according to pytest_collection_modifyitems hook
        """

        return SDVMarks.add(FrameworkSpecific.TO_BE_AUTOMATED)

    @staticmethod
    def link(tc_id):
        """
        This decorator adds Link to allure report
        """

        logger.debug("Adding test case id")

        def _(f):
            f = getattr(pytest.mark, tc_id.value)(f)
            
            f = allure.id(tc_id.value)(f)
            f = allure.link(f"https://google.com/{tc_id}")(f)  # TODO: FInilize test links

            return f

        return _

    @staticmethod
    def add(*args):
        """
        Adds the list of arguments as separate pytest markers for a test item
        """

        def _(f):
            for mark in args:
                f = getattr(pytest.mark, mark.value)(f)

                if mark in Priority:
                    logger.debug(f"FOUND PRIORITY MARK {mark}")
                    f = allure.severity(mark.value)(f)

                if mark in Suite:
                    f = allure.suite(mark.value)(f)
                    f = allure.link("https://google.com")(f)
                    logger.debug(f"FOUND TEST SUIT mark {mark}")

                if mark in Tasks:
                    f = allure.story(mark.value)(f)
                    logger.debug(f"FOUND TASK mark {mark}")

            return f

        return _
    
    @staticmethod
    def get_list_of_marks(test_item):
        return set(d.name for d in test_item.iter_markers())
        # return set(test_item.iter_markers(name='name'))
