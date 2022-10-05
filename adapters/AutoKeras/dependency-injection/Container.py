from dependency_injector import containers, providers
from AdapterScheduler import *



class Managers(containers.DeclarativeContainer):
    adapter_scheduler = providers.ThreadSafeSingleton(
        AdapterScheduler,
    )

class Application(containers.DeclarativeContainer):
    managers =  providers.Container(
        Managers,
    )