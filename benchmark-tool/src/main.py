from user.user import init_user
from asyncio import run


async def main():
    userId = await init_user()
    print(userId)


if __name__ == "__main__":
    run(main())
