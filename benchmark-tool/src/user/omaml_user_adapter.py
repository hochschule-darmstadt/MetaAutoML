from uuid import UUID

from grpc_omaml.client_factory import create_omaml_client
from grpc_omaml import CreateNewUserRequest
from grpc_omaml.omaml_error import OmamlError


async def create_user() -> UUID:
    """Creates a new user and returns its id.

    Returns:
        UUID: The id of the user
    """
    client = create_omaml_client()
    try:
        response = await client.create_new_user(
            create_new_user_request=CreateNewUserRequest()
        )
        return UUID(response.user_id)
    except Exception as e:
        raise OmamlError("Error while creating user: ") from e
