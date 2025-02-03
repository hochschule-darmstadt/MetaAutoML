namespace BlazorBoilerplate.Shared.Dto.Chat
{

    public class SendChatMessageResponseDto
    {
        public string ResponseMessage { get; set; }

        public SendChatMessageResponseDto(string response)
        {
            ResponseMessage = response;
        }
    }
}
