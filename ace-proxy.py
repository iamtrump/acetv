#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask import send_from_directory
import os
import requests
import re
import time
import httplib
import json

engine_url = "http://localhost:6878"
download_path = "/tmp"
retry_time = 90
seconds_between_retries = 3

channels_url = os.environ["PLAYLIST"]
channels_path = download_path+"/channels.json"


app = Flask(__name__)
@app.route("/")
def get_index():
  if not os.path.exists(channels_path) or (time.time()-os.path.getmtime(channels_path) > 180):
    print("Channels refresh needed. Getting...")
    r = requests.get(channels_url)
    if r.status_code != httplib.OK:
      print("Failed. HTTP code "+str(r.status_code))
    else:
      with open(channels_path, "w") as fd:
        fd.write(r.content)
  with open(channels_path) as fd:
    channels = json.loads(fd.read())["channels"]
  play = request.args.get("play")
  if play == None:
    play = channels[0]["url"]
  play_name = play
  for channel in channels:
    if channel["url"] == play:
      play_name = channel["name"]
  return(render_template("index.html.j2", play=play, play_name=play_name, channels=channels))

@app.route("/<stream_id>.m3u8")
def get_manifest(stream_id):
  ace_url = os.path.dirname(request.base_url)
  print("Getting manifest...")
  for i in range(int(retry_time / seconds_between_retries)):
    print("Attempt #"+str(i+1)+"...")
    r = requests.get(engine_url+"/ace/manifest.m3u8?id="+stream_id, timeout=20)
    if r.status_code == httplib.OK:
      print("OK")
      break
    print("Failed. HTTP code "+str(r.status_code))
    time.sleep(seconds_between_retries)
  manifest = re.sub(engine_url+"[a-z0-9/]+/([0-9]+\.ts)", ace_url+"/"+stream_id+"/"+r"\1", r.text)

  #Download chunks:
  chunk_link = re.compile("^http://")
  lines = r.text.split("\n")
  for l in lines:
    if chunk_link.match(l):
      file_name = l.split("/")[-1]
      file_path = download_path+"/"+stream_id+"/"+file_name
      if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
      if not os.path.isfile(file_path):
        print("Getting "+l+"...")
        for i in range(int(retry_time / seconds_between_retries)):
          print("Attempt #"+str(i+1)+"...")
          r = requests.get(l, timeout=20)
          if r.status_code == httplib.OK:
            print("OK")
            break
          print("Failed. HTTP code "+str(r.status_code))
          time.sleep(seconds_between_retries)
        with open(file_path, "w") as fd:
          fd.write(r.content)
      else:
        print("Exists "+l+".")

  print("Reurning manifest")
  resp = Response(manifest)
  resp.headers['Content-Type'] = "application/x-mpegURL"
  return resp

@app.route("/<stream_id>/<chunk_name>.ts")
def get_chunk(stream_id, chunk_name):
  return send_from_directory(download_path+"/"+stream_id+"/", chunk_name+".ts")

if __name__ == "__main__":
  app.run(host='0.0.0.0')
