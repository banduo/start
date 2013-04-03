#!/usr/bin/python
import cgi, cgitb
from xml.dom import minidom
import urllib
import Queue
import threading
import random
import time

API = "http://api.flickr.com/services/rest/?format=rest&method="
GETPHOTOS = "flickr.photosets.getPhotos"
GETINFO = "flickr.photos.getInfo"
API_KEY = "&api_key=1d4744c61dbc7621aefa68441dcbdb51"


class Producer(threading.Thread):
    def __init__(self, queue, photoset):
        threading.Thread.__init__(self)
        self.queue = queue
        self.photoset = str(photoset)
      
    def run(self):
        try:
            url = API + GETPHOTOS + API_KEY + "&photoset_id=" + self.photoset
            page = urllib.urlopen(url) # get photo ids in this photo set
            data = page.read()
            d = minidom.parseString(data) 
            root = d.documentElement
            photos = root.getElementsByTagName("photo")
        except:
            print "<p><font color='red'>Producer cannot open photo set %s</font></p>" % self.photoset
        else:
            for photo in photos:
                photo_id = photo.getAttribute("id")
                self.queue.put(photo_id)
                print "<p>Producer added photo %s to queue</p>" % photo_id
                time.sleep( random.randrange( 2 ) )
        
        print "<p><font color='red'>Producer finished scanning photo set %s</font></p>" % self.photoset
        

class Consumer(threading.Thread):
    def __init__(self, queue, nums):
        threading.Thread.__init__(self)
        self.queue = queue
        self.nums = int(nums)
    
    def run( self ):
        for i in range( self.nums ):
            try:
                photo_id = str(self.queue.get())
            except Queue.Empty:
                pass
            else:
                tag = True # started
                print "<p>Consumer attempted to get information of photo %s</p>" % photo_id
                try:
                    url = API + GETINFO + API_KEY + "&photo_id=" + photo_id
                    page = urllib.urlopen(url)
                    data = page.read()
                    d = minidom.parseString(data) 
                    root = d.documentElement  
                    owner = root.getElementsByTagName("owner")[0]
                    username = owner.getAttribute("username")
                    title = root.getElementsByTagName("title")[0].firstChild.nodeValue
                    print "<p><font color='blue'><strong>%s</strong> uploaded photo %s, the title is <strong>%s</strong></font></p>" % (username, photo_id, title)
                except Exception, e:
                    print "<p><font color='red'>Cannot get information of photo %s</font></p>" % photo_id
                    

form = cgi.FieldStorage()

print "Content-type:text/html\n"
print "<html>"
print "<head>"
print "<title>Parse Flickr Photo Sets</title>"
print "</head>"
print "<body>"

photoset = form.getvalue('photoset')

if photoset != None:
    print "<a href='./start.cgi'>Back</a>"
    
    url = API + GETPHOTOS + API_KEY + "&photoset_id=" + str(photoset)
    page = urllib.urlopen(url) # get loop times of consumer
    data = page.read()
    d = minidom.parseString(data) 
    root = d.documentElement
    nums = root.getElementsByTagName("photoset")[0].getAttribute("total")

    queue = Queue.Queue()
    producer = Producer(queue, photoset)
    consumer = Consumer(queue, nums)
    producer.start()
    consumer.start()

    producer.join()
    consumer.join()

else:
    print "<p>Please enter a photo set ID from flickr</p>"

    print "<form action='./start.cgi' method='get'>"
    print "<input type='text' name='photoset' /></br>"
    print "</br><input type='submit' value='Start!'>"
    print "</form>"

print "</body>"
print "</html>"
