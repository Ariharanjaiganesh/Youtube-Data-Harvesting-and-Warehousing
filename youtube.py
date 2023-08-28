# need full packages for project ---------------------------------------------
import streamlit as st
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import pandas as pd
import mysql.connector
import numpy as np


# data retrival function ---------------------------------------------


def channel_data(all_id):
    API_KEY = "AIzaSyDbj4NY5ZVrAxh9Tknh9fv6sXKs-Cop6n0"
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    cha_res = youtube.channels().list(
        part='contentDetails,snippet,statistics',
        id=all_id).execute()
    global ch_ti1
    ch_ti1 = []
    for i in cha_res['items']:
        ch_id = i['id']
        channel_link = f"https://www.youtube.com/channel/{ch_id}"
        global ch_title
        ch_title = i['snippet']['title']
        global ch_playlist
        ch_playlist = i['contentDetails']['relatedPlaylists']['uploads']
        CreatedAt = i['snippet']['publishedAt']
        global Subcount
        Subcount = i['statistics']['subscriberCount']
        global TotalViews
        global TotalVideos
        TotalViews = i['statistics']['viewCount']
        TotalVideos = i['statistics']['videoCount']
        global ch_logo
        ch_logo = i['snippet']['thumbnails']['medium']['url']
        global da
        da = {
            "Channel_id": ch_id, "Channel_Name": ch_title, "Playlist_id": ch_playlist, "Created_Date": CreatedAt,
            "Subcribers": Subcount, "TotalViews": TotalViews, "TotalVideos": TotalVideos,
            "Thumbnail": ch_logo, "Channel_link": channel_link
        }
        ch_ti1.append(da)

    return ch_ti1


def get_video_ids(playlist_id):
    API_KEY = "AIzaSyDbj4NY5ZVrAxh9Tknh9fv6sXKs-Cop6n0"
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    global video_ids
    video_ids = []

    try:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50
        )

        counter = 0  # Counter for tracking the number of video IDs

        while request and counter < 100:  # Stop when 100 video IDs are obtained
            response = request.execute()
            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])
                counter += 1

            request = youtube.playlistItems().list_next(request, response)

    except HttpError as e:
        error_message = e.content.decode("utf-8")
        print("An error occurred:", error_message)

    return video_ids[:100]


def get_video_details(video_ids):
    API_KEY = "AIzaSyDbj4NY5ZVrAxh9Tknh9fv6sXKs-Cop6n0"
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    # video_ids = video_ids[:100]

    global all_video_stats
    all_video_stats = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50])
        )
        response = request.execute()

        for video in response['items']:
            ch_id = video['snippet']['channelId']
            Video_Id = video['id']
            Title = video['snippet']['title']
            Published_date = video['snippet']['publishedAt']

            try:
                Views = video['statistics']['viewCount']
                Likes = video['statistics']['likeCount']
                Comments = video['statistics']['commentCount']

                all_video_stats.append(
                    {"Channel_id": ch_id, "Video_id": Video_Id, "Video_Title": Title, "Uploaded_Date": Published_date,
                     "Total_Views": Views, "Total_Likes": Likes,
                     "Total_Comments": Comments})
            except KeyError:
                # Skip the item if any of the required keys are missing
                continue

    return all_video_stats


def comment_data(vid_lis):
    API_KEY = "AIzaSyDbj4NY5ZVrAxh9Tknh9fv6sXKs-Cop6n0"
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    comments = []
    for vids in vid_lis:
        try:
            ch_response = youtube.videos().list(
                part='snippet',
                id=vids).execute()

            for video in ch_response['items']:
                ch_id = video['snippet']['channelId']
                vid_title = video['snippet']["title"]
                Channel_title = video['snippet']["channelTitle"]

            response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=vids,
                maxResults=30,
            ).execute()

            video_comments = []
            for item in response['items']:

                comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
                # reply_count = item['snippet']["totalReplyCount"]

                repl = []
                if 'replies' in item:
                    replies = item['replies']['comments']
                    for reply in replies:
                        reply_text = reply['snippet']['textOriginal']
                        repl.append(reply_text)

                else:
                    repl = ["No reply"]

                video_comments.append({"Comments": comment, "Replies": repl})
            comments.append(
                {"Channel_id": ch_id, "Video_id": vids, "Video_title": vid_title, "Comments": video_comments})

        except HttpError as e:
            if e.resp.status == 403:
                pass

    return comments


def metric(Subcount, TotalViews, TotalVideos):
    col1, col2, col3 = st.columns(3)
    col1.metric("Total subscribe : ", Subcount)
    col2.metric("Total Views : ", TotalViews)
    col3.metric("Total video: ", TotalVideos)


def tab(ch1_doc, vi1_doc, com1_doc):
    tab1, tab2, tab3 = st.tabs(["Channel data", "Video data", "Comments data"])
    with tab1:
        ch_jso = ch1_doc
        st.write(ch_jso)
    with tab2:
        vi_jso = vi1_doc
        st.write(vi_jso)
    with tab3:
        co_jso = com1_doc
        st.write(co_jso)


