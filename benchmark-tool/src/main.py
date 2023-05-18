from user.user import init_user
from config.config_validator import validate_config_values
from asyncio import run


async def main():
    configError = validate_config_values()
    if configError is not None:
        print(configError)
        return
    userId = await init_user()
    print(userId)


if __name__ == "__main__":
    run(main())
