#!/usr/bin/env python

# Hello World in GIMP Python

from gimpfu import *

def hello_world(initstr, font, size, color) :
    pass

register(
    "python_fu_hello_world",
    "Hello world image",
    "Create a new image with your text string",
    "Akkana Peck",
    "Akkana Peck",
    "2010",
    "Hello world (Py)...",
    "",      # Create a new image, don't work on an existing one
    [],
    [],
    hello_world, menu="<Image>/File/Create")

main()