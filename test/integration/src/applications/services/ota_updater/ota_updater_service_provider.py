from src.config.config import CONFIG
from src.enums.cloud_providers import CloudProviders
from src.enums.platforms import Platforms
from src.applications.services.ota_updater.aws.docker.ota_upd_client import OtaUpdaterDockerClient


class OtaUpdaterServiceProvider:
    MAPPER = {
        Platforms.RASPBERRY: {
            CloudProviders.AWS: OtaUpdaterDockerClient,
            CloudProviders.AZURE: None,
        },
        Platforms.RENESAS: {
            CloudProviders.AWS: None,
            CloudProviders.AZURE: None,
        },
    }

    @staticmethod
    def get_service(platform=CONFIG.PLATFORM, cloud_provider=CONFIG.CLOUD_PROVIDER):

        _platform = OtaUpdaterServiceProvider.MAPPER.get(platform)
        if _platform is None:
            raise NotImplementedError(
                f"Platform '{platform}' is not registered in the system"
            )

        application = _platform.get(cloud_provider)
        if application is None:
            raise NotImplementedError(
                f"Cloud provider '{cloud_provider}' is not registered in the system"
            )

        return application
