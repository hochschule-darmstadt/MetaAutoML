from ControllerBGRPC import SendChatMessageRequest, SendChatMessageResponse

class ChatbotManager:
    def send_chat_message(
        self,
        send_chat_message_request: SendChatMessageRequest,
        response: str
    ) -> SendChatMessageResponse:
        """
        Prepares and returns the response to be sent to the frontend.

        Args:
            send_chat_message_request (SendChatMessageRequest): The original request from the frontend.
            response (str): The processed response from the backend.

        Returns:
            SendChatMessageResponse: The response to be sent back to the frontend.
        """
        response_str = SendChatMessageResponse(
            controller_response=response
        )
        return response_str
