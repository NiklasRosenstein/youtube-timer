## YouTube Microwave

Give our SAMSUNG YouTube Microwave a try: https://ytmicrowave.niklasrosenstein.com/

Elon said it's a [good idea](https://twitter.com/BoredElonMusk/status/539467221740040192).

__Features__

* Shows a YouTube video instead of a boring timer
* Plays a microwave bell sound after the video
* Displays a graph of videos that have already been scraped from the YouTube
  API into the database -- for some durations a video may not (yet) be
  available

### Initialization/Deployment

__Add Videos to the Database__

    docker-compose build
    docker-compose run collectvids "get schwifty"

__Deploy the Frontend__

    $(EDITOR) docker-compose.yml
    docker-compose build
    docker-compose up -d web
