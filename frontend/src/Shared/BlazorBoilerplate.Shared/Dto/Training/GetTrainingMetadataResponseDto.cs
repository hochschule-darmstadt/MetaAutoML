namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingMetadataResponseDto
    {
        public TrainingMetadataDto Training { get; set; }
        public GetTrainingMetadataResponseDto(TrainingMetadataDto training)
        {
            Training = training;
        }
    }
}
