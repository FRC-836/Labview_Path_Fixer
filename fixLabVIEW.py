#! /usr/bin/python

_description = '''
This script takes in a LabVIEW project file and checks for absolute paths
    to vi files. Any vi files referenced with absolute paths are copied 
    into the local project, and the path is changed to a relative path.
'''

_defaultRun = '''
    python fixLabVIEW.py
        --ignore-prefix=/.*userlib.*/
        --copy-directory=./
        --types=VI
        --infile=project.lvproj
        --outfile=project.lvproj
'''
__author__ = "Dan"
__version__ = "1.0"
__copyright__ = ""

import argparse, re, os, shutil
import xml.etree.ElementTree as ET

def init_args():
    parser = argparse.ArgumentParser(description=_description)

    parser.add_argument('-i','--infile',dest='infilename',required=True,
        help='The .lvproj file that you want to parse from')
    parser.add_argument('-o','--outfile',dest='outfilename',required=False,
        help='The .lvproj file you want to write out to, defaults to infile')
    parser.add_argument('--ignore-prefix','-p',dest='ignore',required=False,
        help='Prefix paths for paths to ignore, comma delimited, regex, already ignores paths containing < or >')
    parser.add_argument('--copy-directory','-c',dest='copyTo',required=False,
        help='Directory to copy files into. Defaults to ./')
    parser.add_argument('--types','-t',dest='types',required=False,
        help='Types of files to copy, comma delimited, defaults to VI')
    parser.add_argument('--move','-m',dest='move',required=False,
        help='Moves instead of copying',action='store_true')

    parser.set_defaults( outfilename='',
                            ignore='',
                            copyTo='./',
                            types='VI',
                            move=False
                        )

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = init_args()

    m_types = args.types.split(",")

    m_ignore = [re.compile(".*&lt;.*"), re.compile(".*&gt;.*"), re.compile(".*[<>].*")]
    for ig in args.ignore.split(","):
        if len(ig) > 0:
            m_ignore.append(re.compile(ig + ".*")) #append a .* so we can use match for prefix


    samefile = (args.outfilename == args.infilename or args.outfilename == '')

    tree = ET.parse(args.infilename)
    root = tree.getroot()

    for item in root.iter("Item"):
        for t in m_types:
            if item.get("Type") == t:
                #matched one of our types
                url = item.get("URL")
                if os.path.isabs(url) or not os.path.commonprefix([os.path.abspath(url),os.path.abspath(args.infilename)]).startswith(os.path.dirname(os.path.abspath(args.infilename))):
                    #not a relative path
                #   print("absolute path: " + url)
                #   print(" commonprefix: " + os.path.commonprefix([os.path.abspath(url),os.path.abspath(args.infilename)]) + " infile path: " + os.path.dirname(os.path.abspath(args.infilename)))
                    ignore = False
                    for ig in m_ignore:
                        #check if this is one of our ignored paths
                        if ig.match(url):
                #           print( "ignore based on " + str(ig))
                            ignore = True
                            break
                    if not ignore:
                        #we found one to move!
                        if os.path.exists(url):
                            if args.move:
                                print("Moving " + item.get("Name") + " from " + os.path.dirname(url) + " to " + args.copyTo)
                                shutil.move(url, args.copyTo)
                            else:
                                print("Copying " + item.get("Name") + " from " + os.path.dirname(url) + " to " + args.copyTo)
                                shutil.copy2(url, args.copyTo)
                            item.set("URL", os.path.join(args.copyTo,os.path.basename(url)))
                        else:
                            print("Path does not exist: " + url)
                #else:
                #   print("relative path: " + url + " abspath: " + os.path.abspath(url) + " infile path: " + os.path.abspath(args.infilename))
    if samefile:
        tree.write(args.infilename)
    else:
        tree.write(args.outfilename)

