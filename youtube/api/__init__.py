#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='youtube.api.log',
                    filemode='w')

PLAYLISTS_URI       = "http://gdata.youtube.com/feeds/" +\
                        "api/users/%s/playlists"

PLAYLISTS_URI_ERROR = "Unable to get the playlists for %s"

PLAYLIST_VIDEOS_URI = "http://gdata.youtube.com/feeds/api/" +\
                        "playlists/%s"
PLAYLIST_VIDEOS_ERROR = "Unable to get the videos for %s"

PROFILE_URI         = "http://gdata.youtube.com/feeds/"+\
                        "api/users/%s"
 
PROFILE_URI_ERROR = "Unable to access the profile for %s"

CONTACTS_URI        = "http://gdata.youtube.com/feeds/" +\
                        "api/users/%s/contacts" 

SUBSCRIPTIONS_URI   = "http://gdata.youtube.com/feeds/" +\
                        "api/users/%s/subscriptions"

def getXMLText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
