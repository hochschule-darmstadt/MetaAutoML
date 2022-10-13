from dependency_injector import containers, providers
from AdapterScheduler import *
from MLJARAdapterManager import MLJARAdapterManager


class Managers(containers.DeclarativeContainer):
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )
    adapter_manager = providers.Factory(
        MLJARAdapterManager,
    )

class Application(containers.DeclarativeContainer):
    managers =  providers.Container(
        Managers,
    )