# data convert to dataframe --------------------------------------


def single_channel_df(channel_data, vid_data):
    # channel df
    channel_df = pd.DataFrame(channel_data)
    channel_df[['Subcribers', 'TotalViews', 'TotalVideos']] = channel_df[
        ['Subcribers', 'TotalViews', 'TotalVideos']].astype(np.int64)
    channel_df['Created_Date'] = pd.to_datetime(channel_df['Created_Date']).dt.strftime('%d-%m-%Y')
    # video df
    video_df = pd.DataFrame(vid_data)
    video_df[['Total_Views', 'Total_Likes', 'Total_Comments']] = video_df[
        ['Total_Views', 'Total_Likes', 'Total_Comments']].astype(np.int64)
    video_df['Uploaded_Date'] = pd.to_datetime(video_df['Uploaded_Date']).dt.strftime('%d-%m-%Y')

    return channel_df, video_df


# mongodb insert part -----------------------------------------------------------------------------


def mdb_insert(keyword, channel_Data, video_Data, comments_data):
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi

    uri = "mongodb+srv://ariharanjaiganesh:ariharan141107@cluster0.joxd3ek.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client.youtubeproject

    collection_names = db.list_collection_names()

    # Find the first available name by appending a number
    new_collection_name = keyword
    counter = 1
    while new_collection_name in collection_names:
        new_collection_name = f"{keyword}{counter}"
        counter += 1
    # Create the collection with the new name

    collection = db[new_collection_name]
    Channel_Data = {"_id": f"{new_collection_name}-Channel", "Channels_Data": channel_Data}
    Videos_Data = {"_id": f"{new_collection_name}-Videos", "Videos_Data": video_Data}
    Comments_Data = {"_id": f"{new_collection_name}-Comments", "Comments_Data": comments_data}
    ## insert at document level
    coll_Data = [Channel_Data, Videos_Data, Comments_Data]

    for col in coll_Data:
        collection.insert_one(col)
    return new_collection_name


def mdb_queries_data(coll_name):
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi

    uri = "mongodb+srv://ariharanjaiganesh:ariharan141107@cluster0.joxd3ek.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client.youtubeproject

    collection = db[f'{coll_name}']
    ch_doc = collection.find_one({"_id": f"{coll_name}-Channel"})
    vi_doc = collection.find_one({"_id": f"{coll_name}-Videos"})
    com_doc = collection.find_one({"_id": f"{coll_name}-Comments"})

    return ch_doc, vi_doc, com_doc


# mysql insert function ----------------------------------------


def mysql_insert(channel_df, video_df):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()

    cursor.execute("use banana")

    ch_schema = """
        CREATE TABLE IF NOT EXISTS Channel_Table (
            ch_id INT AUTO_INCREMENT PRIMARY KEY,
            Channel_Id VARCHAR(30),
            Channel_Name VARCHAR(40),
            Playlist_Id VARCHAR(30),
            Created_Date DATETIME,
            Subscribers BIGINT,
            Total_Views BIGINT,
            Total_Videos BIGINT
        )
    """

    vi_schema = """
        CREATE TABLE IF NOT EXISTS Videos_Table (
            vid_id INT AUTO_INCREMENT PRIMARY KEY,
            Channel_Id INT,
            Video_Id VARCHAR(20),
            Video_Title VARCHAR(100),
            Uploaded_Date DATETIME,
            Total_Views BIGINT,
            Total_Likes BIGINT,
            Total_Comments BIGINT,
            FOREIGN KEY (Channel_Id) REFERENCES Channel_Table (ch_id)
        )
    """

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")  # Enable foreign key support

    cursor.execute(ch_schema)
    cursor.execute(vi_schema)

    for index, row in channel_df.iterrows():
        # Insert values into Channel_Table
        cursor.execute("""
            INSERT IGNORE INTO Channel_Table (Channel_Id, Channel_Name, Playlist_Id, Created_Date, Subscribers, Total_Views, Total_Videos)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['Channel_id'],
            row['Channel_Name'],
            row['Playlist_id'],
            row['Created_Date'],
            row['Subcribers'],
            row['TotalViews'],
            row['TotalVideos']
        ))
        # Retrieve the generated Channel_Id
        channel_id = cursor.lastrowid

        # Insert values into Videos_Table
        for vindex, vrow in video_df[video_df['Channel_id'] == row['Channel_id']].iterrows():
            cursor.execute("""
                INSERT IGNORE INTO Videos_Table (Channel_Id, Video_Id, Video_Title, Uploaded_Date, Total_Views, Total_Likes, Total_Comments)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                channel_id,
                vrow['Video_id'],
                vrow['Video_Title'],
                vrow['Uploaded_Date'],
                vrow['Total_Views'],
                vrow['Total_Likes'],
                vrow['Total_Comments']
            ))
    # Commit the changes
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()


# query part -------------------------------------------------------


