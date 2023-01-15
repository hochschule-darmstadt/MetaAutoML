from dependency_injector import containers, providers
from AdapterScheduler import *
from AutoPytorchAdapterManager import AutoPytorchAdapterManager


class Managers(containers.DeclarativeContainer):
    """Dependency injection declarative container object, providing the different manager instances when injected.
    For each individual adapter the correct AdapterManager is injected here

    Args:
        containers (containers.DeclarativeContainer): dependency-injector dependency providing functionality to inject dependencies
    """
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )
    adapter_manager = providers.Factory(
        AutoPytorchAdapterManager,
    )

class Application(containers.DeclarativeContainer):
    """Dependency injection declarative container object, providing the application context level containers when injected, all dependencies injected by Managers

    Args:
        containers (containers.DeclarativeContainer): dependency-injector dependency providing functionality to inject dependencies
    """
    managers =  providers.Container(
        Managers,
    )
