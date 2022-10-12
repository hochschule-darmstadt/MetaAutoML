from dependency_injector import containers, providers
from AdapterScheduler import *
from AutoSklearnAdapterManager import AutoSklearnAdapterManager


class Managers(containers.DeclarativeContainer):
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )
    adapter_manager = providers.Factory(
        AutoSklearnAdapterManager,
    )

class Application(containers.DeclarativeContainer):
    managers =  providers.Container(
        Managers,
    )