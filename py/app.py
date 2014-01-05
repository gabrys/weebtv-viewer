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
    '/static/grid.js', 'staticGrid',
    '/api/channels.js', 'apiChannels',
    '/api/premium.js', 'apiPremium',
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
        return '\n'.join([
            '<!doctype html>',
            '<html><head><title>Player</title>',
            '<style>html, body, object { display: block; margin: 0; padding: 0; width: 100%; height: 100%; }</style>',
            '<script>',
            '    function refreshVideo() { var p = document.player; if (p.getTime() > 15) { location.reload(); } else { p.Play(); } }',
            '    function toggleFullscreen() { var p = document.player; p.fullscreen = !p.fullscreen; }',
            '</script>',
            '<object id="player" type="video/flv" data="' + mode + '.flv" onEndOfStream="refreshVideo()" onClick="toggleFullscreen()">',
            '    <param autostart="true">',
            '</object>',
            '</html>',
        ])

class playerFlv:
    def GET(self, cid, mode='sd'):
        cid = int(cid)
        hd = mode == 'hd'
        weebtv = WeebTv(config.weebtv_credentials['username'], config.weebtv_credentials['password'])
        params = weebtv.getStreamChannelInfo(cid, hd)

        query = '?r=' + str(params['url']) + '&v=1&p=token&W=' + str(params['ticket'])
        rtmpgw_port = rtmpgw.startOnRandomPort(config.rtmpgw_bin)
        url = 'http://' + config.rtmpgw_host + ':' + str(rtmpgw_port) + '/' + query

        print 'Redirecting to ' + url
        raise web.seeother(url)


class apiChannels:
    def GET(self):
        weebtv = WeebTv(config.weebtv_credentials['username'], config.weebtv_credentials['password'])
        web.header('Cache-control', 'max-age=60')
        web.header('Content-type', 'text/javascript; charset=utf-8')
        return 'WeebTvChannels = ' + json.dumps(weebtv.getChannelList(thumbnails=True)) + ';'

class apiPremium:
    def GET(self):
        weebtv = WeebTv(config.weebtv_credentials['username'], config.weebtv_credentials['password'])
        web.header('Cache-control', 'max-age=60')
        web.header('Content-type', 'text/javascript; charset=utf-8')
        return 'WeebTvPremium = ' + json.dumps(weebtv.isPremium()) + ';'
        


if __name__ == "__main__":
    app.run()

