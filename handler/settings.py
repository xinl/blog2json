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
from google.appengine.ext.webapp import util as gae_util
from google.appengine.ext.webapp import template
from lp.model import Setting
import os

class SettingsHandler(webapp.RequestHandler):
    def get(self):
        
        settings = Setting.get_in_dict()
        
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'settings.html') #two os.path.dirname = "../"
        self.response.out.write(template.render(template_path, settings))
        
        
    def post(self):
        
        keynames = Setting.KEY_LIST.keys()
        settings = []
        
        for keyname in keynames:
            settings.append(Setting(key_name=keyname, value=self.request.get(keyname)))
        
        Setting.save(settings)
        
        self.redirect('../?status=settings_saved')


def main():
    application = webapp.WSGIApplication([('/settings/', SettingsHandler)],
                                         debug=True)
    gae_util.run_wsgi_app(application)


if __name__ == '__main__':
    main()