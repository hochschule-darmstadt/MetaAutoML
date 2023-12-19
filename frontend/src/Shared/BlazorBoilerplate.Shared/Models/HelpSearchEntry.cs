using BlazorBoilerplate.Shared.Dto;
using Karambolo.Common;

namespace BlazorBoilerplate.Shared.Models
{
    public class HelpSearchEntry
    {
        protected HelpSearchEntry(HelpSearchResultType type, string title, string altTitle, string description, bool subsection, string origin, string link, string anchor)
        {
            Type = type;
            Title = title;
            if(altTitle == null)
            {
                AltTitle = "";
            }
            else
            {
                AltTitle = altTitle;
            }
            Description = description;
            IsSubSection = subsection;
            Origin = origin;
            Link = link;
            Anchor = anchor;
        }

        public HelpSearchEntry(string title): this(HelpSearchResultType.PLACEHOLDER, title, null, "", false, null, null, null)
        {
        }

        public HelpSearchResultType Type { get; }
        public string Title { get; }
        public string AltTitle { get; }
        public string Origin { get; }
        public string Description { get; }
        public string Link { get; }
        public string Anchor { get; }
        public bool IsSubSection { get; }

        /// <summary>
        /// Generate Option Text shown in autocomplete dropdown
        /// </summary>
        /// <value></value>
        public string OptionText
        {
            get
            {
                string result = "";
                result += Title;

                if(!AltTitle.IsNullOrEmpty())
                {
                    result += " (" + AltTitle + ")";
                }

                if(!Origin.IsNullOrEmpty())
                {
                    result += " [" + Origin + "]";
                }

                return result.Replace(":", "");
            }
        }

        /// <summary>
        /// Match Search string against Help Search Entry
        ///
        /// Following Ranking is calculated:
        /// 10 = Match in Title or AltLabel at beginning
        /// 9 = Match in Title or AltLabel at beginning in subsection
        /// 8 = Match in Title or AltLabel at beginning of word
        /// 7 = Match in Title or AltLabel at beginning of word in subsection
        /// 6 = Match in Title anywhere
        /// 5 = Match in Title anywhere in subsection
        /// 4 = Match in Description start of word
        /// 3 = Match in Description start of word in subsection
        /// 2 = Match in Description anywhere
        /// 1 = Match in Description anywhere in subsection
        /// 0 = No Match
        /// </summary>
        /// <param name="search">search text</param>
        /// <returns>score</returns>
        public int MatchScore(string search)
        {
            int ranking = Math.Max(DetectStringPosition(Title, search), DetectStringPosition(AltTitle, search));

            if(ranking > 0)
            {
                // Convert Ranking from 1-3 to 6-10
                ranking = (ranking * 2) + 4;
            }
            else
            {
                // Convert Ranking from 0-2(3) to 0-4
                ranking = Math.Min(DetectStringPosition(Description, search) * 2, 4);
            }

            // Subsection get a rank - 1
            if (IsSubSection && ranking > 0)
            {
                ranking -= 1;
            }

            return ranking;
        }

        /// <summary>
        /// Detect where the search term is found in the search entry
        ///
        /// 3 = Start of the string
        /// 2 = Start of a word
        /// 1 = Contained in the string
        /// 0 = No Match found
        /// </summary>
        /// <param name="text">To search in</param>
        /// <param name="search">To find in the search</param>
        /// <returns>score</returns>
        private static int DetectStringPosition(string text, string search)
        {
            // Check if match is at beginning of string
            if(text.StartsWith(search, StringComparison.InvariantCultureIgnoreCase))
            {
                return 3;
            }

            string[] parts = text.Split(" ", StringSplitOptions.RemoveEmptyEntries);

            // Check if match is at beginning of a word in the string
            if(parts.Any(part => part.StartsWith(search, StringComparison.InvariantCultureIgnoreCase)))
            {
                return 2;
            }

            // Check if match in any word of the word
            if(text.Contains(search, StringComparison.InvariantCultureIgnoreCase))
            {
                return 1;
            }

            return 0;
        }

        public override string ToString()
        {
            return OptionText;
        }

        public override bool Equals(object obj)
        {
            //Check for null and compare run-time types.
            if ((obj == null) || ! this.GetType().Equals(obj.GetType()))
            {
                return false;
            }

            HelpSearchEntry other = (HelpSearchEntry) obj;

            return this.Type == other.Type && this.Title == other.Title && this.AltTitle == other.AltTitle && this.Origin == other.Origin;
        }

        public static HelpSearchEntry ConvertToHelpSearchEntry(Server.SearchRelevantData data)
        {
            return new HelpSearchEntry(HelpSearchResultType.ONTOLOGY, data.Label, data.AltLabels, data.Comment, false, data.Class, data.Link, null);
        }

        public static HelpSearchEntry[] ConvertToHelpSearchEntries(Section data)
        {
            List<HelpSearchEntry> entries = new List<HelpSearchEntry>();

            if(data.Subsections != null)
            {
                entries = data.Subsections
                    .Select(e => new HelpSearchEntry(HelpSearchResultType.HELP_ARTICLE, e.SubHeadline, null, e.SubText, true, null, null, data.Anchor))
                    .ToList();
            }

            entries.Add(new HelpSearchEntry(HelpSearchResultType.HELP_ARTICLE, data.Headline, null, data.Text, false, null, null, data.Anchor));

            return entries.ToArray();
        }
    }

    public enum HelpSearchResultType {
        ONTOLOGY,
        HELP_ARTICLE,
        PLACEHOLDER
    }
}
