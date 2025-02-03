import pyinstrument
from Container import Application
from dependency_injector.wiring import inject, Provide
from ControllerBGRPC import *
from UserManager import UserManager

@inject
def get_home_overview_information(
    get_home_overview_information_request: "GetHomeOverviewInformationRequest",
    user_manager: UserManager=Provide[Application.managers.user_manager]
):
    profiler = pyinstrument.Profiler()
    profiler.start()
    response = user_manager.get_home_overview_information(get_home_overview_information_request)
    profiler.stop()
    profiler.print()
    profiler.open_in_browser()
    print(response)

def main():
    get_home_overview_information(get_home_overview_information_request=GetHomeOverviewInformationRequest(user_id="e763ec28-90ab-4621-9227-87c229be09fd"))

if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    main()
