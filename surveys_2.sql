SELECT CAST(s.OBJECTID_1 AS INTEGER) AS OID ,
s.SURVEYID ,
s.SHAPE ,
s.Client ,
s.SurveyDate ,
s.SYEAR ,
s.Firm ,
s.SurveyorKe ,
s.BookPage ,
X.HYPERLINK1 ,X.HYPERLINK2 ,X.HYPERLINK3 ,X.HYPERLINK4 ,X.HYPERLINK5 ,
X.HYPERLINK6 ,X.HYPERLINK7 ,X.HYPERLINK8 ,X.HYPERLINK9 ,X.HYPERLINK10 
FROM CLATSOP.dbo.SURVEYS_evw s 
LEFT OUTER JOIN (
    SELECT DOCUMENTNAME,
    [1] HYPERLINK1,
    [2] HYPERLINK2 ,
    [3] HYPERLINK3                 ,
    [4] HYPERLINK4                 ,
    [5] HYPERLINK5                 ,
    [6] HYPERLINK6                 ,
    [7] HYPERLINK7                 ,
    [8] HYPERLINK8                 ,
    [9] HYPERLINK9                 ,
    [10] HYPERLINK10                 
    FROM (SELECT ROW_NUMBER() OVER( PARTITION BY DOCUMENTNAME ORDER BY [IMAGE]) RN ,
    REPLACE ( [IMAGE],
    '\\clatsop.co.clatsop.or.us\data\Applications\SurveyorData\survey\Scanned Surveys\AA_INDEXED_SURVEYS\' 
    ,'https://delta.co.clatsop.or.us/surveys/') AS [IMAGE],
        DOCUMENTNAME FROM CLATSOP.dbo.SURVEYIMAGES_evw) AS SourceTable PIVOT (MAX([IMAGE]) 
        FOR RN IN( [1],[2],[3],[4],[5],[6],[7],[8],[9],[10])) 
            AS PivotTable) 
            X  ON X.DOCUMENTNAME = s.DocumentNa 