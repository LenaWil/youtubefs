#!/usr/bin/env python

__author__      = "Vishal Patil"
__copyright__   = "Copyright 2007 - 2008, Vishal Patil"
__license__     = "MIT"

import time
import logging
import urllib2
import sys
import youtube.api
import xml.dom.minidom
from youtube.api import gdataTime2UnixTime


class YoutubeProfile:
    def __init__(self):
        self.ctime  =  0 
        self.mtime  =  0 
        self.age    =   "" 
        self.username   = ""
        self.gender     = ""
        self.location   = "" 

    def getData(self):
        data =   (\
                "Username       = %s\n" +\
                "Gender         = %s\n" +\
                "Age            = %s\n" +\
                "Location       = %s\n" +\
                "Published time = %s\n" +\
                "Updated time   = %s\n") %\
        (self.username,self.gender,self.age,self.location,\
            str(self.ctime),str(self.mtime))

        return data.encode('ascii')

    def __str__(self):
        return self.getData()       


class YoutubePlaylist:
    def __init__(self,id):
        self.id = id
        self.title = ""  
        self.ctime = long(time.time())
        self.mtime = long(time.time())
        splits           = self.id.split('/')
        self.playlist_id = splits[len(splits) - 1]
        self.url    = youtube.api.PLAYLIST_VIDEOS_URI\
            % self.playlist_id   
   
    def getVideos(self):
        videos = []
        logging.debug("YoutubePlaylist getting videos from %s", self.url)

        try:
            urlObj = urllib2.urlopen(self.url)
            data   = urlObj.read()
        except:
            logging.critical("Unable to open " + self.url)
            print youtube.api.PLAYLIST_VIDEOS_ERROR % self.playlist_id 

        dom = xml.dom.minidom.parseString(data)
        try:
            for entry in dom.getElementsByTagName('entry'):
                id = (entry.getElementsByTagName('id')[0]).firstChild.data
                video = YoutubeVideo(id)
                logging.debug("Video id: " + video.id)

                video.title =  \
                    (entry.getElementsByTagName('title')[0]).firstChild.data
                logging.debug("Video title: " + video.title)

                if entry.hasAttribute('published'):
                    video.ctime = \
                        gdataTime2UnixTime((entry.getElementsByTagName('published')[0]).firstChild.data)
                    logging.debug("Video ctime: " + str(video.ctime))

                video.mtime = \
                    gdataTime2UnixTime((entry.getElementsByTagName('updated')[0]).firstChild.data)
                logging.debug("Video mtime: " + str(video.mtime))

                mediaGroup      = (entry.getElementsByTagName('media:group')[0])
                mediaContent    = (mediaGroup.getElementsByTagName('media:content'))

                if mediaContent and \
                        mediaContent[0].getAttribute('type') \
                            == "application/x-shockwave-flash":
                    video.url   =  mediaContent[0].getAttribute('url')
                    video.type  =  mediaContent[0].getAttribute('type')
                if (video.url != ""):        
                    videos.append(video)
        except Exception,inst:
            logging.critical("Invalid video XML format: " + \
                        str(inst))
        return videos

class YoutubeVideo:
    def __init__(self,id):
        self.id = id
        self.title = ""  
        self.ctime = 0 
        self.mtime = 0 
        self.url   = ""
        self.type  = ""
        splits           = self.id.split('/')
        self.video_id = splits[len(splits) - 1]

    def getContents(self):
        content = youtube.api.META_TAG % (self.url)
        content = content.encode('ascii')
        return content        

    def __str__(self):
        str = self.id + "\n" + \
            self.title + "\n" + \
            self.url   
        return str
            
class YoutubeSubscription(YoutubePlaylist):
    def __init__(self,id):
        self.id = id
        self.title = ""  
        self.ctime = long(time.time())
        self.mtime = long(time.time())

