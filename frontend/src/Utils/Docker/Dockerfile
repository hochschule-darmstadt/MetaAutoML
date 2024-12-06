FROM mcr.microsoft.com/dotnet/aspnet:6.0.16-jammy-amd64 AS base
WORKDIR /
EXPOSE 443
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:6.0.408-jammy-amd64 AS build
WORKDIR /
COPY . .

# Install Node.js 16.x
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get update && apt-get install -y nodejs

# Install npm (included with Node.js)
#RUN npm install -g npm@latest

RUN dotnet restore "src/Server/BlazorBoilerplate.Server/BlazorBoilerplate.Server.csproj"
WORKDIR "/src/Server/BlazorBoilerplate.Server"
RUN dotnet build "BlazorBoilerplate.Server.csproj" -c Release -o /app/build --no-restore

FROM build AS publish
RUN dotnet publish "BlazorBoilerplate.Server.csproj" -c Release -o /app/publish
RUN dotnet dev-certs https --clean
RUN dotnet dev-certs https -ep /app/publish/aspnetapp.pfx -p Admin123
#if .pfx was provided from certificate authority uncomment the below
#COPY src/Server/BlazorBoilerplate.Server/AuthSample.pfx /app/publish/aspnetapp.pfx

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
COPY --from=publish /app/publish/aspnetapp.pfx ./AuthSample.pfx
ENTRYPOINT ["dotnet", "BlazorBoilerplate.Server.dll"]
