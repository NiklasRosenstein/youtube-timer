
import re
import requests
from urllib.parse import urljoin


class YouTubeAPI:

  class InvalidVideoID(ValueError):
    pass

  def __init__(self, api_key, ssl=True):
    self.api_key = api_key
    self.ssl = ssl
    self.base_url = 'http{}://www.googleapis.com/youtube/v3/'.format('s' if self.ssl else '')

  def request(self, url, *args, **kwargs):
    url = urljoin(self.base_url, url)
    if not url.endswith('/'):
      url += '/'
    check = kwargs.pop('check', True)
    method = kwargs.pop('method', 'get')
    params = kwargs.get('params', None)
    if params is None:
      params = {}
    else:
      params = dict(params)
      kwargs['params'] = params
    params['key'] = self.api_key
    response = requests.request(method, url, *args, **kwargs)
    if check:
      response.raise_for_status()
    return response

  def video(self, video_id, parts=['snippet', 'contentDetails']):
    params = {'part': ','.join(parts), 'id': video_id}
    data = self.request('videos', params=params).json()
    if len(data['items']) != 1:
      raise self.InvalidVideoID(video_id)
    return data['items'][0]

  def search(self, **params):
    params.setdefault('part', 'snippet')
    params.setdefault('type', 'video')
    return self.request('search', params=params).json()

  @staticmethod
  def parse_duration(duration):
    """
    Parses content duration as described here:
    https://developers.google.com/youtube/v3/docs/videos#contentDetails.duration
    """

    match = re.match('P(\d+D)?T(\d+H)?(\d+M)?(\d+S)?', duration)
    if not match:
      raise ValueError('invalid duration: {!r}'.format(duration))
    days, hours, minutes, seconds = [int(x[:-1]) if x else 0 for x in match.groups()]
    return seconds + minutes * 60 + hours * 3600 + days * 86400
