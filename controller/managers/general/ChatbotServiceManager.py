import asyncio
from grpclib.client import Channel
from ChatbotBGRPC import ChatRequest, ChatReply, ChatbotStub
import logging

class ChatbotServiceManager:
    def __init__(self, host: str = 'localhost', port: int = 50051):
    #def __init__(self, host: str = 'chatbot-container', port: int = 50051):
        self.host = host
        self.port = port
        logging.basicConfig(level=logging.INFO)
        self.__log = logging.getLogger('ChatbotServiceManager')

    async def send_message(self, message: str, new_chat: bool) -> str:
        """
        Sends a user-defined message to the RAG pipeline gRPC service and collects responses.

        Args:
            message (str): The user's message to be sent to the RAG pipeline.

        Returns:
            str: The aggregated response from the RAG pipeline.
        """
        async with Channel(self.host, self.port) as channel:
            stub = ChatbotStub(channel)
            request = ChatRequest(message=message, new_chat=new_chat)

            reply_text = ""
            async for reply in stub.chat(request):  # Correct usage of async generator
                reply_text += reply.reply
                # self.__log.info(f"Received reply chunk: {reply.reply}")
            self.__log.info(f"Received Reply: {reply_text}")
            return reply_text
