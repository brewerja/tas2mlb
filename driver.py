#!/usr/bin/python

import sys
import os.path
import pickle

from xml.sax import make_parser
from bsddb3 import db

from team import Team, Game
from proc import ParseStats
from printer import BoxPrinter

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "USAGE: ", sys.argv[0], " <GAMEFILE>"
        sys.exit(1)

    startPath = os.path.dirname(sys.argv[1])
    dbPath = startPath + '/BDB/'
    htmPath = startPath + '/HTML/'
    if not os.path.exists(dbPath):
        os.mkdir(dbPath)
    if not os.path.exists(htmPath):
        os.mkdir(htmPath)

    # Filenames for the databases
    BATTERS_DB = 'avgDB'
    PITCHERS_DB = 'eraDB'
    WL_DB = 'winlossDB'
    GAME_DB = 'gameDB'

    # Remove all existing databases to generate new ones
    if (sys.argv[-1] == 'clean'):
        os.remove(dbPath + BATTERS_DB)
        os.remove(dbPath + PITCHERS_DB)
        os.remove(dbPath + GAME_DB)
        os.remove(dbPath + WL_DB)

    xmllist = []
    if os.path.basename(sys.argv[1]) == '*':
        filelist = []
        filenames = os.listdir(startPath)
        for filename in filenames:
            filenamesplit = str(filename).split('.')
            if len(filenamesplit) > 1:
                if filenamesplit[1] == 'xml' or filenamesplit[1] == 'XML':
                    xmllist.append(startPath + "/" + filename)
        print xmllist
    else:
        #xmllist.append(str(sys.argv[1]).split(".")[0])
        xmllist.append(str(sys.argv[1]))

    # Database Stuff
    batterDB = db.DB()
    batterDB.set_flags(db.DB_DUPSORT)
    batterDB.open(dbPath + BATTERS_DB, None, db.DB_BTREE, db.DB_CREATE)

    pitcherDB = db.DB()
    pitcherDB.set_flags(db.DB_DUPSORT)
    pitcherDB.open(dbPath + PITCHERS_DB, None, db.DB_BTREE, db.DB_CREATE)

    gameDB = db.DB()
    gameDB.open(dbPath + GAME_DB, None, db.DB_HASH, db.DB_CREATE)

    winlossDB = db.DB()
    winlossDB.set_flags(db.DB_DUPSORT)
    winlossDB.open(dbPath + WL_DB, None, db.DB_BTREE, db.DB_CREATE)

    databases = [dbPath + BATTERS_DB, dbPath + PITCHERS_DB, dbPath + WL_DB]

    for filename in xmllist:
        try:
            # Create a parser
            parser = make_parser()

            # Set up content handler
            game = Game()
            visitor = Team()
            home = Team()
            p = ParseStats(game, home, visitor)
            parser.setContentHandler(p)

            # Announce the file being parsed
            print "Parsing: " + filename

            # Parse the XML
            parser.parse(filename)

            # Database Stuff
            teams = [visitor, home]
            for team in teams:

                # Add to the batting db all the position players in the game.
                for i in range(1, team.getLineupLength() + 1):
                    for pID in team.getLineupSpot(i):
                        player = team.players[pID]
                        playerPickled = pickle.dumps(player)
                        try:
                            batterDB.put(str(player.name), playerPickled)
                        except db.DBKeyExistError:
                            raise StopIteration()

                # Add to the pitching database all the pitchers in the game.
                for i in range(1, team.getPitchingOrderLength() + 1):
                    for pID in team.getPitchingSpot(i):
                        player = team.players[pID]
                        playerPickled = pickle.dumps(player)
                        try:
                            pitcherDB.put(str(player.name), playerPickled)
                        except db.DBKeyExistError:
                            raise StopIteration()

            if game.duration == 'FORF-H':
                winner = home.id
                loser = visitor.id
            elif game.duration == 'FORF-V':
                winner = visitor.id
                loser = home.id
            elif visitor.runs > home.runs:
                winner = visitor.id
                loser = home.id
            elif home.runs > visitor.runs:
                winner = home.id
                loser = visitor.id

            # Add to the win/loss db the winner and loser of the current game.
            date = game.date.strftime("%Y%m%d" + str(game.dhgame))
            try:
                winlossDB.put(date, pickle.dumps({'winner': winner, \
                                                 'loser': loser}))
            except db.DBKeyExistError:
                raise StopIteration()

            # Add to the games database the team objects and game object
            gamePackage = [game, visitor, home]
            try:
                gameDB.put(filename, pickle.dumps(gamePackage))
            except db.DBKeyExistError:
                pass  # print 'gameDB already exists'

        except StopIteration:
            # Announce the file being skipped
            print "Skipping: " + filename

    batterDB.close()
    pitcherDB.close()
    winlossDB.close()
    gameDB.close()

    # Save the console address
    consoleOutputAddress = sys.stdout

    # Create listing page
    sys.stdout = open(htmPath + '/listing.htm', 'w')
    print "<h1>Listing</h1>"
    print "<table>"

    # Return to console
    sys.stdout = consoleOutputAddress

    for filename in xmllist:

        # Retrieve the game from the database for processing
        gameDB = db.DB()
        gameDB.open(dbPath + GAME_DB, None, db.DB_HASH)
        gamePackagePickled = gameDB.get(filename)
        gamePackage = pickle.loads(gamePackagePickled)
        game = gamePackage[0]
        visitor = gamePackage[1]
        home = gamePackage[2]

        # Announce where HTML output is headed
        print 'Output to ' + htmPath + \
                os.path.basename(filename).split('.')[0].lower() + '.htm'

        # Print HTML box score
        box = BoxPrinter(databases)

        # Print the box score!
        box.printBox(visitor, home, game, filename)

        # Add to listing Page
        sys.stdout = open(htmPath + '/listing.htm', 'a')
        basename = os.path.basename(filename).split('.')[0].lower()
        print "<tr><td>"
        print "<a href=\"" + basename + ".htm\">" + basename + ".htm</a><br/>"
        print "</td><td>"
        print "<a href=\"" + basename + "_pbp.htm\">" + basename + \
                "_pbp.htm</a><br/>"
        print "</td></tr>"
        sys.stdout = consoleOutputAddress

    sys.stdout = open(htmPath + '/listing.htm', 'a')
    print "</table>"
    sys.stdout = consoleOutputAddress
    gameDB.close()
