"""
Uses the Youtube API to pull videos from a search query and store them in a
database, only assocating the video ID with the video's length.
"""

import queue
import threading
import sys
from .concurrent import ThreadHub
from .config import config
from .database import db_session, commit, Video
from .youtube import YouTubeAPI

yt = YouTubeAPI(config['youtube']['developer_key'])

def get_argument_parser():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('query', help='The YouTube Search Query.')
  return parser

def main():
  parser = get_argument_parser()
  args = parser.parse_args()

  search_params = {'q': args.query, 'maxResults': 50}
  response = yt.search(**search_params)
  items = queue.Queue(maxsize=20)
  stop = threading.Event()

  def get_worker(hub):
    nonlocal response
    while not hub.stopped():
      for item in response['items']:
        # Try to add the item to the queue, and check again if the threadhub
        # was stopped.
        while True:
          try: items.put(item, True, 0.1)
          except queue.Full:
            if hub.stopped(): break
          else: break
        if hub.stopped(): break
      if hub.stopped(): break
      if not response['items']:
        print('Note: No more items. End of search results?')
        print(response)
        break
      search_params['pageToken'] = response['nextPageToken']
      response = yt.search(**search_params)
    # Only add the sentinel if the hub hasn't been stopped, otherwise we
    # may not have a worker that can consume the element.
    if not hub.stopped(): items.put(None)

  @db_session
  def store_worker(hub):
    items_total = response['pageInfo']['totalResults']

    print('Query:', args.query)
    print('Total search results:', items_total)

    while not hub.stopped():
      item = items.get()
      if item is None: break # Sentinel

      video_id = item['id']['videoId']
      video = Video.get(id=video_id)
      if video:
        print('{} (SKIP)'.format(video_id))
        continue

      try:
        duration = yt.video(video_id)['contentDetails']['duration']
      except yt.InvalidVideoID:
        print('{} (INVALID ID)'.format(video_id))
        continue
      duration = yt.parse_duration(duration)
      print('{} ({}s): {}'.format(video_id, duration, item['snippet']['title']))
      Video(id=video_id, duration=duration)
      commit()

  with ThreadHub() as hub:
    hub.start(get_worker)
    hub.start(store_worker)

if __name__ == '__main__':
  sys.exit(main())
