"""
Copyright (c) 2010, Xin Li.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from lp.model import Setting
from xml.etree import ElementTree as et
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
import lp.json
import urllib
import urllib2
import re
import os
import logging

class DashboardHandler(webapp.RequestHandler):
    def get(self):
        vars = {}
        
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'dashboard.html') #two os.path.dirname = "../"
        self.response.out.write(template.render(template_path, vars))

    def post(self):
        
        if self.request.get('update_latest'):
            action = 'update_latest'
        elif self.request.get('update_collection'):
            action = 'update_collection'
        else:
            self.redirect('/')
            return
        
        settings = Setting.get_in_dict()
        ns = '{http://www.w3.org/2005/Atom}'
        
        def save_to_s3(key, content):
                conn = S3Connection(settings['aws3_access_key'], settings['aws3_secret_key'])
                bucket = conn.get_bucket(settings['aws3_bucket_name'])
                f = S3Key(bucket)
                f.key = key
                f.set_contents_from_string(content, headers = {'Content-Type': 'application/javascript', 'x-amz-storage-class':'REDUCED_REDUNDANCY'}, policy = 'public-read')
        
        if action == 'update_latest':
            url = 'https://www.blogger.com/feeds/' + settings['blogger_id'] + '/posts/default?max-results=' + settings['max_latest_result']
            
            xmlfile = urllib2.urlopen(url)
            entryxml = et.parse(xmlfile).findall(ns+'entry')
            entries = []
            for e in entryxml:
                entries.append({
                                'id': re.sub(r'.*post-', '', e.find(ns+'id').text),
                                'title': e.find(ns+'title').text,
                                'published': e.find(ns+'published').text,
                                'content': re.sub(r'\r\n|\r|\n|<div class="blogger-post-footer">.*</div>', '', e.find(ns+'content').text),
                                'tags': [cat.attrib['term'] for cat in e.findall(ns+'category')]
                                })
            #self.response.out.write(lp.json.encodep(entries).encode('utf-8'))
            
            save_to_s3('latest.json', lp.json.encodep(entries).encode('utf-8'))
            
            self.redirect('/?status=updated_latest')
            
        elif action == 'update_collection':
            if settings['collection_list'].strip() == '':
                self.redirect('/?status=error_collection_empty')
                return
            
            collection_list = [ line.strip().split(' ') for line in settings['collection_list'].strip().split('\n')]
            collection_list = [ {'name':item[0], 'slug': item[1]} for item in collection_list]
            for item in collection_list:
                url = 'https://www.blogger.com/feeds/' + settings['blogger_id'] + '/posts/default/-/' + urllib.quote(item['name'].encode('utf-8')) + '?max-results=' + settings['max_collection_result']
                
                xmlfile = urllib2.urlopen(url)
                entryxml = et.parse(xmlfile).findall(ns+'entry')
                entries = []
                for e in entryxml:
                    entries.append({
                                    'id': re.sub(r'.*post-', '', e.find(ns+'id').text),
                                    'title': e.find(ns+'title').text,
                                    'published': e.find(ns+'published').text,
                                    'content': re.sub(r'\r\n|\r|\n|<div class="blogger-post-footer">.*</div>', '', e.find(ns+'content').text),
                                    'tags': [cat.attrib['term'] for cat in e.findall(ns+'category')]
                                    })
                
                save_to_s3('anthology/' + item['slug'] + '.json', lp.json.encodep(entries).encode('utf-8'))
                
                #logging.info(url)
            #Now update the index file
            save_to_s3('anthology.json', lp.json.encodep(collection_list).encode('utf-8'))
            
            self.redirect('/?status=updated_collection')
        

def main():
    application = webapp.WSGIApplication([('/', DashboardHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
