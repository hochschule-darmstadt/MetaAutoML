from uuid import UUID

from grpc_omaml.omaml_client import OmamlClient
from grpc_omaml import CreateNewUserRequest
from grpc_omaml.omaml_error import OmamlError


async def create_user() -> UUID:
    """Creates a new user and returns its id.

    Raises:
        OmamlError: When an error occurs while creating the user

    Returns:
        UUID: The id of the user
    """
    with OmamlClient() as client:
        try:
            response = await client.grpc_client.create_new_user(
                create_new_user_request=CreateNewUserRequest()
            )
            return UUID(response.user_id)
        except Exception as e:
            raise OmamlError("Error while creating user: ") from e
