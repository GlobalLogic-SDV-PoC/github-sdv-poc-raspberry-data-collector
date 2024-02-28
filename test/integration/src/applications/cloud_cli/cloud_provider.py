from src.applications.cloud_cli.aws.aws_cli_client import AWSCliClient
from src.applications.cloud_cli.azure.azure_cli_client import AzureCliClient
from src.enums.cloud_providers import CloudProviders


class CloudProvider:
    MAPPER = {
        CloudProviders.AWS: AWSCliClient,
        CloudProviders.AZURE: AzureCliClient,
    }

    @staticmethod
    def get_provider(name):
        provider = CloudProvider.MAPPER.get(name)
        if provider is None:
            raise NotImplementedError(
                f"Cloud provider {name} is not registered in the system"
            )

        return provider
