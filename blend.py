#!/usr/bin/env python2.7

import atexit
import os
import re
import shutil
import sys
import tempfile

import requests

os.environ['PATH'] = '~ccl/software/external/imagemagick/bin:' + os.environ['PATH']

# Global variables

REVERSE     = False
DELAY       = 20
STEPSIZE    = 5

# Functions

def usage(status=0):
    print '''Usage: {} [ -r -d DELAY -s STEPSIZE ] netid1 netid2 target
    -r          Blend forward and backward
    -d DELAY    GIF delay between frames (default: {})
    -s STEPSIZE Blending percentage increment (default: {})'''.format(
        os.path.basename(sys.argv[0]), DELAY, STEPSIZE
    )
    sys.exit(status)

# Parse command line options

args = sys.argv[1:]

while len(args) and args[0].startswith('-') and len(args[0]) > 1:
  arg = args.pop(0)
  if arg == '-r':
    REVERSE = True
  elif arg == '-d':
    DELAY = int(args.pop(0))
  elif arg == '-s':
    arg = int(args.pop(0))
    if arg > 0 and arg < 100:
      STEPSIZE = arg
  elif arg == '-h':
    usage()

if len(args) != 3:
    usage(1)

netid1 = args[0]
netid2 = args[1]
target = args[2]

# Main execution

# TODO: Create workspace

tempDir = tempfile.mkdtemp()

# TODO: Register cleanup

def rmDir():
  shutil.rmtree(tempDir)

atexit.register(rmDir)

# TODO: Extract portrait URLs

def search_portrait(netid):
  url = 'https://engineering.nd.edu/profiles/' + netid
  getURLS = requests.get(url)
  imgURL = re.findall('https.*@@images.*(?:jpeg|png)', getURLS.text)
  imgURL = imgURL[0]
  if len(imgURL) < 1:
    sys.exit(1)
  return imgURL

imgURL1 = search_portrait(netid1)
imgURL2 = search_portrait(netid2)

# TODO: Download portraits

def download_file(url, path):
  img = requests.get(url)
  with open(path, 'w') as f:
    f.write(img.content)

pic1 = tempDir + "/portrait1.jpg"
pic2 = tempDir + "/portrait2.jpg"

download_file(imgURL1, pic1)
download_file(imgURL2, pic2)


# TODO: Generate blended composite images

def run_command():
  count = 0
  step = STEPSIZE
  command = "convert -loop {0} -delay {1}".format(0, DELAY)
  while count >=0 and count <= 100:
    if count < 10:
      string = "/00" + str(count) + "-" + target
    elif count == 100:
      string = "/" + str(count) + "-" + target
    else:
      string = "/0" + str(count) + "-" + target
    picFinal = tempDir + string
    blend = "composite -blend {0} {1} {2} {3}".format(count, pic1, pic2, picFinal)
    if os.system(blend) != 0:
      sys.exit(2)
    command += " " + tempDir + string
    if count + step > 100 and REVERSE == True:
      step *= -1
    count += step
      
  command += " " + target
  return command

command = run_command()

# TODO: Generate final animation

if os.system(command) != 0:
  sys.exit(3)



