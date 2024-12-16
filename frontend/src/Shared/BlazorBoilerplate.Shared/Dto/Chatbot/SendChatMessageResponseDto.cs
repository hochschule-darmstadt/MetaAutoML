namespace BlazorBoilerplate.Shared.Dto.Chat
{

    public class SendChatMessageResponseDto
    {
        public string ResponseChunk { get; set; }
        public bool IsFinalMessage { get; set; }
    }
}
