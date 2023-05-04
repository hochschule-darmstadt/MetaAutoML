from uuid import UUID
from config.config_accessor import get_userid
from user.omaml_user_adapter import create_user


def init_user() -> UUID:
    """Initializes a user with configured id.
    If no id was configured, a new user is created and the id is returned.

    Returns:
        UUID: The id of the user
    """

    userid = get_userid()
    if userid is None:
        return create_user()
    return UUID(get_userid())
