from dependency_injector import containers, providers
from AdapterScheduler import *
from H2OAdapterManager import H2OAdapterManager
from ThreadLock import ThreadLock

class Ressources(containers.DeclarativeContainer):
    lock =  providers.ThreadSafeSingleton(
        ThreadLock,
    )


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
        H2OAdapterManager,
        lock=ressources.lock
    )

class Application(containers.DeclarativeContainer):
    """Dependency injection declarative container object, providing the application context level containers when injected, all dependencies injected by Managers

    Args:
        containers (containers.DeclarativeContainer): dependency-injector dependency providing functionality to inject dependencies
    """
    ressources = providers.Container(
        Ressources,
    )
    managers =  providers.Container(
        Managers,
        ressources=ressources,
    )
