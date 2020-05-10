from datetime import datetime
from elasticsearch import Elasticsearch
#timestamp = data.get('@timestamp')
IndexName = 'test-index'
es = Elasticsearch()
if not es.indices.exists(IndexName):
    # Setting mappings for index
    mapping = '''
        {
            "mappings": {
                  "_default_": {
                    "_all": {
                      "enabled": true,
                      "norms": false
                    },
                    "dynamic_templates": [
                      {
                        "message_field": {
                          "path_match": "message",
                          "match_mapping_type": "string",
                          "mapping": {
                            "norms": false,
                            "type": "text"
                          }
                        }
                      },
                      {
                        "string_fields": {
                          "match": "*",
                          "match_mapping_type": "string",
                          "mapping": {
                            "fields": {
                              "keyword": {
                                "type": "keyword"
                              }
                            },
                            "norms": false,
                            "type": "text"
                          }
                        }
                      }
                    ],
                    "properties": {
                      "@timestamp": {
                        "type": "date",
                        "include_in_all": true
                      },
                      "@version": {
                        "type": "keyword",
                        "include_in_all": true
                      }
                    }
                  }
            }
        }
    '''
    es.indices.create(IndexName, ignore=400, body=mapping)

data = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    '@timestamp': '1589046526494'
}
timestamp = datetime.now().isoformat()
print(timestamp)
es.index(index=IndexName, doc_type='system',  body=data)

def get_size(start_path = './some_storage'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size