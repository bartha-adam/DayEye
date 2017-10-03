CREATE TABLE [dbo].[Users]
(
	[Email] NVARCHAR(50) NOT NULL PRIMARY KEY, 
    [GoogleToken] NVARCHAR(200) NOT NULL, 
    [RefreshToken] NVARCHAR(100) NOT NULL, 
    [FirstName] NVARCHAR(50) NULL
)
