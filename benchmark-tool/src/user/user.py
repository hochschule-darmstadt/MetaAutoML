from uuid import UUID
from config.config_accessor import get_userid
from grpc_omaml.omaml_client import OmamlClient


async def init_user(client: OmamlClient) -> UUID:
    """Initializes a user with configured id.
    If no id was configured, a new user is created and the id is returned.

    Args:
        client (OmamlClient): The omaml client to use

    Returns:
        UUID: The id of the user
    """

    userid = get_userid()
    if userid is None:
        return await client.create_user()
    return UUID(userid)
