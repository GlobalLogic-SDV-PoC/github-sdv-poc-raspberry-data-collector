class BaseCloudClient:
    def init_cli(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def connect_to_message_bus(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def terminate(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def publish_message(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def subscribe_to_topic(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def tear_up_thing(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def tear_down_thing(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def ecr_login(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def get_ota_service_test_package(self):
        raise NotImplementedError(f"Method {__name__} needs to be implemented")

    def convert_to_non_strict_message(self, message):
        message = message.lower()
        message = message.replace(" ", "")
        message = message.replace("\"", "")
        message = message.replace("'", "")

        return message
        