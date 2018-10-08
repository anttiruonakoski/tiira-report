#!/usr/bin/env python3

"""tiirareport.py: Generate template based HTML-document from Bokeh sub-components."""

__author__ = "Antti Ruonakoski"
__copyright__ = "Copyright 2018"
__credits__ = ["Antti Ruonakoski"]
__license__ = "MIT"
__version__ = ""
__maintainer__ = "Antti Ruonakoski"
__email__ = "aruonakoski@gmail.com"
__status__ = "Development"

template_file_name = 'base.html'

from jinja2 import Environment, FileSystemLoader

class Report():

    def __init__(self):          
        pass
        
    def write(self):    
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)  
        template = env.get_template(template_file_name)
        output = template.render()
        return output

if __name__ == "__main__":

    output = Report()
    print (output.write())