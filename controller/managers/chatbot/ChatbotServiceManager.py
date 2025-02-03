import asyncio
from grpclib.client import Channel
import os
from ChatbotBGRPC import ChatRequest, ChatReply, ChatbotStub
import logging

class ChatbotServiceManager:
	"""
	Handles communication with the backend RAG pipeline gRPC service.
	"""
	def __init__(self, host_env_var: str = 'CHATBOT_SERVICE_HOST', port_env_var: str = 'CHATBOT_SERVICE_PORT'):
		self.host = os.getenv(host_env_var, 'host.docker.internal')
		self.port = int(os.getenv(port_env_var, 50051))  # Default to 50051 if not set
		logging.basicConfig(level=logging.INFO)
		self.__log = logging.getLogger('ChatbotServiceManager')
		self.__log.info(f"Chatbot service will connect to {self.host}:{self.port}")

	async def send_message(self, message: str, history: str) -> str:
		"""
		Sends a user-defined message to the RAG pipeline gRPC service and collects responses.

		Args:
			message (str): The user's message.
			history (str): The conversation history.

		Returns:
			str: The aggregated response from the RAG pipeline.
		"""
		try:
			async with Channel(self.host, self.port) as channel:
				stub = ChatbotStub(channel)
				request = ChatRequest(message=message, history=history)
				reply_text = ""
				async for reply in stub.chat(request):  # Correct usage of async generator
					reply_text += reply.chatbot_reply
				self.__log.info(f"Received Reply: {reply_text}")
				return reply_text
		except Exception as e:
			self.__log.error(f"Error in send_message: {e}")
			return "An error occurred while communicating with the chatbot service."
