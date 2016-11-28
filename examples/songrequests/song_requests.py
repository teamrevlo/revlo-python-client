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

def scan_song_redemptions(token, reward_id):
  client = RevloClient(api_key=token)
  results = []
  last_redemption_id = get_last_redemption()
  for redemptions_batch in client.get_redemptions():
    redemption_ids = []
    for redemption in redemptions_batch:
      redemption_ids.append(redemption['redemption_id'])
      if redemption['reward_id'] == reward_id:
        if not redemption['refunded'] or not redemption['completed']:
          results.append(redemption['user_input']['song'])
          last_redemption_id = max(last_redemption_id, redemption['redemption_id'])
    if last_redemption_id >= max(redemption_ids):
      break
  update_last_redemption(last_redemption_id)
  results.reverse()
  print("New songs found:{}".format(results))
  return results

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