class YoutubeUser:
    def __init__(self,username):
        self.__username__ = username

    def getSubscriptions(self):
        subscriptions = []
        url = youtube.api.SUBSCRIPTIONS_URI % (self.__username__)
        logging.debug("YoutubeUser getting subscriptions from %s",url)

        try:
            urlObj = urllib2.urlopen(url)
            data   = urlObj.read()
        except Exception,inst:
            logging.critical("Unable to open " + url)
            logging.critical(str(inst))

        dom = xml.dom.minidom.parseString(data)
        try:
            for entry in dom.getElementsByTagName('entry'):
                id = (entry.getElementsByTagName('id')[0]).firstChild.data
                sub = YoutubeSubscription(id)
                sub.title =  \
                    (entry.getElementsByTagName('title')[0]).firstChild.data
                logging.debug("Subscription title: " + sub.title)

                sub.ctime = \
                    gdataTime2UnixTime((entry.getElementsByTagName('published')[0]).firstChild.data)
                logging.debug("Subscription ctime: " + str(sub.ctime))

                sub.mtime = \
                   gdataTime2UnixTime((entry.getElementsByTagName('updated')[0]).firstChild.data)
                logging.debug("Subscription mtime: " + str(sub.mtime))
                subscriptions.append(sub)

                feedLink = entry.getElementsByTagName('gd:feedLink')
                if feedLink:
                    sub.url = feedLink[0].getAttribute('href')
                    logging.debug("Subscription url " + str(sub.url))                
                subscriptions.append(sub)
        except Exception, inst:            
            logging.critical("Invalid subscription XML format " + \
                        str(inst))

        return subscriptions


    def getPlaylists(self):
        
        playlists = []
        url = youtube.api.PLAYLISTS_URI % (self.__username__)
        logging.debug("YoutubeUser getting playlists from %s",url)

        try:
            urlObj = urllib2.urlopen(url)
            data   = urlObj.read()
        except Exception,inst:
            logging.critical("Unable to open " + url)
            logging.critical(str(inst))

        dom = xml.dom.minidom.parseString(data)
        try:
            for entry in dom.getElementsByTagName('entry'):
                id = (entry.getElementsByTagName('id')[0]).firstChild.data
                pl = YoutubePlaylist(id)
                logging.debug("Playlist id: " + pl.id)

                pl.title =  \
                    (entry.getElementsByTagName('title')[0]).firstChild.data
                logging.debug("Playlist title: " + pl.title)

                pl.ctime = \
                    gdataTime2UnixTime((entry.getElementsByTagName('published')[0]).firstChild.data)
                logging.debug("Playlist ctime: " + str(pl.ctime))

                pl.mtime = \
                   gdataTime2UnixTime((entry.getElementsByTagName('updated')[0]).firstChild.data)
                logging.debug("Playlist mtime: " + str(pl.mtime))
                playlists.append(pl)
        except Exception, inst:            
            logging.critical("Invalid playlist XML format " + \
                        str(inst))

        return playlists        

    """
        Returns a YoutubePlaylist object containing all
        of the user's favourite videos.
    """
    def getFavourities(self):
        videos = []
        url    = youtube.api.FAVOURITES_URI\
            % self.__username__
        favourities = YoutubePlaylist(url) 
        favourities.url = url
        return favourities 
    
    def getProfile(self):
        url = youtube.api.PROFILE_URI % (self.__username__)
        logging.debug(url)

        try:
            urlObj = urllib2.urlopen(url)
            data   = urlObj.read()
        except:
            logging.critical("Unable to get profile for " + 
                self.__username__)
            print youtube.api.PROFILE_URI_ERROR % self.__username__ 
            sys.exit(1) 

        profile = YoutubeProfile()
        dom = xml.dom.minidom.parseString(data)
        logging.debug(data)
        try:
           for entry in dom.getElementsByTagName('entry'):
               profile.ctime = \
                   (entry.getElementsByTagName('published')[0]).firstChild.data
               profile.ctime = youtube.api.gdataTime2UnixTime(profile.ctime)
               logging.debug("Profile ctime: " + str(profile.ctime))

               profile.mtime = \
                   (entry.getElementsByTagName('updated')[0]).firstChild.data
               profile.mtime = youtube.api.gdataTime2UnixTime(profile.mtime)
               logging.debug("Profile mtime: " + str(profile.mtime))
               
               profile.age    =   (entry.getElementsByTagName('yt:age')[0]).firstChild.data 
               profile.username   = (entry.getElementsByTagName('yt:username')[0]).firstChild.data  
               profile.gender     = (entry.getElementsByTagName('yt:gender')[0]).firstChild.data 
               profile.location   = (entry.getElementsByTagName('yt:location')[0]).firstChild.data  
               logging.debug(("Profile: %s\n" % (profile)));
        except:            
           logging.critical("Invalid profile XML format " + \
                       str(sys.exc_info()[0]))
        return profile

    def getContacts(self):
        pass
 
