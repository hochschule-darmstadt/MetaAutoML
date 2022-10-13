namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingResponseDto
    {
        public TrainingDto Training { get; set; }
        public GetTrainingResponseDto(TrainingDto training)
        {
            Training = training;
        }
    }
}
