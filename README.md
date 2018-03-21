[Works best with your microwave.](https://twitter.com/BoredElonMusk/status/539467221740040192)

### How to ...

__Add Videos to the Database?__

    $ docker-compose build
    $ docker-compose run collectvids "important meme videos"

__Deploy the Frontend?__

    $ $(EDITOR) docker-compose.yml
    $ docker-compose build
    $ docker-compose up -d web

### To do

* Better scraping of YouTube videos
* Reduce duplication in `docker-compose.yml`
