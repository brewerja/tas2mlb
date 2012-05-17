#!/usr/bin/python

import os
import os.path
import sys
from string import lowercase

from xml.sax import make_parser

from printer import BoxPrinter, PlayByPlayPrinter
from team2 import Game, Inning
from proc2 import parsePlayByPlay

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "USAGE: ", sys.argv[0], " <GAMEFILE>"
        sys.exit(1)

    startPath = os.path.dirname(sys.argv[1])
    htmPath = startPath + '/HTML/'
    if not os.path.exists(htmPath):
        os.mkdir(htmPath)

    xmllist = []
    if os.path.basename(sys.argv[1]) == '*':
        filelist = []
        filenames = os.listdir(startPath)
        for filename in filenames:
            filenamesplit = str(filename).split('.')
            if len(filenamesplit) > 1:
                if filenamesplit[1] == 'xml':
                    xmllist.append(startPath + "/" + filename)
        print xmllist
    else:
        xmllist.append(str(sys.argv[1]))

    for filename in xmllist:

        # Create a parser
        parser = make_parser()

        gameData = Game()

        # Set up content handler
        p = parsePlayByPlay(gameData)
        parser.setContentHandler(p)

        # Announce the file being parsed
        print "Parsing: " + filename

        # Parse the XML
        parser.parse(filename)

        # Save the console address
        consoleOutputAddress = sys.stdout

        # Create listing page
        sys.stdout = open(htmPath + '/listing.htm', 'w')
        print "<h1>Listing</h1>"

        # Return to console
        sys.stdout = consoleOutputAddress

        # Announce where HTML output is headed
        print ('Output to ' + htmPath +
               os.path.basename(filename).split('.')[0].lower() + '.htm')

        # Print HTML box score
        playbyplay = PlayByPlayPrinter()

        # Print the box score!
        playbyplay.printPlayByPlay(gameData, filename)

        # Add to listing Page
        sys.stdout = open(htmPath + '/listing.htm', 'a')
        print ("<a href=\"" + os.path.basename(filename).split('.')[0].lower()
               + ".htm\">" + os.path.basename(filename).split('.')[0].lower() +
               ".htm</a><br/>")
        sys.stdout = consoleOutputAddress
