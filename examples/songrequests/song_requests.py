import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib'))
from revlo_client import RevloClient
import socket
import time
import os
from configparser import ConfigParser
from irc import Irc

LAST_REWARD_REDEEMED_FILENAME = './last_redemption_id.dat'

def request_songs_to_nightbot(songs):
  if not songs:
    return
  irc = Irc(twitch)
  sock = irc.get_irc_socket_object()
  sock.settimeout(8)
  for song in songs:
    irc.send_message(twitch['channel'], '!songs request {}'.format(song))
    time.sleep(3)
  irc.leave(twitch['channel'])

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

def scan_song_redemptions(token, reward_id):
  client = RevloClient(api_key=token)
  results = []
  last_redemption_id = get_last_redemption()
  for redemptions_batch in client.get_redemptions():
    for redemption in redemptions_batch:
      if redemption['reward_id'] == reward_id:
        if redemption['completed']:
          return results.reverse()
        elif last_redemption_id >= redemption['reward_id']:
          return results.reverse()
        elif not redemption['refunded']:
          results.append(redemption['user_input'])
          last_redemption_id = max(last_redemption_id, redemption['redemption_id'])
          update_last_redemption(last_redemption_id)
  return results.reverse()

def main():
  config = ConfigParser()
  config.read('config.ini')
  twitch = config['twitch']
  revlo = config['revlo']

  token = revlo['api_key']
  reward_id = int(revlo['reward_id'])
  while True:
    songs = scan_song_redemptions(token, reward_id)
    request_songs_to_nightbot(songs)
    time.sleep(60)

if __name__ == '__main__':
  main()
