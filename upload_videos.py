import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

# YouTube API information
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secrets.json"

def get_authenticated_service():
    # Use the client_secrets.json file to perform OAuth authentication
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)

    # Use run_local_server() instead of run_console()
    credentials = flow.run_local_server(port=0)  # Starts a local server for authentication
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def upload_video(youtube, video_file, title, description, category_id, tags):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",  # Can be "private", "unlisted" or "public"
            "madeForKids": False  # Always set to False, not made for kids
        }
    }
    # MediaFileUpload is used to upload the video file
    media_body = googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True)

    # Make the request to upload the video
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media_body
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading {video_file}: {int(status.progress() * 100)}%")
    print(f"Upload complete for {video_file}!")

def upload_videos_from_folder(folder_path):
    youtube = get_authenticated_service()

    for video_file in os.listdir(folder_path):
        if video_file.endswith(".mp4"):  # Upload only .mp4 files
            video_path = os.path.join(folder_path, video_file)
            title = os.path.splitext(video_file)[0]  # Use the file name as the title
            description = ""  # Add your own description
            category_id = "22"  # "22" is the category ID for "People & Blogs"
            tags = []  # Add your own tags

            # Upload video with madeForKids set to False
            upload_video(youtube, video_path, title, description, category_id, tags)

# Example usage:
folder_path = input("Enter the folder path with videos to upload: ")
upload_videos_from_folder(folder_path)
