
import functools
import io
import json
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
  Parses a duration string in the form of M:S and returns it as seconds.
  """

  duration = [int(x) for x in s.split(':')]
  if len(duration) > 2:
    raise ValueError('invalid duration string')
  return sum(x*y for x, y in zip(duration[::-1], [1, 60]))


@db_session
def render_videos_svg_graph():
  max_duration = Video.max_duration()
  if max_duration is None:
    return ''  # No videos

  config_max = parse_duration(config.get('web.graph.max_duration', '20:00'))
  max_duration = min(max_duration, config_max)

  out = io.StringIO()
  out.write('<svg height="50px" width="100%">')
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
@db_session
def index():
  videoid = None

  if 'duration' in request.args:
    try:
      seconds = parse_duration(request.args['duration'])
    except ValueError:
      pass
    else:
      video = Video.select_by_duration(seconds)
      if video:
        videoid = video.id

  graph = render_videos_svg_graph()
  notfound = ('duration' in request.args and videoid is None)
  return render_template('index.html', notfound=notfound, videoid=videoid,
    graph=Markup(graph))


@app.route('/api')
@jsonify
@db_session
def api():
  if 'duration' not in request.args:
    return {'error': 'bad request'}, 400
  try:
    duration = parse_duration(request.args['duration'])
  except ValueError:
    return {'error': 'bad request'}, 400

  video = Video.select_by_duration(duration)

  if not video:
    return {'status': 'ok', 'result': None}, 200

  return {'status': 'ok', 'result': video.id, 'duration': video.duration}, 200
