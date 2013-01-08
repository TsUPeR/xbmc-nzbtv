"""
 Copyright (c) 2012, 2012, 2013 Popeye

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
import xbmcvfs

import pickle
import os

import cache

class Tv:
    def __init__(self, path, url, local_path, cache_time):
        self.path = path
        self.cache = cache.Cache(self.path, cache_time)
        #
        channel_cache = DictCache(self.path, 'channel')
        show_cache = DictCache(self.path, 'show')
        thumb_cache = DictCache(self.path, 'thumb')
        fanart_cache = DictCache(self.path, 'fanart')
        # Load cache
        self.channel = channel_cache.get_dict()
        self.show = show_cache.get_dict()
        self.thumb = thumb_cache.get_dict()
        self.fanart = fanart_cache.get_dict()
        # Check if update is needed
        md5_url = "%s.md5" % url
        md5_path = "%s.md5" % local_path
        local_md5 = DictCache(self.path, 'md5')
        local_md5_dict = local_md5.get_dict()
        if 'md5' in local_md5_dict:
            md5 = local_md5_dict['md5']
        else:
            md5 = '0'
        if xbmcvfs.exists(local_path) and xbmcvfs.exists(md5_path):
            is_channel_xml_local = True
            remote_md5, error = self._read_doc(md5_path)
            print "###3333333"
            print remote_md5
        else:
            is_channel_xml_local = False
            remote_md5, error = self._load_doc(md5_url)
        # Compare md5's
        if (md5 != remote_md5) and remote_md5 is not None:
            local_md5_dict['md5'] = remote_md5
            local_md5.set_dict(local_md5_dict)
            # Update
            if is_channel_xml_local:
                channel_xml, error = self._read_xml(local_path)
            else:
                channel_xml, error = self._load_xml(url)
            if error is None:
                # clear dicts
                self.channel.clear()
                self.show.clear()
                self.thumb.clear()
                self.fanart.clear()
                for chan in channel_xml.getElementsByTagName("Channel"):
                    rageid_list = []
                    for show in chan.getElementsByTagName("Show"):
                        rageid = self._get_node_value(show, 'RageID')
                        rageid_list.append(rageid)
                        self.show[rageid] = self._get_node_value(show, 'Title')
                        self.thumb[rageid] = self._get_node_value(show, 'thumb')
                        self.fanart[rageid] = self._get_node_value(show, 'fanart')
                    self.channel[self._get_node_value(chan, 'name')] = rageid_list
                channel_cache.set_dict(self.channel)
                show_cache.set_dict(self.show)
                thumb_cache.set_dict(self.thumb)
                fanart_cache.set_dict(self.fanart)

    def _get_node_value(self, parent, name):
        try:
            return unicode(parent.getElementsByTagName(name)[0].childNodes[0].data.encode('utf-8'), 'utf-8')
        except:
            return unicode("", 'utf-8')

    def _load_doc(self, url):
        return self.cache.fetch_doc(url)

    def _read_doc(self, path):
        try:
            f = xbmcvfs.File(path)
            obj = f.read()
            f.close()
            error = None
        except:
            obj = None
            error = "failed reading %s" % path
        return obj, error

    def _load_xml(self, url):
        return self.cache.fetch(url)

    def _read_xml(self, path):
        obj, error = self._read_doc(path)
        if error is None:
            return self.cache._parse_string(obj)
        else:
            return None, error

class DictCache:
    def __init__(self, path, name):
        self.cache_path = os.path.join(path, name)
        if not os.path.exists(self.cache_path):
            pickle.dump( dict(), open( self.cache_path, "wb" ) )

    def get_dict(self):
        return pickle.load( open( self.cache_path, "rb" ) )

    def set_dict(self, obj):
            pickle.dump( obj, open( self.cache_path, "wb" ) )

    def get_value(self, key):
        cache_dict = self.get_dict()
        if key in cache_dict:
            return cache_dict[key]
        else:
            return None

    def set_value(self, key, value):
        cache_dict = self.get_dict()
        cache_dict[key] = value
        pickle.dump( cache_dict, open( self.cache_path, "wb" ) )
