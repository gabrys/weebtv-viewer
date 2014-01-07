#!/usr/bin/env python

try:
    import json
except:
    import simplejson as json
import os, sys
import web
from weebtv import WeebTv
import rtmpgw
import config

urls = (
    '/', 'staticIndex',
    '/static/app.js', 'staticApp',
    '/static/grid.png', 'staticGrid',
    '/api/channels.js', 'apiChannels',
    '/api/website.js', 'apiWebsite',
    '/player/([0-9]+)/(hd|sd).html', 'playerHtml',
    '/player/([0-9]+)/(hd|sd).flv', 'playerFlv',
)
app = web.application(urls, globals())

class staticIndex:
    def GET(self):
        web.header('Content-type', 'text/html; charset=utf-8')
        web.header('Cache-control', 'max-age=600')
        return open(config.static_dir + '/index.html').read()

class staticApp:
    def GET(self):
        web.header('Content-type', 'text/javascript; charset=utf-8')
        web.header('Cache-control', 'max-age=600')
        return open(config.static_dir + '/app.js').read()

class staticGrid:
    def GET(self):
        web.header('Content-type', 'image/png')
        web.header('Cache-control', 'max-age=36000')
        return open(config.static_dir + '/grid.png').read()

class playerHtml:
    def GET(self, cid, mode):
        web.header('Content-type', 'text/html; charset=utf-8')
        web.header('Cache-control', 'max-age=600')
        return open(config.static_dir + '/player.html').read()

class playerFlv:
    def GET(self, cid, mode='sd'):
        cid = int(cid)
        hd = mode == 'hd'
        weebtv = WeebTv(config.weebtv_credentials['username'], config.weebtv_credentials['password'])
        params = weebtv.getStreamChannelInfo(cid, hd)

        params = ['-r', params['url'], '-v', '-p', 'token', '-W', str(params['ticket'])]
        rtmpgw_port = rtmpgw.startOnRandomPort(config.rtmpgw_bin, params)
        url = 'http://' + config.rtmpgw_host + ':' + str(rtmpgw_port)

        print 'Redirecting to ' + url
        raise web.seeother(url)


class apiChannels:
    def GET(self):
        weebtv = WeebTv(config.weebtv_credentials['username'], config.weebtv_credentials['password'])
        web.header('Cache-control', 'max-age=60')
        web.header('Content-type', 'text/javascript; charset=utf-8')
        return 'WeebTvChannels = ' + json.dumps(weebtv.getChannelList()) + ';'


class apiWebsite:
    def GET(self):
        weebtv = WeebTv(config.weebtv_credentials['username'], config.weebtv_credentials['password'])
        thumbs, premium = weebtv.getDataFromWebsite()
        web.header('Cache-control', 'max-age=60')
        web.header('Content-type', 'text/javascript; charset=utf-8')
        return 'WeebTvThumbs = ' + json.dumps(thumbs) + '; updateThumbs(); updatePremium(' + json.dumps(premium) + ');'


if __name__ == "__main__":
    app.run()

