
import pony.orm
from pony.orm import commit, db_session, select
from .config import config

db = pony.orm.Database(**config['database'])

class Video(db.Entity):
  id = pony.orm.PrimaryKey(str)
  duration = pony.orm.Required(int)  # in seconds

  @classmethod
  def select_with_duration(cls, duration):
    video = select(x for x in cls if x.duration == duration).random(1)
    if video:
      return video[0]
    # TODO: If no video with the exact duration was found, try to select
    #       one with a different but close duration.
    return None

db.generate_mapping(create_tables=True)
