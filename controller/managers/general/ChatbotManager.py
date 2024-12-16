from ControllerBGRPC import UserMessageRequest, ChatbotResponse

class ChatbotManager:

    def send_chat_message(self, user_message_request: "UserMessageRequest")-> "ChatbotResponse":
        """
        testing
        """
        print("TEST!!!!", user_message_request)
        self.__log.debug(f"TEST: {user_message_request}")

        response = ChatbotResponse()
