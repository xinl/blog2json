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

from django.utils import simplejson
import datetime
#import re
from google.appengine.ext import db
from google.appengine.api import users


class _GAEModelEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        isa=lambda *xs: any(isinstance(obj, x) for x in xs) # shortcut
        
        if isa(datetime.datetime):
            obj = obj.replace(microsecond = 0)
            # No need to expose microsecond to the end user.
            # To decode date in javascript, use:
            # function decodeJsonDate(s){
            #     return new Date(s.slice(0,19).replace('T',' ')+' GMT');
            # }
            return obj.isoformat()
        elif isa(db.Model):
            result = dict((p, getattr(obj, p)) for p in obj.properties())
            """
            if isa(Entry):
                obj.content = re.sub(r'\r\n|\r|\n', '<br />', obj.content)
                # Replace newlines with <br />
            """
            return result
        elif isa(users.User):
            return obj.email()
        else:
            return simplejson.JSONEncoder.default(self, obj)
        
        """ # The original L33T version (http://stackoverflow.com/questions/1531501/json-serialization-of-google-app-engine-models/3063649#3063649):
        return obj.isoformat() if isa(datetime.datetime) else \
        dict((p, getattr(obj, p)) for p in obj.properties()) if isa(db.Model) else \
        obj.email() if isa(users.User) else \
        simplejson.JSONEncoder.default(self, obj)
        """

def encode(obj):
    return simplejson.dumps(obj, cls=_GAEModelEncoder, ensure_ascii=False)

def encodep(obj):
    # May also consider using A versatile static solution to jsonp from http://kawanet.blogspot.com/2008/01/jsonp-se-jsonp-static-emulation.html
    # pre = "(function(d){var l=document.getElementsByTagName('script');var t=l[0].src.match(/[\?\&]callback=([A-Za-z0-9\_\.\[\]]*)/);var f=t?t[1]:'callback';eval(f+'(d)');})("
    pre = "lp_jsonp("
    end = ");"
    return pre + simplejson.dumps(obj, cls=_GAEModelEncoder, ensure_ascii=False, separators=(',',':')) + end
