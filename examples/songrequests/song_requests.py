import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib'))
from revlo_client import RevloClient
import socket
import time
import os
from configparser import ConfigParser
from irc import Irc

LAST_REWARD_REDEEMED_FILENAME = './last_redemption_id.dat'

def request_songs_to_nightbot(irc, twitch, songs):
  if not songs:
    return
  for song in songs:
    irc.send_message(twitch['channel'], '!songs request {}'.format(song))
    time.sleep(6)

def get_last_redemption():
  with open(LAST_REWARD_REDEEMED_FILENAME) as f:
    try:
      i = f.read()
      return int(i)
    except:
      return 0

def update_last_redemption(new_redemption_id):
  with open(LAST_REWARD_REDEEMED_FILENAME, 'w') as f:
    f.write(str(new_redemption_id))

def redeemable(redemption, last_redemption_id):
  return (not redemption['refunded'] or not redemption['completed']) and last_redemption_id < redemption['redemption_id']

def song_request(redemption):
  return redemption and 'user_input' in redemption and 'song' in redemption['user_input']

def scan_song_redemptions(token, reward_id):
  client = RevloClient(api_key=token)
  last_redemption_id = get_last_redemption()
  songs = []
  ids = []
  for redemptions_batch in client.get_redemptions():
    results = []
    for redemption in redemptions_batch:
      if redeemable(redemption, last_redemption_id):
        ids.append(redemption['redemption_id'])
        if song_request(redemption):
          results.append({"song": redemption['user_input']['song'], "id": redemption['redemption_id']})
    songs.extend([x['song'] for x in results if x['id'] > last_redemption_id][::-1])
    print(ids)
    if ids:
      if max(ids) > last_redemption_id:
        last_redemption_id = max(ids)
        update_last_redemption(last_redemption_id)
        print("New songs found:{}".format(songs))
        return songs
  if ids:
    if max(ids) > last_redemption_id:
      last_redemption_id = max(ids)
      update_last_redemption(last_redemption_id)
      print("New songs found:{}".format(songs))
  return songs

def main():
  config = ConfigParser()
  config.read('config.ini')
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
      time.sleep(60)
  except KeyboardInterrupt:
    print("Leaving channel")
  finally:
    irc.leave(twitch['channel'])

if __name__ == '__main__':
  main()
