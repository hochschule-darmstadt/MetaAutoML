from dependency_injector import containers, providers
from AdapterScheduler import *
from AutoGluonAdapterManager import AutoGluonAdapterManager


class Managers(containers.DeclarativeContainer):
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )
    adapter_manager = providers.Factory(
        AutoGluonAdapterManager,
    )

class Application(containers.DeclarativeContainer):
    managers =  providers.Container(
        Managers,
    )