from src.applications.services.data_collector.aws.docker.dc_client import \
    DataCollectorDockerClient
from src.config.config import CONFIG
from src.enums.cloud_providers import CloudProviders
from src.enums.platforms import Platforms


class DCServiceProvider:
    MAPPER = {
        Platforms.RASPBERRY: {
            CloudProviders.AWS: DataCollectorDockerClient,
            CloudProviders.AZURE: None,
        },
        Platforms.RENESAS: {
            CloudProviders.AWS: None,
            CloudProviders.AZURE: None,
        },
    }

    @staticmethod
    def get_service(platform=CONFIG.PLATFORM, cloud_provider=CONFIG.CLOUD_PROVIDER):
        _platform = DCServiceProvider.MAPPER.get(platform)
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