def mysql_single_query(chn_name):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = conn.cursor()
    cursor.execute("use banana")

    cu_q = f"SELECT * FROM Channel_Table WHERE CHANNEL_NAME IN ('{chn_name}')"
    ch_df = pd.read_sql(cu_q, conn)  ##
    # needed to isolate ch_id from chl that are selected
    ch_id_qu = ch_df['Channel_Id'].to_list()[0]
    # needed to select based upon the ch_id_qu

    vi_qu = f"SELECT a.Video_Id,a.Video_Title,a.Uploaded_Date,a.Total_Views,a.Total_Likes,a.Total_Comments FROM Videos_Table a JOIN Channel_Table b ON a.Channel_Id = b.Ch_id WHERE b.Channel_Id = '{ch_id_qu}'"

    vi_df = pd.read_sql(vi_qu, conn)

    return ch_df, vi_df


# UI ---------------------------------------------------------

page_title = "Youtube Data Harvesting and Warehousing "
page_icon = ":money_with_wings:"
layout = "wide"

channel_names = ['coding is fun', 'maxy', 'vaadhiyar', 'Internet Made Coder', "Alex The Analyst", "BWF TV",
                 "cherry vlogs", "Curious Freaks", "Enowaytion Plus", "pyros girl", "Others"]

channel_ids = ["UCZjRcM1ukeciMZ7_fvzsezQ", "UCbimE7uQT3yz2gsVLPriAVg", "UCaqkok_r96V3PaieOOXcmxg",
               "UCcJQ96WlEhJ0Ve0SLmU310Q", "UC7cs8q-gJRlGwj4A8OmCmXg", "UChh-akEbUM8_6ghGVnJd6cQ",
               "UCTxfYLmM82aMCovQexkRxFQ", "UCvhU9qF1xtUsFXdKrcJxbFA", "UC_rD0WTWsygn28me13EqbkA",
               "UCGWmWu-_oBTyUe8_wN7Gjsg"]

# page configration ---------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

option = st.selectbox(
    'select the channel name you like',
    channel_names)

if option == channel_names[10]:
    st.markdown("#    ")
    st.write("### Enter YouTube Channel_ID below :")
    ch_id = st.text_input(
        "Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')

ex = st.button("Extract Data")

if ex:
    if option == channel_names[0]:
        channel_data = channel_data(channel_ids[0])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[0]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[1]:
        channel_data = channel_data(channel_ids[1])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[1]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[2]:
        channel_data = channel_data(channel_ids[2])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[2]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[3]:
        channel_data = channel_data(channel_ids[3])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[3]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[4]:
        channel_data = channel_data(channel_ids[4])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[4]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[5]:
        channel_data = channel_data(channel_ids[5])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[5]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[6]:
        channel_data = channel_data(channel_ids[6])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[6]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[7]:
        channel_data = channel_data(channel_ids[7])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[7]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[8]:
        channel_data = channel_data(channel_ids[8])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[8]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))
    elif option == channel_names[9]:
        channel_data = channel_data(channel_ids[9])
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = channel_names[9]
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))

    else:
        channel_data = channel_data(ch_id)
        v = get_video_ids(ch_playlist)
        video_data = get_video_details(v)
        comment_data = comment_data(video_data)
        st.header("Channel Details")
        st.image(ch_logo, width=150)
        metric(da.get("Subcribers"), da.get("TotalViews"), da.get("TotalVideos"))
        keyword = ch_title
        new_collection_name = mdb_insert(keyword, channel_data, video_data, comment_data)
        ch_doc, vi_doc, com_doc = mdb_queries_data(new_collection_name)
        data = {
            "cha_data": ch_doc,
            "vide_data": vi_doc,
            "comm_data": com_doc
        }
        tab(data.get("cha_data"), data.get("vide_data"), data.get("comm_data"))

my = st.button("Upload to MYSQL")

if my:
    if option == channel_names[0]:
        channel_data = channel_data(channel_ids[0])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)
    elif option == channel_names[1]:
        channel_data = channel_data(channel_ids[1])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[2]:
        channel_data = channel_data(channel_ids[2])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[3]:
        channel_data = channel_data(channel_ids[3])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[4]:
        channel_data = channel_data(channel_ids[4])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[5]:
        channel_data = channel_data(channel_ids[5])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[6]:
        channel_data = channel_data(channel_ids[6])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[7]:
        channel_data = channel_data(channel_ids[7])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[8]:
        channel_data = channel_data(channel_ids[8])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)

    elif option == channel_names[9]:
        channel_data = channel_data(channel_ids[9])
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database and create the table")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)
    else:
        channel_data = channel_data(ch_id)
        v = get_video_ids(ch_playlist)
        vid_data = get_video_details(v)
        comment_data = comment_data(vid_data)
        channel_df, vid_df = single_channel_df(channel_data, vid_data)
        mysql_insert(channel_df, vid_df)
        st.success("success fully to connect the sql database ")
        ch_df, vi_df = mysql_single_query(ch_title)
        tab1, tab2 = st.tabs(["Channel table", "video table"])
        with tab1:
            st.write(ch_df)
        with tab2:
            st.write(vi_df)






