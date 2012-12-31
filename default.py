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
import xbmcaddon
import xbmcgui
import xbmcplugin

import os
from xml.dom.minidom import parseString

__settings__ = xbmcaddon.Addon(id='plugin.video.nzbtv')
__language__ = __settings__.getLocalizedString

USERDATA_PATH = xbmc.translatePath(__settings__.getAddonInfo("profile"))
ADDON_PATH = xbmc.translatePath(__settings__.getAddonInfo("path"))
NEWZNAB_SITE = __settings__.getSetting("newznab_site")

NEWZNAB = "plugin://plugin.video.newznab"
NEWZNAB_SEARCH_RAGEID = "%s?mode=newznab&newznab=search_rageid&index=%s" % (NEWZNAB, NEWZNAB_SITE)


MODE_CHANNEL = "channel"
MODE_SHOW = "show"

def list_channels():
    #Build channel list
    for channel_name in channel_name_list():
        add_posts({'title' : '%s' % channel_name,}, mode=MODE_CHANNEL, \
                  url='&nzbtv_channel_name=%s' % quote_plus(channel_name))
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True, cacheToDisc=True)
    
def channel_name_list():
    doc = parseString(read_xml())
    channels = []
    for channel in doc.getElementsByTagName("channel"):
        channels.append(channel.getAttribute("name"))
    return channels

def list_shows(channel_name):
    print channel_name
    doc = parseString(read_xml())
    for channel in doc.getElementsByTagName("channel"):
        print channel.getAttribute("name")
        if channel.getAttribute("name") == channel_name:
            for show in channel.getElementsByTagName("show"):
                show_name = show.getAttribute("name")
                rageid = show.getAttribute("rageid")
                thumb = show.getAttribute("thumb")
                fanart = show.getAttribute("fanart")
                url = "%s&rageid=%s" % (NEWZNAB_SEARCH_RAGEID, rageid) 
                add_posts({'title' : '%s' % show_name,}, mode=MODE_SHOW, url=url, thumb=thumb, fanart=fanart)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True, cacheToDisc=True)

def read_xml():
    #TODO
    #add setting and option to store other xml files
    #from online sources etc
    with open(os.path.join(ADDON_PATH, "channels.xml"), "rb") as out:
        xml = out.read()
    return xml

def add_posts(info_labels, **kwargs):
    url = kwargs.get('url', '')
    mode = kwargs.get('mode', None)
    thumb = kwargs.get('thumb', '')
    fanart = kwargs.get('fanart', '')
    isFolder = (kwargs.get('isFolder', 'true') == "true")
    listitem=xbmcgui.ListItem(info_labels['title'], iconImage="DefaultVideo.png", thumbnailImage=thumb)   
    listitem.setProperty("Fanart_Image", fanart)
    xurl = ''
    if mode != MODE_SHOW:
        xurl = "%s?mode=%s" % (sys.argv[0], mode)
    xurl = "%s%s" % (xurl, url)
    listitem.setInfo(type="Video", infoLabels=info_labels)
    listitem.setPath(xurl)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=xurl, listitem=listitem, isFolder=isFolder)

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
        list_channels()
    else:
        params = get_parameters(sys.argv[2])
        get = params.get
        if get("mode")== MODE_CHANNEL:
            list_shows(get('nzbtv_channel_name'))
