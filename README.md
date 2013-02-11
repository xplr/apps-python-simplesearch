Simple search
=============

Index and search using XPLR topics API, using the python whoosh index and search engine

Description
-----------

This application permits the following operations :

* Index a set of documents : From an url list, get XPLR prediction on the resources located at these
urls, and indexes the topics returned using the whoosh indexing engine.

* Seerch : Performs full text search on topics on the index, returning the list of urls
that matched the query

Licence
-------

This application is realased under the MIT licence

> 
> Copyright (c) 2012 Xplr Software Inc
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
> 


Prerequisites
-------------

- Get an XPLR API key on www.xplr.com, the key hash is to be passed as an argument to the script


Usage
-----

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



