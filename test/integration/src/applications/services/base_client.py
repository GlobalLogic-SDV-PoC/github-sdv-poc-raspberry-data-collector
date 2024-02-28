class BaseClient:
    HAS_ARTIFACTS_TO_COLLECT = False

    def tear_up(self):
        raise NotImplementedError("Methon tear_up needs to be implemented")

    def tear_down(self):
        raise NotImplementedError("Methon tear_down needs to be implemented")

    def collect_artifacts(self):
        raise NotImplementedError("Methon collect_artifacts needs to be implemented")
