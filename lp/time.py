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

import datetime

class TZOffset(datetime.tzinfo):
    def __init__(self, offset_string):
        # validity of offset_string is already taken care of by Setting.put() so we just trust it here. 
        self.offset_string = offset_string
        self._h = int(self.offset_string[1:3])
        self._m = int(self.offset_string[3:5])
        if self.offset_string[0] == "-":
            self._h = - self._h
            self._m = - self._m
    
    def utcoffset(self, dt): return datetime.timedelta(hours = self._h, minutes = self._m)
    
    def dst(self, dt): return datetime.timedelta(0)
    
    def tzname(self, dt): return self.offset_string

#UTC = TZOffset("+0000")

def str2datetime(time_str, time_zone="+0000"):
    """ Convert string (format: YYYY-MM-DD HH:MM:SS) into datetime object. """
    # For some unknown reason, datetime.strptime() refuse to work.
    ts = time_str.split(' ')
    ts[0] = ts[0].split('-')
    ts[1] = ts[1].split(':')
    time_object = datetime.datetime(int(ts[0][0]), int(ts[0][1]), int(ts[0][2]), int(ts[1][0]), int(ts[1][1]), int(ts[1][2]), 000000, TZOffset(time_zone))
    
    #time_object = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    #time_object.tzinfo = TZOffset(time_zone)
    return time_object

def datetime2str(time_obj):
    """ Convert datetime object to string (format: YYYY-MM-DD HH:MM:SS). """
    #time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
    time_str = "-".join([str(time_obj.year), str(time_obj.month), str(time_obj.day)]) + " " + ":".join([str(time_obj.hour), str(time_obj.minute), str(time_obj.second)])
    return time_str

def changetz(time_object, timezone_string):
    if time_object.tzinfo == None:
        time_object = time_object.replace(tzinfo=TZOffset("+0000"))
    return time_object.astimezone(TZOffset(timezone_string))
    