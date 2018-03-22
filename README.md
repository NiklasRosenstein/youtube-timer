
Try out the YouTube Microwave here: https://ytmicrowave.niklasrosenstein.com/

[Inspired by "BoredElonMusk"](https://twitter.com/BoredElonMusk/status/539467221740040192).

<img align="center" src="https://i.imgur.com/nBXaFsC.png">

__Features__

* Shows a graph of videos available for a duration (from 0s to 20m)
* Plays a microwave bell sound after the video

### Initialization/Deployment

__Add Videos to the Database__

    docker-compose build
    docker-compose run collectvids "get schwifty"

__Deploy the Frontend__

    $(EDITOR) docker-compose.yml
    docker-compose build
    docker-compose up -d web
