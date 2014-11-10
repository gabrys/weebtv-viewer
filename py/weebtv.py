#!/usr/bin/env python

import urllib, urllib2, subprocess, sys
import simplejson as json
import cgi
from bs4 import BeautifulSoup

channelUrl = 'http://weeb.tv/api/getChannelList&option=online-alphabetical'
playerUrl = 'http://weeb.tv/api/setplayer'
thumbsUrl = 'http://weeb.tv/channels/live'

class WeebTv(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.cache = {'channels': None, 'thumbs': None}


    def __getChannelDict(self):
        if self.cache['channels']:
            return self.cache['channels']

        data = None
        if self.username and self.password:
            data = urllib.urlencode({'username': self.username, 'userpassword': self.password})

        response = urllib2.urlopen(channelUrl, data)
        channels = [(chInfo['cid'], chInfo) for chInfo in json.loads(response.read()).itervalues()]
        channelDict = {}
        for channel in channels:
            chInfo = channel[1]
            if chInfo['channel_title'] is None:
                chInfo['channel_title'] = chInfo['channel_name']
            channelDict[str(channel[0])] = chInfo
        self.cache['channels'] = channelDict
        return channelDict


    def getDataFromWebsite(self):
        if self.cache['thumbs']:
            return self.cache['thumbs']

        headers = None
	if self.username and self.password:
            cookie_username = urllib.urlencode({'weeb-tv_username': self.username})
	    cookie_password = urllib.urlencode({'weeb-tv_userpassword': self.password})
            headers = {'Cookie': cookie_username + ';' + cookie_password}

        reqUrl = urllib2.Request(thumbsUrl, None, headers)
        soup = BeautifulSoup(urllib2.urlopen(reqUrl))
        thumbs = {}
        for channel in soup.select('ul.channels li'):
            name = channel.select('p > span > a')[0].text
            url = channel.select('img')[0]['data-original']
            thumbs[name] = url

        if soup.select('li.icon.premium'):
            premium = True
        else:
            premium = False

        self.cache['thumbs'] = (thumbs, premium)
        return (thumbs, premium)


    def channelInfo(self, channel):
        return self.__getChannelDict()[str(channel)]


    def getChannelList(self):
        chList = []
        channelsInfo = self.__getChannelDict()
        for channel in sorted([(chInfo['channel_title'].replace('*', '').strip().lower(), chInfo) for chInfo in channelsInfo.itervalues()]):
            chList.append(channel[1])
        return chList


    def getStreamChannelInfo(self, cid, hd=False):
        values = {'platform': 'XBMC', 'cid': cid}
        if self.username and self.password:
            values['username'] = self.username
            values['userpassword'] = self.password
        headers = {'User-Agent' : 'XBMC'}
        data = urllib.urlencode(values)
        #print 'requesting data', {'url': playerUrl, 'data': data, 'headers': headers}
        reqUrl = urllib2.Request(playerUrl, data, headers)
        response = urllib2.urlopen(reqUrl)
        resLink = response.read()

        #print resLink

        rawparams = cgi.parse_qs(resLink)

        params = {
            'status':   rawparams["0"][0],
            'premium':  rawparams["5"][0],
            'rtmpLink': rawparams["10"][0],
            'playPath': rawparams["11"][0],
            'ticket':   rawparams["73"][0],
        }

        url = params['rtmpLink'] + '/' + params['playPath']
        if hd:
            url += 'HI'

        params['url'] = url
        params['hd'] = hd
        return params

