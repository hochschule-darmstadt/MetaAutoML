using System;
namespace BlazorBoilerplate.Shared.Dto
{
    public class HelpPageDto
    {
        public string PanelHeadline { get; set; }
        public string Text { get; set; }
        public string Image { get; set; }
        public List<Section> Sections { get; set; }
        public HelpPageDto()
        {
            PanelHeadline = "";
            Sections = new List<Section>();
        }
    }
    public class Subsection
    {
        public string SubHeadline { get; set; }
        public string SubText { get; set; }
    }
    public class Section
    {
        public string Headline { get; set; }
        public string Text { get; set; }
        public List<Subsection> Subsections { get; set; }
        public string GIF { get; set; }
        public string Anchor { get; set; }
    }
    public class HelpTabPanel
    {
        public string PanelHeadline { get; set; }
        public List<Section> IntroductionSections { get; set; }
    }
}

