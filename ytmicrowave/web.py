
import functools
import io
import json
import random
import re

from flask import Flask, Markup, make_response, redirect, request, render_template
from .database import db_session, select, Video
from . import config

app = Flask(__name__)


def jsonify(func):
  @functools.wraps(func)
  def wrapper(*a, **kw):
    data, code = func(*a, **kw)
    return json.dumps(data), code, {'Content-type': 'application/json'}
  return wrapper



def parse_duration(s):
  """
  Parses a duration string in the form of `X m Y s` (ignoring spaces).
  """

  s = s.replace(' ', '')
  matches = re.findall('(\d+[ms])', s)
  if sum(len(x) for x in matches) != len(s):
    raise ValueError('invalid duration string', matches, s)

  mod = {'m': 60, 's': 1}
  return sum(int(x[:-1]) * mod[x[-1]] for x in matches)


@db_session
def render_videos_svg_graph():
  max_duration = Video.max_duration()
  if max_duration is None:
    return ''  # No videos

  config_max = parse_duration(config.get('web.graph.max_duration', '20m'))
  max_duration = min(max_duration, config_max)
  if max_duration == 0:
    return ''

  out = io.StringIO()
  out.write('<svg height="50px" width="100%" style="background-color: #f2f2f2">')
  out.write('''
      <style type="text/css">
      <![CDATA[
        rect { fill: #0042ff; }
      ]]>
      </style>
  ''')

  scale = lambda x: x
  for start, end in Video.iter_duration_ranges():
    if start > max_duration: break
    w = (end-start+1)/max_duration
    x = start/max_duration
    out.write('<rect width="{w}%" height="100%" x="{x}%" y="0"/>'.format(
      w=scale(w)*100, x=scale(x)*100))

  out.write('</svg>')
  return out.getvalue()


@app.route('/')
@app.route('/<duration>')
@db_session
def index(duration=None):
  video = None
  if duration:
    try:
      seconds = parse_duration(duration)
    except ValueError:
      pass
    else:
      video = Video.select_by_duration(seconds)

  random_video = next(iter(Video.select_random(limit=1)), None)
  if random_video:
    random_duration = '{}m {}s'.format(*divmod(random_video.duration, 60))
  else:
    random_duration = '1m 3s'

  return render_template('index.html',
    notfound=(duration and not video),
    videoid=(video.id if video else None),
    graph=Markup(render_videos_svg_graph()),
    randint=random.randint,
    duration=duration,
    random_duration=random_duration)


@app.route('/api')
@jsonify
@db_session
def api():
  if not request.args.get('duration'):
    return {'error': 'bad request'}, 400
  try:
    duration = parse_duration(request.args['duration'])
  except ValueError:
    return {'error': 'bad request'}, 400

  video = Video.select_by_duration(duration)

  if not video:
    return {'status': 'ok', 'result': None}, 200

  return {'status': 'ok', 'result': video.id, 'duration': video.duration}, 200
