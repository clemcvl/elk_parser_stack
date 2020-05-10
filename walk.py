import os
from elasticsearch import Elasticsearch
import math

def walklevel(some_dir, level=1):
    total_size = 0
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    mydict = {}
    for dirpath, dirnames, filenames in os.walk(some_dir):
        #print(dirpath, dirnames, filenames)
        mydict[dirpath] = 0
        #yield dirpath, dirnames, filenames
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                #print(f, os.path.getsize(fp))
                mydict[dirpath] += os.path.getsize(fp)
        num_sep_this = dirpath.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirnames[:]
    return mydict

    


def get_size(start_path = '/'):
    total_size = 0
    for dirpath, dirnames, filenames in walklevel(start_path):
        print(dirpath, dirnames, filenames)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

res = walklevel('/mnt')
for key, value in res.iteritems():
    print(key, convert_size(value))
#print(get_size(), 'bytes')