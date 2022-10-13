from dependency_injector import containers, providers
from AdapterScheduler import *
from FLAMLAdapterManager import FLAMLAdapterManager


class Managers(containers.DeclarativeContainer):
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )
    adapter_manager = providers.Factory(
        FLAMLAdapterManager,
    )

class Application(containers.DeclarativeContainer):
    managers =  providers.Container(
        Managers,
    )