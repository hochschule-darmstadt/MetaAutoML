from ControllerBGRPC import SendChatMessageRequest, SendChatMessageResponse

class ChatbotManager:
    def send_chat_message(
        self,
        send_chat_message_request: SendChatMessageRequest,
        response_chunk: str
    ) -> SendChatMessageResponse:
        """
        Prepares and returns the response to be sent to the frontend.

        Args:
            send_chat_message_request (SendChatMessageRequest): The original request from the frontend.
            response_chunk (str): The processed response from the backend.

        Returns:
            SendChatMessageResponse: The response to be sent back to the frontend.
        """
        # Here you can add any additional processing or formatting if needed
        response = SendChatMessageResponse(
            response_chunk=response_chunk,
            final_msg=True
        )
        return response
