from libs.redis_custom import redis_client, pubsub
import json
import moviepy.editor as mp
import time
import boto3
import os

s3 = boto3.resource('s3')

pubsub.subscribe('file-convert-channel')
for message in pubsub.listen():
    if message["type"] == "message":
        print(message.get("data"))
        raw_msg = json.loads(message.get("data"))
        raw_msg = raw_msg.get("data")
        bucket = raw_msg.get("bucket")
        file_id = raw_msg.get("file_id")
        file_addr = raw_msg.get("file")
        time.sleep(2)
        redis_client.publish("video-audio." + file_id, json.dumps({"data": {"file_id": file_id, "status": "started"}}))
        clip = mp.VideoFileClip("https://" + bucket + ".s3.amazonaws.com/"+file_addr)
        clip.audio.write_audiofile("temp/"+file_id+".mp3")
        s3.meta.client.upload_file("temp/" + file_id + ".mp3", bucket, "Temp/"+file_id + ".mp3", ExtraArgs={'ACL':'public-read'})
        redis_client.publish("video-audio." + file_id, json.dumps(
            {"data": {"file_id": file_id, "status": "completed",
                      "link": "https://" + bucket + ".s3.amazonaws.com/Temp/" + file_id+".mp3"}}))
        print("msg processed .., file id = ", file_id)
        os.remove("temp/"+file_id+".mp3")
