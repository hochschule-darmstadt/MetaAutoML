using Microsoft.AspNetCore.Razor.TagHelpers;

namespace BlazorBoilerplate.Theme.Material.TagHelpers
{
    public class ThemeTagHelperComponent : TagHelperComponent
    {
        public override int Order => 1;
        public override Task ProcessAsync(TagHelperContext context, TagHelperOutput output)
        {
            var path = typeof(Module).Namespace;

            if (string.Equals(context.TagName, "head", StringComparison.OrdinalIgnoreCase))
            {
                output.PostContent.AppendHtml(@$"
<link rel=""shortcut icon"" type=""image/x-icon"" href=""_content/{path}/images/favicon.ico"">
<link rel=""icon"" type=""image/x-icon"" href=""_content/{path}/images/favicon.ico"">
<link href=""_content/{path}/css/bootstrap/bootstrap.min.css"" rel=""stylesheet"" />
<link href=""_content/{path}/stackpath.bootstrapcdn.com/font-awesome/4.7.0/font-awesome.min.css"" rel=""stylesheet"" />
<link href=""_content/{path}/fonts.googleapis.com/Roboto.css"" rel=""stylesheet"" />
<link href=""_content/{path}/fonts.googleapis.com/KFOlCnqEu92Fr1MmEU9fBBc4.woff2"" rel=""woff2"" />
<link href=""_content/{path}/fonts.googleapis.com/KFOlCnqEu92Fr1MmWUlfBBc4.woff2"" rel=""woff2"" />
<link href=""_content/{path}/fonts.googleapis.com/KFOmCnqEu92Fr1Mu4mxK.woff2"" rel=""woff2"" />
<link href=""_content/{path}/fonts/roboto/roboto.css"" rel=""stylesheet"" />
<link href=""_content/MatBlazor/dist/matBlazor.css"" rel=""stylesheet"" />
<link href=""_content/{path}/css/cdn.quilljs.com/1.3.6/quill.snow.css"" rel=""stylesheet"">
<link href=""_content/{path}/css/cdn.quilljs.com/1.3.6/quill.bubble.css"" rel=""stylesheet"">
<script src=""_content/{path}/js/cdn.quilljs.com/1.3.6/quill.js""></script>
<link href=""_content/{path}/css/site.css"" rel=""stylesheet"" />");
            }
            else if (string.Equals(context.TagName, "app", StringComparison.OrdinalIgnoreCase))
            {
                output.PostElement.AppendHtml(@$"
<script src=""_content/MatBlazor/dist/matBlazor.js""></script>
<script src=""_content/{path}/js/cdn.quilljs.com/1.3.6/quill.js""></script>
<script src=""_content/Blazored.TextEditor/quill-blot-formatter.min.js""></script>
<script src=""_content/Blazored.TextEditor/Blazored-BlazorQuill.js""></script>");
            }

            return Task.CompletedTask;
        }
    }
}
