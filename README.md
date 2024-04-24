A Web Crawler that crawls University domains for useful information about the said university.



**NB**
this crawler is the first step to a bigger project: AI for education. the script here is simply for data gathering purposes.

**WORK FLOW**
-- Reads the university domains from the UK_Universities file and, 
-- grabs 300 Urls from within the domain ensuring that all links are not broken and that links belong to the domain
-- Download text data, page titles from all 300 urls as txt files while logging activities.
-- makes use of multithreading to perform tasks


**UK_Universities**
-- file contains list of Universities (University Domain) across  the United kingdom.
-- it is worth noting that this list could be changed and another passed into crawler

**OUTPUT**
--downloaded data is stored as text files in folders
