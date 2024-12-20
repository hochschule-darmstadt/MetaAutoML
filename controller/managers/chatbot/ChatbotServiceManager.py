import asyncio
from grpclib.client import Channel
from ChatbotBGRPC import ChatRequest, ChatReply, ChatbotStub
import logging

class ChatbotServiceManager:
    def __init__(self, host: str = 'localhost', port: int = 50051):
        self.host = host
        self.port = port
        logging.basicConfig(level=logging.INFO)
        self.__log = logging.getLogger('ChatbotServiceManager')

    async def send_message(self) -> str:
        """
        Sends a predefined message to the gRPC service and collects responses.
        """
        message = "can u spell OMAML"  # Fixed message for testing purposes
        async with Channel(self.host, self.port) as channel:
            stub = ChatbotStub(channel)
            request = ChatRequest(message=message)

            reply_text = ""
            async for reply in stub.chat(request):  # Correct usage of async generator
                reply_text += reply.reply
                self.__log.info(f"Received reply: {reply.reply}")

            return reply_text

if __name__ == "__main__":
    manager = ChatbotServiceManager()
    response = asyncio.run(manager.send_message())
    print("Response from gRPC service:", response)
