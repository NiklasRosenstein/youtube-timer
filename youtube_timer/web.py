
import functools
import json
from flask import Flask, make_response, redirect, request, render_template
from .database import db_session, select, Video

app = Flask(__name__)

def jsonify(func):
  @functools.wraps(func)
  def wrapper(*a, **kw):
    data, code = func(*a, **kw)
    return json.dumps(data), code, {'Content-type': 'application/json'}
  return wrapper


@app.route('/api')
@jsonify
@db_session
def api():
  if 'seconds' not in request.args:
    return {'error': 'bad request'}, 400
  try:
    seconds = int(request.args['seconds'])
  except ValueError:
    return {'error': 'bad request'}, 400

  video = Video.select_with_duration(seconds)

  if not video:
    return {'status': 'ok', 'result': None}, 200

  return {'status': 'ok', 'result': video.id, 'duration': video.duration}, 200


@app.route('/')
@db_session
def index():
  if 'duration' in request.args:
    try:
      duration = [int(x) for x in request.args['duration'].split(':')]
      if len(duration) > 3: raise ValueError
    except ValueError:
      return render_template('index.html')
    seconds = sum(x*y for x, y in zip(duration[::-1], [1, 60, 3600]))
    video = Video.select_with_duration(seconds)
    if not video:
      return render_template('index.html', notfound=True)
    return redirect('https://youtu.be/' + video.id)

  return render_template('index.html')
