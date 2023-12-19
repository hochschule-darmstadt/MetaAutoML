using GTour.Abstractions;

namespace GTour.Themes
{
    internal class CustomTheme : ITheme
    {
        public string GTourOverlay { get; set; } 
        public string GTourWrapper { get; set; }
        public string GTourArrow { get; set; }
        public string GTourStepWrapper { get; set; } = "modal-content ";
        public string GTourStepHeaderWrapper { get; set; }// = "modal-header ";
        public string GTourStepContentWrapper { get; set; } = "modal-body ";
        public string GTourStepFooterWrapper { get; set; } = "modal-footer ";
        public string GTourStepHeaderTitle { get; set; } 
        public string GTourStepCancelButton { get; set; } = "mud-button-root mud-button mud-button-filled mud-button-filled-secondary mud-button-filled-size-medium mud-ripple ";
        public string GTourStepPreviousButton { get; set; } = "mud-button-root mud-button mud-button-filled mud-button-filled-secondary mud-button-filled-size-medium mud-ripple";
        public string GTourStepNextButton { get; set; } = "mud-button-root mud-button mud-button-filled mud-button-filled-secondary mud-button-filled-size-medium mud-ripple";
        public string GTourStepCompleteButton { get; set; } = "mud-button-root mud-button mud-button-filled mud-button-filled-secondary mud-button-filled-size-medium mud-ripple";
    }
}
