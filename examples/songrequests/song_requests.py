import sys, os
from revlo.client import RevloClient
import socket
import time
import os
import yaml
from irc import Irc

def request_songs_to_nightbot(irc, twitch, songs):
  if not songs:
    return
  for song in songs:
    irc.send_message(twitch['channel'], '!songs request {}'.format(song))
    time.sleep(6)

def song_request(redemption):
  return redemption and 'user_input' in redemption and 'song' in redemption['user_input']

def scan_song_redemptions(token, reward_id):
  client = RevloClient(api_key=token)
  songs = []
  ids = []
  for redemption in client.get_redemptions(completed=False):
    if song_request(redemption):
      songs.append(redemption['user_input']['song'])
      client.update_redemption(redemption['redemption_id'], {'completed' : True})
  songs = songs[::-1]
  if songs:
    print("New songs found:{}".format(songs))
  else:
    print("No songs found")
  return songs

def main():
  lines = open('config.yml').read()
  config = yaml.load(lines)
  twitch = config['twitch']
  revlo = config['revlo']

  irc = Irc(twitch)
  token = revlo['api_key']
  reward_id = int(revlo['reward_id'])

  print("Press Ctrl+C to kill the bot")
  try:
    while True:
      songs = scan_song_redemptions(token, reward_id)
      request_songs_to_nightbot(irc, twitch, songs)
      songs=[]
      time.sleep(60)
  except KeyboardInterrupt:
    print("Leaving channel")
  finally:
    irc.leave(twitch['channel'])

if __name__ == '__main__':
  main()
