import asyncio
from grpclib.client import Channel
import os
from ChatbotBGRPC import ChatRequest, ChatReply, ChatbotStub
import logging

class ChatbotServiceManager:
    def __init__(self, host_env_var: str = 'CHATBOT_SERVICE_HOST', port_env_var: str = 'CHATBOT_SERVICE_PORT'):
        # Retrieve host and port from environment variables
        #Problem: it cant get the host host_env_var so host.docker.internal is the default (should be localhost)
        self.host = os.getenv(host_env_var, 'host.docker.internal')
        print("host",self.host)
        self.port = int(os.getenv(port_env_var, 50051))
        print ("port",self.port)
        # Default to 50051 if not set
        logging.basicConfig(level=logging.INFO)
        self.__log = logging.getLogger('ChatbotServiceManager')
        self.__log.info(f"Chatbot service will connect to {self.host}:{self.port}")

    async def send_message(self, message: str, history: str) -> str:
        """
        Sends a user-defined message to the RAG pipeline gRPC service and collects responses.

        Args:
            message (str): The user's message to be sent to the RAG pipeline.

        Returns:
            str: The aggregated response from the RAG pipeline.
        """
        async with Channel(self.host, self.port) as channel:
            stub = ChatbotStub(channel)
            request = ChatRequest(message=message, history=history)
            reply_text = ""
            async for reply in stub.chat(request):  # Correct usage of async generator
                reply_text += reply.chatbot_reply
                # self.__log.info(f"Received reply chunk: {reply.chatbot_reply}")
            self.__log.info(f"Received Reply: {reply_text}")
            return reply_text
