from ControllerBGRPC import SendChatMessageRequest, SendChatMessageResponse

class ChatbotManager:

    def send_chat_message(self, user_message_request: "SendChatMessageRequest")-> "SendChatMessageResponse":
        """
        testing
        """
        print("TEST!!!!", user_message_request)
        self.__log.debug(f"TEST: {user_message_request}")

        response = SendChatMessageResponse()
        return response
