from dependency_injector import containers, providers
from AdapterScheduler import *
from McflyAdapterManager import McflyAdapterManager


class Managers(containers.DeclarativeContainer):
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )
    adapter_manager = providers.Factory(
        McflyAdapterManager,
    )

class Application(containers.DeclarativeContainer):
    managers =  providers.Container(
        Managers,
    )