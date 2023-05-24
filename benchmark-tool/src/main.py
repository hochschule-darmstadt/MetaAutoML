from user.user import init_user
from dataset.dataset import upload_dataset
from config.config_validator import validate_config_values
from asyncio import run
from grpc_omaml.omaml_client import OmamlClient


async def main():
    configError = validate_config_values()
    if configError is not None:
        print(configError)
        return
    with OmamlClient() as client:
        userId = await init_user(client)
        await upload_dataset(client, userId)


if __name__ == "__main__":
    run(main())
