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
from google.appengine.ext import db
import re

class Setting(db.Model):
    #key_name = "time_offset"
    value = db.StringProperty (required=False, indexed=False, multiline=True)
  
    KEY_LIST = {
        # Allowed keys and their default values.
        # Don't forget to modify Setting.put() if you change this.
        'blogger_id': '', # a 20ish long digit
        'aws3_bucket_name': '',
        'aws3_access_key': '',
        'aws3_secret_key': '',
        'collection_list': '',
        'max_latest_result': '7',
        'max_collection_result': '12'
        }
    
    @classmethod
    def get_by_keynames(cls, keynames = None):
        """ Extended from db.Model.get(). Will create a Setting in its default values if key_name is not found.
    
            Args:
                keyname: a string of a key_name, or list of key_names.
    
            Returns:
                a Setting instance or a list of Setting instances. 
        """
        if keynames == None:
            keynames = cls.KEY_LIST.keys()
            
        result = cls.get_by_key_name(keynames)
    
        try: # if iterable
            if None in result: # skip the loop if all key_name are present
                missing = []
                for (offset, key) in enumerate(keynames): #TODO: Possible optimization by converting to list comprehension?
                    if result[offset] == None:
                        result[offset] = Setting(key_name=key, value=cls.KEY_LIST[key])
                        missing.append(result[offset])
                db.put(missing)
        except TypeError: # if not iterable
            #TODO: is kind of braching is hard to understand. Consider revising using isinstance()?
            if result == None:
                result = Setting(key_name=str(keynames), value=cls.KEY_LIST[str(keynames)])
                db.put(result)
          
        return result
  
    @classmethod
    def get_in_dict(cls, keynames = None):
        """
        Extended from Setting.get_by_keynames(). Returns a Dict of key_name / value pairs."""
        # TODO: memcache
        if keynames == None:
            keynames = cls.KEY_LIST.keys()
        result = cls.get_by_keynames(keynames)
        output = {}
    
        try:
            iter(result)
        except TypeError: # if not iterable
            result = [result,]
      
        for item in result:
            output[item.key().name()] = item.value
    
        return output
    
    @classmethod
    def save(cls, settings):
        """ Update or create Setting entries after validating values.
            Note: We don't choose the db.StringProperty(validator = ***) way because there is no way to set a validator to key_name.
    
            Args:
                settings: a Setting object or a list of Setting objects.
            
            Returns:
                a Key object or a List of Key objects of the updated or created entries.
      
            Raise:
                ValidationError: if the provided Setting.value fails to conform the formating rules.
        """
        if not isinstance(settings, (list, tuple)):
            settings = [settings,]
      
        for setting in settings:
      
            keyname = setting.key().name()
      
            if not keyname in cls.KEY_LIST:
                # Drop keynames that are not in KEY_LIST
                settings.remove(setting)
        
        db.put(settings)