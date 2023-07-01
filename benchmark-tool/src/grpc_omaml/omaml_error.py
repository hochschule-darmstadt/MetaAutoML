class OmamlError(Exception):
    """Exception raised when an error occurs while communicating with the omaml server"""

    pass


class TrainingFailedError(Exception):
    """Exception raised when the training failed"""

    pass
