# -*- coding: utf-8 -*-
# Python 2.7
#  Pattern based fact extraction library.
#    Copyright (C) 2013 University of Tartu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from corpus import *
import cherrypy
import sys
import shelve
import json

class CorpEdit(object):

    def index(self):
        cherrypy.response.headers['Content-Type']= 'text/html'
        f = open('static/corpedit.html')
        html = f.read()
        f.close()
        return html

    def corpedit_js(self):
        cherrypy.response.headers['Content-Type']= 'text/javascript'
        f = open('static/corpedit.js')
        js = f.read()
        f.close()
        return js

    def ajaxloader_gif(self):
        cherrypy.response.headers['Content-Type']= 'image/gif'
        f = open('static/ajaxloader.gif')
        js = f.read()
        f.close()
        return js

    def style_css(self):
        cherrypy.response.headers['Content-Type']= 'text/css'
        f = open('static/style.css')
        js = f.read()
        f.close()
        return js

    def get_series_names(self):
        cherrypy.response.headers['Content-Type']= 'application/json'
        c = shelve.open(path)
        if len(c) > 0:
            return json.dumps(list(c[c.keys()[0]].columns))
        else:
            return json.dumps([])

    index.exposed             = True
    corpedit_js.exposed       = True
    get_series_names.exposed  = True
    ajaxloader_gif.exposed    = True
    style_css.exposed         = True

def do_main():
    global path

    if len(sys.argv) < 2:
        raise Exception('You must provide the path of the corpus to serve')
    path = sys.argv[1].strip()

    cherrypy.quickstart(CorpEdit())

if __name__ == '__main__':
    do_main()

