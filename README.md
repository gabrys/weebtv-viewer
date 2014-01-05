weebtv-viewer
=============

WEEB.TV viewer using API exposed by WEEB.TV for XBMC

Components
----------

Server-side:

1. This Python web app (as wsgi or fastcgi app) with its dependencies
2. Webserver: Apache, nginx, lighttpd, or anything else that talks fastcgi or wsgi
3. rtmpgw (version 2.4 is required) daemon running on the same host (this can help: http://github.com/gabrys/rtmpgwd)

Client-side:

1. A web browser (for example Firefox)
2. A plugin to watch HTTP streams (media-geckoplayer works nicely)

Installation on Debian/Ubuntu (using integrated webserver)
----------------------------------------------------------

Get deps:

    sudo apt-get install python-webpy python-bs4

Additionally for python < 2.6:

    sudo apt-get install python-simple-json

Get code:

    git clone https://github.com/gabrys/weebtv-viewer.git

Set up the config file:

    cd weebtv-viewer/py
    cp config.py.sample config.py

Edit the file. At least update the static dir path.

Start the app from the weebtv-viewer directory:

    cd ..
    py/app.py

Open a web browser and navigate to http://localhost:8080/
You should see a grid of WEEB.TV channels.

Install rtmpdump package (with rtmpgw binary). It needs to be version 2.4:

    sudo apt-get install rtmpdump

Start rtmpgw in a separate terminal window:

    /usr/sbin/rtmpgw --sport 8777

Install gecko-mediaplayer package to be able to view HTTP streams directly from a browser:

    sudo apt-get install gecko-mediaplayer

Restart browser, go to http://localhost:8080/ and click one of the channels. The output in the terminals should help you debug if everything goes OK.

That was the minimal setup. Additionally you may want to:

* enter your e-mail and password to the config.py to get the logged in and premium channels
* configure the application to run from Apache or Lighttpd
* use rtmpgwd to start rtmpgw as a daemon
