#!/usr/bin/env python
from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import send_from_directory
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import json
import os
import re

engine_url = "http://localhost:6878"
download_dir = "/tmp"
channels_path = download_dir+"/channels.json"
channels_url = os.environ["PLAYLIST"]
channels_refresh_interval = os.environ["PLAYLIST_INTERVAL"]
preferred_lang = os.environ["PREFERRED_LANG"]

def requests_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
  session = session or requests.Session()
  retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('http://', adapter)
  session.mount('https://', adapter)
  return session

def get_piece(url):
  response = requests_retry_session().get(url)
  return response

def channel_name(channel):
  return channel["name"].lower()

def get_channel_name(ace_id, channels):
  name = ace_id
  for channel in channels:
    if channel["url"] == ace_id:
      name = channel["name"]
  return name

def get_channels():
  if not os.path.exists(channels_path) or (time.time()-os.path.getmtime(channels_path) > channels_refresh_interval):
    r = get_piece(channels_url)
    channels = sorted(json.loads(r.text)["channels"], key = channel_name)
    with open(channels_path, "w") as fd:
      fd.write(json.dumps(channels))

def read_channels():
  with open(channels_path) as fd:
    channels = json.loads(fd.read())
  return channels

def get_manifest(ace_id):
  r = get_piece(engine_url+"/ace/manifest.m3u8?id="+ace_id+"&preferred_audio_language="+preferred_lang)
  m3u8 = re.findall(r"https?://.*\.m3u8",r.text)
  while len(m3u8) > 0: # playlist in playlist situation
    r = get_piece(m3u8[0])
    m3u8 = re.findall(r"https?://.*\.m3u8",r.text)
  manifest = r.text
  return manifest

def return_manifest(ace_id, manifest):
  manifest = re.sub(engine_url+".+/([^/]+\.ts)", ace_id+"/"+r"\1", manifest)
  return manifest

def get_chunks(ace_id, manifest):
  chunks = re.findall(r"https?://.*\.ts", manifest) 
  for chunk in chunks:
    chunk_name = chunk.split("/")[-1]
    chunk_path = download_dir+"/"+ace_id+"/"+chunk_name
    if not os.path.exists(os.path.dirname(chunk_path)):
      os.makedirs(os.path.dirname(chunk_path))
    if not os.path.isfile(chunk_path):
      r = get_piece(chunk)
      with open(chunk_path, "w") as fd:
        fd.write(r.content)

app = Flask(__name__)
@app.route("/")
def get_index():
  get_channels()
  channels = read_channels()
  play = request.args.get("play")
  if play == None:
    play = channels[0]["url"]
  play_name = get_channel_name(play, channels)
  play_link = os.path.dirname(request.base_url)+"/"+play+".m3u8"
  return(render_template("index.html.j2", play=play, play_name=play_name, play_link=play_link, channels=channels))

@app.route("/<ace_id>.m3u8")
def get_m3u8(ace_id):
  original_manifest = get_manifest(ace_id)
  get_chunks(ace_id, original_manifest)
  manifest = return_manifest(ace_id, original_manifest)
  resp = Response(manifest)
  resp.headers["Content-Type"] = "application/x-mpegURL"
  return resp

@app.route("/<stream_id>/<chunk_name>.ts")
def get_ts(stream_id, chunk_name):
  return send_from_directory(download_dir+"/"+stream_id+"/", chunk_name+".ts")

if __name__ == "__main__":
  app.run(host='0.0.0.0')
