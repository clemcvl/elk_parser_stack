import os
import math
import json
import time
from datetime import datetime
from elasticsearch import Elasticsearch

def create_index(Index, es):
    print(es.indices)
    if not es.indices.exists(IndexName):
        # Setting mappings for index
        mapp = '''
        {
            "settings" : {
                "number_of_replicas" : 0
            },
              "mappings": {
                    "properties": {
                        "date": { "type": "date" }
                    }
                }
        }
        '''
        es.indices.create(Index, body=mapp)
    return es

def insert_to_index(es, index, data):
    print(data)
    es.index(index=index, doc_type='_doc',  body=data)

def get_directory_size(dir):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", dir)
        for entry in os.scandir(dir):
            if entry.is_file(follow_symlinks=False):
                # if it's a file, use stat() function
                total += entry.stat(follow_symlinks=False).st_size
            elif entry.is_dir(follow_symlinks=False):
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(dir)
    except:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def scanDir(folder_path, es, depth=1):
    start_time = time.time()
    subfolders = {}
    data = {}
    # iterate over all the directories inside this path
    if depth > 0 and len(next(os.walk(folder_path))[1]) != 0:
        try:
            for directory in next(os.walk(folder_path))[1]:
                directory_ = os.path.join(folder_path, directory)
                subfolders[os.path.basename(directory_)] = scanDir(directory_, es, depth - 1)
                #print(subfolders[os.path.basename(directory_)])
                data_for_elastic = {
                    'folder_name': os.path.basename(directory_) ,
                    'size': subfolders[os.path.basename(directory_)]['total_size_bit'] / 1000,
                    'date': datetime.now().timestamp() * 1000
                    }
                #print(data_for_elastic)
                #print(es.indices)
                insert_to_index(es, IndexName, data_for_elastic)
        except NotADirectoryError:
            # if `directory` isn't a directory, get the file size then
            subfolders = {}
        except PermissionError:
            # if for whatever reason we can't open the folder, return 0
            subfolders = {}
        data['subfolder'] = subfolders
        if len(subfolders) == 0:
            data['total_size_bit'] = 0
            data['total_size'] = convert_size(0)
    directory_size = get_directory_size(folder_path)
    data['total_size_bit'] = directory_size
    data['total_size'] = convert_size(directory_size)
    data['time'] = round(time.time() - start_time, 2)
    return data

if __name__ == "__main__":
    today = datetime.today().strftime('%Y-%m-%d')
    FolderPath = '/home/chevalier'
    IndexName = f'fresh-index-{today}'
    es_obj = Elasticsearch()
    es_idx = create_index(IndexName, es_obj)
    d = scanDir(FolderPath, es_idx)
    print(json.dumps(d))