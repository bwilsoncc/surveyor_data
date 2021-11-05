import-module dbatools
#Variable setup
$directory = "\\clatsop.co.clatsop.or.us\data\Applications\SurveyorData\survey\Scanned Surveys\AA_INDEXED_SURVEYS" #Path\Directory to recursively search
$instance = "cc-gis"
$database = "Clatsop"
 
#don't edit the following variables
$table = "dbo.SurveyTable_FromFileSystem"
$loaddate = Get-Date
 
#setup filesystem table if it doesn't exist
Invoke-DbaQuery -SqlInstance $instance -Database $database -Query "SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SurveyTable_FromFileSystem]') AND type in (N'U'))
BEGIN
CREATE TABLE [dbo].[SurveyTable_FromFileSystem] (
[FullName] nvarchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
[FileName] nvarchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
[LastWriteTime] datetime2(7) NULL,
[LoadDate] datetime2(7) NULL)
ON [PRIMARY]
TEXTIMAGE_ON [PRIMARY]
WITH (DATA_COMPRESSION = NONE);
END;"
 
#Begin pulling data
$Datatable = Get-ChildItem -Path $directory -Recurse -File |`
Select-Object -Property FullName, @{ Name = 'FileName'; Expression = {$_.NAME}}, LastWriteTime, @{ Name = 'LoadDate'; Expression = {$loaddate}}
 
#Write dataset to filesystem table
Write-DbaDataTable -SqlInstance $instance -Database $database -Table $table -InputObject $Datatable -Truncate
 
#Execute merge statement to update modified date if record exists but date doesn't match
#Insert record to the multi-version view if a file with the exact same path doesn't exist.
Invoke-DbaQuery -SqlInstance $instance -Database $database -Query "
EXECUTE Clatsop.sde.set_current_version 'dbo.STAGING';

EXECUTE Clatsop.sde.edit_version 'dbo.STAGING',1;

MERGE INTO Clatsop.dbo.SURVEYIMAGES_evw t
USING Clatsop.dbo.SurveyTable_FromFileSystem s ON t.[IMAGE] = s.FULLNAME
WHEN MATCHED AND t.[DateModified] <> s.LASTWRITETIME THEN UPDATE SET t.[DateModified] = s.LASTWRITETIME
WHEN NOT MATCHED THEN INSERT ([Image], [FileName], [DateModified])
VALUES (s.FULLNAME, s.FILENAME, s.LASTWRITETIME);

EXECUTE Clatsop.sde.edit_version 'dbo.STAGING',2;
"