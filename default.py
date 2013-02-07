"""
 Copyright (c) 2012, 2012 Popeye

 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""

import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import os
from xml.dom.minidom import parseString

import tv

__settings__ = xbmcaddon.Addon(id='plugin.video.nzbtv')
if not (__settings__.getSetting("firstrun")):
    __settings__.setSetting("firstrun", "1")
__language__ = __settings__.getLocalizedString

USERDATA_PATH = xbmc.translatePath(__settings__.getAddonInfo("profile"))
REMOTE = __settings__.getSetting("remote_channels")
if (__settings__.getSetting("enable_local_channels").lower() == "true"):
    LOCAL = unicode(__settings__.getSetting("local_channels"), 'utf-8')
else:
    LOCAL = ""
CACHE_TIME = int(__settings__.getSetting("cache_time"))*3600

TV = tv.Tv(USERDATA_PATH, REMOTE, LOCAL, CACHE_TIME)
FAV = tv.Favorite(USERDATA_PATH)

NEWZNAB_SITE = __settings__.getSetting("newznab_site")
NEWZNAB = "plugin://plugin.video.newznab"
NEWZNAB_SEARCH_RAGEID = "%s?mode=newznab&newznab=search_rageid&index=%s" % (NEWZNAB, NEWZNAB_SITE)

MODE_CHANNEL = "channel"
MODE_CHANNEL_FAV = "channel_fav"
MODE_CHANNEL_FAV_LIST = "channel_fav_list"
MODE_CHANNEL_FAV_ADD = "channel_fav_add"
MODE_CHANNEL_FAV_DEL = "channel_fav_del"
MODE_SHOW = "show"
MODE_SHOW_FAV = "show_fav"
MODE_SHOW_FAV_LIST = "show_fav_list"
MODE_SHOW_FAV_ADD = "show_fav_add"
MODE_SHOW_FAV_DEL = "show_fav_del"

def list_channels(channels, mode=MODE_CHANNEL):
    #Build channel list
    for name, rageids in channels:
        add_posts({'title' : '%s' % name,}, mode=mode, \
                  url="&nzbtv_rageids=%s" % quote_plus(','.join(rageids)))
    the_end()

def list_shows(rageids, mode=MODE_SHOW):
    for rageid in rageids.split(','):
        if rageid != '':
            url = "%s&rageid=%s" % (NEWZNAB_SEARCH_RAGEID, rageid) 
            add_posts({'title' : '%s' % TV.show[rageid],}, mode=mode, url=url, \
                      thumb=TV.thumb[rageid], fanart=TV.fanart[rageid], rageid=rageid)
    the_end()

def the_end():
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True, cacheToDisc=True)

def list_show_fav():
    rageids = []
    for rageid, nothing in FAV.show.items():
        rageids.append(rageid)
    list_shows(','.join(rageids), mode=MODE_SHOW_FAV)

def show_fav_add(rageid):
    FAV.show_cache.set_value(rageid, '')

def show_fav_del(rageid):
    FAV.show_cache.del_key(rageid)
    xbmc.executebuiltin("Container.Refresh")

def channel_fav_add(channel_name, rageids):
    FAV.channel_cache.set_value(channel_name, [x for x in rageids.split(',')])
    if len(FAV.channel.items()) == 0:
        xbmc.executebuiltin("Container.Refresh")

def channel_fav_del(channel_name):
    FAV.channel_cache.del_key(channel_name)
    xbmc.executebuiltin("Container.Refresh")

def add_posts(info_labels, **kwargs):
    url = kwargs.get('url', '')
    mode = kwargs.get('mode', None)
    thumb = kwargs.get('thumb', '')
    fanart = kwargs.get('fanart', '')
    isFolder = (kwargs.get('isFolder', 'true') == "true")
    listitem=xbmcgui.ListItem(info_labels['title'], thumbnailImage=thumb)   
    listitem.setProperty("Fanart_Image", fanart)
    xurl = ''
    if mode == MODE_CHANNEL:
        cmurl = "&nzbtv_channel=%s%s" % (quote_plus(info_labels['title']), url)
        cm = []
        cm.append(cm_build("Add to favorite channels", MODE_CHANNEL_FAV_ADD, cmurl))
        listitem.addContextMenuItems(cm, replaceItems=True)
    if mode == MODE_CHANNEL_FAV:
        mode = MODE_CHANNEL
        cmurl = "&nzbtv_channel=%s%s" % (quote_plus(info_labels['title']), url)
        cm = []
        cm.append(cm_build("Remove favorite", MODE_CHANNEL_FAV_DEL, cmurl))
        listitem.addContextMenuItems(cm, replaceItems=True)
    if mode == MODE_SHOW:
        cmurl = "&rageid=%s" % kwargs.get('rageid', '')
        cm = []
        cm.append(cm_build("Add to favorite shows", MODE_SHOW_FAV_ADD, cmurl))
        listitem.addContextMenuItems(cm, replaceItems=True)
    if mode == MODE_SHOW_FAV:
        mode = MODE_SHOW
        cmurl = "&rageid=%s" % kwargs.get('rageid', '')
        cm = []
        cm.append(cm_build("Remove favorite", MODE_SHOW_FAV_DEL, cmurl))
        listitem.addContextMenuItems(cm, replaceItems=True)
    if mode != MODE_SHOW:
        xurl = "%s?mode=%s" % (sys.argv[0], mode)
    xurl = "%s%s" % (xurl, url)
    listitem.setInfo(type="Video", infoLabels=info_labels)
    listitem.setPath(xurl)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem, isFolder=isFolder)

def cm_build(label, mode, url):
    command = "XBMC.RunPlugin(%s?mode=%s%s)" % (sys.argv[0], mode, url)
    out = (label, command)
    return out

# FROM plugin.video.youtube.beta  -- converts the request url passed on by xbmc to our plugin into a dict  
def get_parameters(parameterString):
    commands = {}
    splitCommands = parameterString[parameterString.find('?')+1:].split('&')
    for command in splitCommands: 
        if (len(command) > 0):
            splitCommand = command.split('=')
            name = splitCommand[0]
            value = splitCommand[1]
            commands[name] = value
    return commands

def quote_plus(name):
    if isinstance(name, unicode):
        return urllib.quote_plus(name.encode('utf-8'))
    else:
        return urllib.quote_plus(name)

def unquote_plus(name):
    if isinstance(name, unicode):
        return urllib.unquote_plus(name)
    else:
        return unicode(urllib.unquote_plus(name), 'utf-8')

if (__name__ == "__main__" ):
    if (not sys.argv[2]):
        if len(FAV.channel.items()) > 0:
            add_posts({'title' : '- Favorite channels',}, mode=MODE_CHANNEL_FAV_LIST, url="")
        if len(FAV.show.items()) > 0:
            add_posts({'title' : '- Favorite shows',}, mode=MODE_SHOW_FAV_LIST, url="")
        list_channels(TV.channel.items())
    else:
        params = get_parameters(sys.argv[2])
        get = params.get
        if get("mode")== MODE_CHANNEL:
            list_shows(unquote_plus(get('nzbtv_rageids')))
        if get("mode")== MODE_CHANNEL_FAV_LIST:
            list_channels(FAV.channel.items(), mode=MODE_CHANNEL_FAV)
        if get("mode")== MODE_CHANNEL_FAV_ADD:
            channel_fav_add(unquote_plus(get('nzbtv_channel')), unquote_plus(get('nzbtv_rageids')))
        if get("mode")== MODE_CHANNEL_FAV_DEL:
            channel_fav_del(unquote_plus(get('nzbtv_channel')))
        if get("mode")== MODE_SHOW_FAV_LIST:
            list_show_fav()
        if get("mode")== MODE_SHOW_FAV_ADD:
            show_fav_add(unquote_plus(get('rageid')))
        if get("mode")== MODE_SHOW_FAV_DEL:
            show_fav_del(unquote_plus(get('rageid')))
