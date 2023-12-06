using BlazorBoilerplate.Shared.Dto;

namespace BlazorBoilerplate.Shared.Models
{
    public class HelpSearchEntry
    {
        public HelpSearchEntry(Section data)
        {
            Type = HelpSearchResultType.HELP_ARTICLE;
            HelpArticleData = data;
        }

        public HelpSearchEntry(Server.SearchRelevantData data)
        {
            Type = HelpSearchResultType.ONTOLOGY;
            OntologyData = data;
        }

        public HelpSearchResultType Type { get; }
        public Section HelpArticleData { get; }
        public Server.SearchRelevantData OntologyData { get; }

        public string[] AutocompleteTexts {
            get {
                switch(Type)
                {
                    case HelpSearchResultType.ONTOLOGY:
                    {
                        return new string[]{OntologyData.Label, OntologyData.AltLabels};
                    }
                    case HelpSearchResultType.HELP_ARTICLE:
                    {

                        if(HelpArticleData.Subsections == null)
                        {
                            return new string[]{HelpArticleData.Headline};
                        }

                        return HelpArticleData.Subsections.Select(e => e.SubHeadline)
                            .Concat(new string[]{HelpArticleData.Headline})
                            .ToArray();
                    }
                    default:
                    {
                        return new string[]{};
                    }
                }
            }
        }

        public string[] FullSearchTexts {
            get {
                switch(Type)
                {
                    case HelpSearchResultType.ONTOLOGY:
                    {
                        return new string[]{OntologyData.Label, OntologyData.AltLabels, OntologyData.Comment};
                    }
                    case HelpSearchResultType.HELP_ARTICLE:
                    {
                        return HelpArticleData.Subsections.SelectMany(e => new[]{ e.SubHeadline, e.SubText})
                            .Concat(new []{HelpArticleData.Headline, HelpArticleData.Text})
                            .ToArray();
                    }
                    default:
                    {
                        return new string[]{};
                    }
                }
            }
        }
    }

    public enum HelpSearchResultType {
        ONTOLOGY,
        HELP_ARTICLE
    }
}
