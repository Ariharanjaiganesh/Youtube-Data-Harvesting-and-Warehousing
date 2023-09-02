# YouTube Data Harvesting and Warehousing:
  > Using Python, MYSQL, MongoDB, Streamlit and Googleapiclient


## Project Descriptions:

- The problem statement is to create a Streamlit application that allows users to access and analyze data from __Multiple YouTube Channels__:
   
   - Ability to input a _**YouTube channel ID**_ and retrieve all the relevant data using _**Google API**_.
  
        __| Channel name | Subscribers | Total video count | Playlist ID | Video ID | Likes| Comments of each video |__
     
   - Option to store the data in a MongoDB database as a data lake.
   - Ability to collect data for up to 10 different YouTube channels and store them in the data lake by clicking a button.
   - Option to select a channel name and migrate its data from the data lake to a SQL database as tables.
   - Ability to search and retrieve data from the SQL database using different search options, including joining tables to get channel details.

 ## Basic Requirements:

- __[Python 3.11](https://www.google.com/search?q=docs.python.org)__
- __[googleapiclient](https://www.google.com/search?q=googleapiclient+python)__ 
- __[mysql_connector](https://www.google.com/search?q=mysql+connector)__ 
- __[Pandas](https://www.google.com/search?q=python+pandas)__
- __[Streamlit](https://www.google.com/search?q=python+streamlit)__
- __[Numpy](https://www.google.com/search?q=numpy)__ 
- __[pymongo](https://www.google.com/search?q=pymongo)__
- __[requests](https://www.google.com/search?q=requests)__

## General workflow of this Project:
![PhonePe Design](https://github.com/Ariharanjaiganesh/Youtube-Data-Harvesting-and-Warehousing/blob/main/work%20flow%20image.png)

## Demo Video of the Project 

(https://drive.google.com/file/d/1_inmZT_kYc70K1bNIREHZ35BpKkaaYKN/view?usp=sharing)



## Features

- Harvests data from YouTube videos, channels, and comments.
- Stores the collected data in a structured data warehouse.
- Supports regular updates to keep the data up-to-date.
- Provides data analysis and reporting capabilities.
- User-friendly command-line interface.


## Data Harvesting
The data harvesting process involves querying the YouTube API to gather information about videos, channels, and comments. The harvested data includes video titles, descriptions, view counts, likes, dislikes, channel information, comment text, and more.

## Data Warehousing
The harvested data is stored in a structured data warehouse, allowing for efficient querying and analysis. The warehouse schema is designed to support data integration and reporting.
