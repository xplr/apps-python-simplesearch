#!/usr/bin/env python
"""
Index and search using XPLR topics

This application permits the following operations :
- Indexing : From an url list, get XPLR prediction on the resources located at these
urls, and indexes the topics returned using the whoosh indexing engine.
- Search : Performs full text search on topics on the index, returning the list of urls
that matched 

Usage: topicssearch.py [options] 

Options:
  -h, --help            show this help message and exit
  -i, --index           Perform topics prediction and indexation
  -q QUERY, --query=QUERY
                        Perform query on topics
  -d INDEXDIR, --indexdir=INDEXDIR
                        whoosh index directory

  Indexing Options:
    These options are needed for indexing (-i).

    -s SOURCEFILE, --source=SOURCEFILE
                        Source list of URLs to index
    -f, --flush         Flush index before indexing
    -K APIKEY, --key=APIKEY
                        XPLR API key
    -H APIHOST, --host=APIHOST
                        XPLR API host
    -P APIPORT, --port=APIPORT
                        XPLR API port
    -S, --ssl           use ssl on XPLR calls


Licence (MIT licence) :
Copyright (c) 2012 Xplr Software Inc

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
import urllib2
import httplib
import json
import os
import shutil
from optparse import OptionParser,OptionGroup

from whoosh.fields import ID,TEXT,Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer

INDEX_DIR="/tmp/topicssearch_index"

# whoosh schema for topics indexation

schema=Schema(uri=ID(stored=True),                       # url of the document
              title=TEXT(stored=True),                   # title returned by XPLR
              topics=TEXT(analyzer=StemmingAnalyzer(),stored=True), # plain text list of topics
              )

class PredictFailed(Exception):
    """ Exception raised when prediction failed for some reason
    """
    pass

def flush():
    """Empty the whoosh index
    """
    try:
        shutil.rmtree(INDEX_DIR)
    except:
        pass

def index(sourcefile):
    """Reads the sourcefile, on every line, calls xplr to
    get prediction on the url, and indexes the url with topics

    :param sourcefile: name of the file containing urls to index, 1 per line
    """
    # creates the index directory if it does not exist
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
    # open the index
    ix = create_in(INDEX_DIR, schema)
    writer = ix.writer()
    try:
        # read links to index
        with open(sourcefile,'r') as s:
            for url in s.readlines():
                url=url.strip()
                print "indexing",url
                try:
                    title, topics = get_prediction(url, topics_count=5)
                    add_document(writer, url, title, topics)
                except PredictFailed, e:
                    print "Prediction Failed:",e
    finally:
        writer.commit()

def get_prediction(url,topics_count=5):
    """ Send an url to xplr and gets the result of the prediction
    as labelled topics, and title

    :param url: the url to be predicted
    :param topics_count: number of topics expected, default 5
    :returns: a tuple (title, topics) where title is extracted
    by XPLR, topics is the list of labels for predicted topics
    """
    # prepare the json to be posted to xplr
    data = '''{"parameters":{
                     "labels":true,
                     "topics_limit":%d,
                     "qualifiers":true,
                     "filters_in":["content_extraction"],
                     "filters_out":["content","title"]
                  },
                  "document":{"uri":"%s"}}
            '''%(topics_count,url)
            
    # Create an urllib2 Request object
    if XPLR_SSL:
        xplrurl='https://%s/predict'%(XPLR_HOST,)
    else:
        xplrurl='http://%s/predict'%(XPLR_HOST,)
    req = urllib2.Request(xplrurl, data)
    
    # Add api key to the HTTP header
    req.add_header('XPLR-Api-Key',XPLR_API_KEY)
    
    # Make the request
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        raise PredictFailed, e
    except httplib.BadStatusLine, e:
        raise PredictFailed, e

    # read the response
    jsonresponse=response.read()

    # parses the json returned by xplr
    try:
        j = json.loads(jsonresponse)
    except UnicodeDecodeError:
        raise PredictFailed, "Wrong Encoding"

    # check the status code
    if j['status']['code']==200:

        # get title
        title = j['body']['extracted_title']

        # get topics labels
        topics=[topic['labels'][0]['label'] for topic in j['body']['topics']]
        return title,topics
    else:
        raise PredictFailed, j['status']['code']
    

def add_document(writer, uri, title, topics):
    """ adds a document to the whoosh index
    :param writer: whoosh index writer
    :param uri: uri of the document
    :param title : title of the document
    :param topics: list of tuples (label, uuid, score)
    :param words: list of words
    """
    idxtopics = u" / ".join(topics)
    writer.add_document(uri = unicode(uri.decode('utf-8')),
                        title = title,
                        topics = idxtopics,
                        )


def topicssearch(q):
    """ iterator : perform a search on topics field (plain text)
    uses the TopicsFormatter class for returning the indices of the matched topics
    :param q: query performed on topics
    :returns: for each result a tuple with indexed fields of result documents
    """
    ix = open_dir(INDEX_DIR)
    queryparser=QueryParser("topics", ix.schema)
    with ix.searcher() as searcher:
        query = queryparser.parse(q)
        results = searcher.search(query,limit=None)
        for result in results:
            yield (result.get('uri'),
                   result.get('title'),
                   result.get('topics'),
                   )

if __name__ == '__main__':
    usage = "usage: %prog [options] "
    parser = OptionParser(usage)

    parser.add_option("-i", "--index", dest="doindex",
                      action="store_true", default=False,
                      help="Perform topics prediction and indexation")
    parser.add_option("-q", "--query", dest="query",
                      help="Perform query on topics")

    parser.add_option("-d", "--indexdir", dest="indexdir",
                      help="whoosh index directory")

    group = OptionGroup(parser, "Indexing Options",
                        "These options are needed for indexing (-i).")

    group.add_option("-s", "--source", dest="sourcefile",
                      help="Source list of URLs to index")
    group.add_option("-f", "--flush", dest="doflush",
                      action="store_true", default=False,
                      help="Flush index before indexing")
    group.add_option("-K", "--key", dest="apikey",
                      help="XPLR API key")
    group.add_option("-H", "--host", dest="apihost",
                      help="XPLR API host")
    group.add_option("-P", "--port", dest="apiport",
                      help="XPLR API port")
    group.add_option("-S", "--ssl", dest="apissl",
                      action="store_true", default=False,
                      help="use ssl on XPLR calls")
    parser.add_option_group(group)


    (options, args) = parser.parse_args()

    if not(options.doindex or options.query):
        parser.error('index or query option required')

    if options.indexdir:
        INDEX_DIR=options.indexdir

    if options.doindex:
        if not options.sourcefile:
            parser.error('source file required')
        if not options.apikey:
            parser.error('XPLR API key required')
        XPLR_API_KEY=options.apikey
        if not options.apihost:
            parser.error('XPLR host required')
        XPLR_HOST=options.apihost
        XPLR_SSL=options.apissl
        
        if options.apiport:
            XPLR_HOST+=":"+options.apiport
        if options.doflush:
            flush()
        index(options.sourcefile)

    if options.query:
        for res in topicssearch(unicode(options.query)):
            # display results
            print res[1],'(',res[0],')'








