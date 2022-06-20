from pickletools import long1
from urllib.parse import urlparse
from hashlib import md5
from pymongo import MongoClient
import datetime
class tiny_url:
    _BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _long_url = ''
    _tiny_url = ''
    _i = 0 # linear probing variable
    _client = MongoClient("mongodb+srv://admin:admin@tinyurlcluster.w89ns.mongodb.net/?retryWrites=true&w=majority")
    db = _client.tinyUrlDB.tinyUrlCollection
    def __init__(self,url):
        self._long_url = url

    def b62_encode(self,url):
        #hashing a string from hex then to b62 which always gives 22 size of string
        #but we only make use of first 7 characters for our url as we get around
        #62 ^ 7 tiny urls which we can use for 11 years even if we generate 1 per sec

        # we don't get O(1) searching like in has bcoz we only use first 7 chars which
        # isn't an acutal hash
        hash_str = []
        hex = md5(url.encode('UTF-8')).hexdigest()
        deci = int(hex,16) + self._i
        while deci > 0 :
            X = self._BASE62[deci % 62]
            hash_str.append(X)
            deci //= 62
        self._tiny_url = ''.join(hash_str[0:7])

    def printUrl(self):
        print("Tiny URL is ",self._tiny_url)

    def does_exist(self):
        cur = self.db.find_one({"tiny_url":self._tiny_url})
        if cur:
            if cur["long_url"]==self._long_url:
                print("Url Already Exist")
                self._tiny_url = cur["tiny_url"]
                self.printUrl()
            else:
                while not self.does_collide(): # linear probing
                    self._i += 1
                self._tiny_url = self.b62_encode()
                self.add()
        else:
            self.add()
            self.printUrl()

    def does_collide(self):
        cur = self.db.find_one({"tiny_url":self._tiny_url})
        if cur:
            return 1
        return 0

    def add(self):
        self.db.insert_one({"tiny_url":self._tiny_url,
                            "long_url":self._long_url,
                            "created_at":datetime.datetime.now()})
        print("Url Added successfully")
                     
    
    


input_url = str(input("Enter Url\n"))
obj = tiny_url(input_url)

obj.b62_encode(input_url)
obj.does_exist()
del obj

