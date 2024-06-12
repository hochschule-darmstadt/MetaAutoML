using System.ComponentModel.DataAnnotations;

namespace BlazorBoilerplate.Shared.Models.Account
{
    public class LoginInputModel : AccountFormModel
    {
        private string _userName;
        public string UserName
        {
            get => _userName;
            set => _userName = value?.Trim();
        }

        private string _password;
        [DataType(DataType.Password)]
        public string Password
        {
            get => _password;
            set => _password = value?.Trim();
        }
    }
}
