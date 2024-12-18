from ControllerBGRPC import SendChatMessageRequest, SendChatMessageResponse

class ChatbotManager:

    def send_chat_message(self, send_chat_message_request: "SendChatMessageRequest")-> "SendChatMessageResponse":
        """
        testing
        """
        response = SendChatMessageResponse(response_chunk="hi", final_msg=True)
        return response
