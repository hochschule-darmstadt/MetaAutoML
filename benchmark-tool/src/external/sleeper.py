"""An adapter around the asyncio sleep function to be able to mock this import"""

import asyncio


async def sleep(seconds: int):
    """Sleeps for the given amount of seconds

    Args:
        seconds (int): The amount of seconds to sleep
    """
    await asyncio.sleep(seconds)
