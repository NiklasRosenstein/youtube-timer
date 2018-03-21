
import pony.orm
from pony.orm import commit, db_session, select
from .config import config

db = pony.orm.Database(**config['database'])

class Video(db.Entity):
  id = pony.orm.PrimaryKey(str)
  duration = pony.orm.Required(int)  # in seconds

  @classmethod
  def select_by_duration(cls, duration):
    video = select(x for x in cls if x.duration == duration).random(1)
    if video:
      return video[0]
    # TODO: If no video with the exact duration was found, try to select
    #       one with a different but close duration.
    return None

  @classmethod
  def iter_duration_ranges(cls):
    """
    Returns an iterator of tuples in the form of (start, begin) for every
    consecutively occupied range of duration in seconds in the database.
    """

    start = None
    end = None
    for duration in select(x.duration for x in cls).order_by(1):
      if start is None: start = end = duration
      elif duration == (end+1): end = duration
      else: yield (start, end); start = None

  @classmethod
  def max_duration(cls):
    return select(x.duration for x in cls).order_by(-1).first()


db.generate_mapping(create_tables=True)
