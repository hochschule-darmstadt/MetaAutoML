from user.user import init_user
from dataset.dataset import upload_dataset
from config.config_validator import validate_config_values
from asyncio import run


async def main():
    configError = validate_config_values()
    if configError is not None:
        print(configError)
        return
    userId = await init_user()
    await upload_dataset(userId)


if __name__ == "__main__":
    run(main())
