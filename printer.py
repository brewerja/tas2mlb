#!/usr/bin/python
""" Prints an HTML box score. """

# Conventions: t = Team object, p = Player object, e = Event object,
# i = integer, pID = player last name, key for a Team object's players dict.

import sys
import os.path
from string import lowercase

from utils import printTeamRecord, printTeamStreak, printAVG, printHittingTotal
from utils import prettyInning, translateNarrative, printErrors
from utils import printERA, printPitcherRecord, printSaves, printPassedBalls

class BoxPrinter:
    
    def __init__(self, databases):
        self.BATTERS_DB = databases[0]
        self.PITCHERS_DB = databases[1]
        self.WL_DB = databases[2]
        
    def printLinescore(self, away, home):
        """ Prints an HTML table linescore given 2 Team objects. """
        print "<table id=\"linescore\">"
        self.printLineHeader(len(away.linescore))
        self.printLine(away)
        self.printLine(home)
        print "</table>"
        
    def printLineHeader(self, num_inn):
        """ Prints an HTML table header for a linescore. """
        print "<tr>",
        sys.stdout.write("<th></th>")
        for i in range(1, num_inn + 1):
            sys.stdout.write("<th>%s</th>" % i)
        print "<th></th><th>R</th><th>H</th><th>E</th>",
        print "</tr>"
        
    def printLine(self, t):
        """ Prints an HTML table row given a Team object """
        print "<tr>",
        sys.stdout.write("<td>" + t.name + "</td>"),
        for x in t.linescore:
            if x != '0' and x != 'X':
                sys.stdout.write("<td class=\"b\">%s</td>" % x)
            else:
                sys.stdout.write("<td>%s</td>" % x)
        print "<td></td><td class=\"score\">%(r)2d</td><td>%(h)2d</td><td>%(e)\
               2d</td>" % {'r': t.runs, 'h': t.hits, 'e': t.errs},
        print "</tr>"
        
    def printBattingTable(self, t, seasonTotals=1):
        """ Prints a box score batting table in HTML, given a Team object. """     
        
        # Opening <table> tag and header row.
        print "<table class=\"batting_table\">"
        print "<tr><th>" + str(t.name) + "</th><th>AB</th><th>R</th><th>H</th>\
        <th>RBI</th><th>BB</th><th>SO</th><th>LOB</th>"
        
        # If season totals are desired, add a column for AVG.
        if seasonTotals:
            sys.stdout.write("<th>AVG</th></tr>")
        else:
            sys.stdout.write("</tr>")
        
        # Iterate through the lineup, populating the various columns.
        for i in range(1, t.getLineupLength() + 1):
            sub = 0
            for pID in t.getLineupSpot(i):
                # Retrieve Player object.
                p = t.players[pID]
                nameprefix = "<td>"
                
                # If player is not a starter, add CSS class for indenting.
                if sub:
                    nameprefix = "<td class=\"sub\">"
                    # Pinch runners get numbered footnotes.
                    if p.poslist[0] == 'pr':
                        for num, e in enumerate(t.pinchrunners):
                            if e.name == p.id:
                                nameprefix += str(num + 1) + "-"
                                break
                    # Pinch hitters get lettered footnotes.
                    if p.poslist[0] == 'ph':
                        alphabet = lowercase
                        for num, e in enumerate(t.pinchhitters):
                            if e.name == p.id:
                                nameprefix += alphabet[num] + "-"
                                break
                            
                # Print out positions played in order (e.g. 1B-3B).
                positions = ""
                if -1 in p.poslist:
                    p.poslist.remove(-1)
                for pos in p.poslist:
                    positions += pos.upper()
                    if pos != p.poslist[-1]:
                        positions += "-"
                tmpname = nameprefix + p.name + ", " + positions
                
                # Turn on sub flag for remaining players within lineup spot.
                sub = 1
                
                dict = {'td_name': tmpname, 'ab': p.hitting.ab, \
                        'r': p.hitting.r, 'h': p.hitting.h, \
                        'rbi': p.hitting.rbi, 'bb': p.hitting.bb, \
                        'so': p.hitting.so, 'lob': p.hitting.lob}
                print "<tr>%(td_name)s</td><td>%(ab)s</td><td>%(r)s</td><td>\
                       %(h)s</td><td>%(rbi)s</td><td>%(bb)s</td><td>%(so)s</td>\
                       <td>%(lob)s</td>" % dict,
                
                # If season totals are desired populate the AVG column.
                if seasonTotals:
                    dict['avg'] = printAVG(self.BATTERS_DB, str(p.name), \
                                        int(p.date))
                    print "<td>%(avg)s</td></tr>\n" % dict,
                else:
                    print "<tr>\n",       
                    
                # Add up individual LOB for print total in final row.         
                t.playerlob += p.hitting.lob
        
        # Print team totals for table's final row and close </table> tag.
        dict = {'ab': t.ab, 'r': t.runs, 'h': t.hits, 'rbi': t.rbi, \
                'bb': t.bb, 'so':t.so, 'lob':t.playerlob}        
        print "<tr class=\"totals\"><td>Totals</td><td>%(ab)s</td><td>%(r)s\
               </td><td>%(h)s</td><td>%(rbi)s</td><td>%(bb)s</td><td>%(so)s\
	       </td><td>%(lob)s</td></tr>" % dict
        print "</table>"
        
    def printPitchingTable(self, t, seasonTotals=1):
        """ Prints a box score pitching table in HTML, given a Team object. """
        
        # Opening <table> tag and header row.
        print "<table class=\"pitching_table\">"
        print "<tr><th>" + str(t.name) + "</th><th>IP</th><th>H</th><th>R</th>\
               <th>ER</th><th>BB</th><th>SO</th><th>HR</th>",
        
        # If season totals are desired, add a column for ERA.
        if seasonTotals:
            print "<th>ERA</th></tr>"
        else:
            print "</tr>"
        
        # Iterate through the pitchers used, populating the various columns.    
        for i in range(1, t.getPitchingOrderLength() + 1):
            for pID in t.getPitchingSpot(i):
                # Retrieve Player object.
                p = t.players[pID]
                
                # If pitcher was tagged with the W, L, or S, append to name.
                if p.pitching.win != 0:
                    if seasonTotals:
                        record = printPitcherRecord(self.PITCHERS_DB, \
                                                    str(p.name), int(p.date))
                        namesuffix = " (W, " + record + ")"
                    else:
                        namesuffix = " (W)"
                elif p.pitching.loss != 0:
                    if seasonTotals:
                        record = printPitcherRecord(self.PITCHERS_DB, \
                                                    str(p.name), int(p.date))
                        namesuffix = " (L, " + record + ")"
                    else:
                        namesuffix = " (L)"
                elif p.pitching.save != 0:
                    if seasonTotals:
                        saves = printSaves(self.PITCHERS_DB, str(p.name), \
                                           int(p.date))
                    namesuffix = " (S, " + saves + ")"
                else:
                    namesuffix = ''
                    
                tmpname = p.name + namesuffix
                dict = {'name': tmpname, 'ip': p.pitching.ip, \
                        'h': p.pitching.h, 'r': p.pitching.r, \
                        'er': p.pitching.er, 'bb': p.pitching.bb, \
                        'so': p.pitching.so, 'hr': p.pitching.hr}
                print "<tr><td>%(name)s</td><td>%(ip)s</td><td>%(h)s</td><td>\
                       %(r)s</td><td>%(er)s</td><td>%(bb)s</td><td>%(so)s</td>\
                       <td>%(hr)s</td>" % dict,
                
                # If season totals are desired, populate the ERA column.
                if seasonTotals:
                    dict['era'] = printERA(self.PITCHERS_DB, str(p.name), \
                                           int(p.date))
                    print "<td>%(era)s</td></tr>\n" % dict,
                else:
                    print "</tr>" 
        
        # No team totals are printed in a pitchers table, close </table> tag.
        print "</table>"
        
    def printPitchingParagraph(self, teams, game):
        """ Prints the paragraph section of the pitching box score. """
        
        # Print pitcher texts (e.g. "Rivera pitched to 2 batters in the 9th.").
        # These notes are generated when a pitcher is relieved before recording
        # any outs in the inning.
        teams_with_pitchertexts = [t for t in teams if t.pitcherTexts != [] ]
        if teams_with_pitchertexts != []:
            print "<p>"
            # Combine both teams' list of texts and sort in game order.
            eventTexts = teams[0].pitcherTexts + teams[1].pitcherTexts
            eventTexts.sort(key = lambda x: x.play)
            for e in eventTexts:
                # Print texts, adjusting for grammar difference.
                if e.battersSincePitchingChange == 1:
                    text = " pitched to 1 batter in the "
                else:
                    text = " pitched to " + \
                    str(e.battersSincePitchingChange) + " batters in the "
                print e.name + text + prettyInning(e.inning) + "."
                print "<br/>"
            print "</p>"
        
        
        # Start a definition list for pitching items.
        print "<dl>"
        
        # Wild pitches.
        teams_with_wp = [t for t in teams if t.wp != 0]
        if teams_with_wp != []:
            print "<dt>WP:&nbsp;</dt>"
            print "<dd>",
            pitchers_with_wp = []
            for t in teams_with_wp:
                for i in range(1, t.getPitchingOrderLength() + 1):
                    for pID in t.getPitchingSpot(i):
                        player = t.players[pID]
                        if player.pitching.wp != 0:
                            pitchers_with_wp.append(player)
            for p in pitchers_with_wp:
                print p.id,
                if p.pitching.wp > 1:
                    print p.pitching.wp,
                if p != pitchers_with_wp[-1] :
                    sys.stdout.write(", ")
                else:
                    sys.stdout.write(".")
            print "</dd>"
            
        # Balks.
        teams_with_balks = [t for t in teams if t.balks != 0]
        if teams_with_balks != []:
            print "<dt>Balk:&nbsp;</dt>"
            print "<dd>",
            pitchers_with_balks = []
            for t in teams_with_balks:
                for i in range(1, t.getPitchingOrderLength() + 1):
                    for pID in t.getPitchingSpot(i):
                        player = t.players[pID]
                        if player.pitching.bk != 0:
                            pitchers_with_balks.append(player)
            for p in pitchers_with_balks:
                print p.id,
                if p.pitching.bk > 1:
                    print p.pitching.bk,
                if p != pitchers_with_balks[-1] :
                    sys.stdout.write(", ")
                else:
                    sys.stdout.write(".")
            print "</dd>"            
            
        # Intentional walks.
        teams_with_ibb = [x for x in teams if x.been_ibb != 0]
        if teams_with_ibb != []:
            print "<dt>IBB:&nbsp;</dt>"
            print "<dd>",
            list_been_ibb = []    
            for team in teams_with_ibb:
                for event in team.events:
                    if event.type == 'ibb':
                        list_been_ibb.append(event)
            for event in list_been_ibb:
                print event.name,
                sys.stdout.write(" (by " + str(event.pitcher) + ")")
                if event != list_been_ibb[-1]:
                    sys.stdout.write(", ")
                else:
                    sys.stdout.write(".")
            print "</dd>"             
            
        # Hit by pitches.
        teams_with_hbp = [x for x in teams if x.been_hbp != 0]
        if teams_with_hbp != []:
            print "<dt>HBP:&nbsp;</dt>"
            print "<dd>",
            list_been_hbp = []    
            for team in teams_with_hbp:
                for event in team.events:
                    if event.type == 'hbp':
                        list_been_hbp.append(event)
            for event in list_been_hbp:
                print event.name,
                sys.stdout.write(" (by " + str(event.pitcher) + ")")
                if event != list_been_hbp[-1]:
                    sys.stdout.write(", ")
                else:
                    sys.stdout.write(".")
            print "</dd>"
            
        # Pitches-strikes.
        firstpitcher = teams[0].getPitchingSpot(1)
        if firstpitcher != []:
            player = teams[0].players[firstpitcher[0]]
            # Check to see if pitches are being tracked in this game.
            if player.pitching.pitches != None: 
                print "<dt>Pitches-strikes:&nbsp;</dt>"
                print "<dd>",
                for t in teams:
                    lenPitchingOrder = t.getPitchingOrderLength()
                    for i in range(1, lenPitchingOrder + 1):
                        for pID in t.getPitchingSpot(i):
                            p = t.players[pID]
                            print p.id
                            sys.stdout.write(str(p.pitching.pitches) + "-" + \
                                             str(p.pitching.strikes))
                        if (i == lenPitchingOrder and t == teams[-1]):
                            print "."
                        else:
                            print ", "
                print "</dd>"
            
            # Groundouts-flyouts.
            print "<dt>Groundouts-flyouts:&nbsp;</dt>"
            print "<dd>",
            for t in teams:
                lenPitchingOrder = t.getPitchingOrderLength()
                for i in range(1, lenPitchingOrder + 1):
                    for pID in t.getPitchingSpot(i):
                        p = t.players[pID]
                        sys.stdout.write(p.id + ' ' + str(p.pitching.ground) +\
                                         "-" + str(p.pitching.fly))
                    if (i == lenPitchingOrder and t == teams[-1]):
                        sys.stdout.write(".")
                    else:
                        sys.stdout.write(", ")
            print "</dd>" 
            
            # Batters faced.
            print "<dt>Batters faced:&nbsp;</dt>"
            print "<dd>",
            for t in teams:
                lenPitchingOrder = t.getPitchingOrderLength()
                for i in range(1, lenPitchingOrder + 1):
                    for pID in t.getPitchingSpot(i):
                        p = t.players[pID]
                        sys.stdout.write(p.id + ' ' + str(p.pitching.bf))
                    if (i == lenPitchingOrder and t == teams[-1]):
                        sys.stdout.write(".")
                    else:
                        sys.stdout.write(", ")
            print "</dd>"

            #Inherited runners-scored.
            pitchers_with_inherited = []
            for t in teams:
                lenPitchingOrder = t.getPitchingOrderLength()
                for i in range(1, lenPitchingOrder + 1):
                    for pID in t.getPitchingSpot(i):
                        p = t.players[pID]
                        if p.pitching.inheritr != 0:
                            pitchers_with_inherited.append(p)
            if pitchers_with_inherited != []:
                print "<dt>Inherited runners-scored:&nbsp;</dt>"
                print "<dd>",
                for p in pitchers_with_inherited:   
                    print p.id
                    sys.stdout.write(str(p.pitching.inheritr) + "-" + \
                                     str(p.pitching.inherits))
                    if p == pitchers_with_inherited[-1]:
                        print "."
                    else:
                        print ", "
                print "</dd>" 
            
        # Umpires.
        umps = game.umpires
        if umps != []:
            print "<dt>Umpires:&nbsp;</dt>"
            print "<dd>",
            for each in umps:
                sys.stdout.write(each[0][0] + ": " + each[1][0])
                if each != umps[-1]:
                    sys.stdout.write(". ")
                else:
                    sys.stdout.write(".")
            print "</dd>" 
        
        # Weather.
        if game.weather != None:
            print "<dt>Weather:&nbsp;</dt>"
            print "<dd>",
            sys.stdout.write(game.weather + ".")                
            print "</dd>" 
        
        # Time (duration).
        if game.duration != None:
            print "<dt>T:&nbsp;</dt>"
            print "<dd>",
            sys.stdout.write(game.duration + ".")                
            print "</dd>"

        # Attendance.
        if int(game.attend) != 0:
            print "<dt>Att:&nbsp;</dt>"
            print "<dd>",
            sys.stdout.write(game.attend + ".")                   
            print "</dd>"
        
        # Date.
        gameday = game.date
        sys.stdout.write("<dt>" + gameday.strftime("%B %e, %Y") + \
                         "&nbsp;</dt>\n<dd>&nbsp;</dd>")
        
        # Close out definition list.
        print
        print "</dl>"
                
    def printBattingParagraph(self, t):
        
        write = sys.stdout.write
        
        # Pinch Runners (1,2,3) and Pinch Hitters (a,b,c)
        if (len(t.pinchrunners) != 0 or len(t.pinchhitters) != 0):
            print "<p>"
            if len(t.pinchhitters) != 0:
                alphabet = lowercase
                for num, e in enumerate(t.pinchhitters):
                    narr = translateNarrative(e.narrative)
                    print alphabet[num] + "-" + narr.capitalize() + " for " + \
                    e.subfor + " in the " + prettyInning(e.inning) + ". "
                        
            if len(t.pinchrunners) != 0:
                if len(t.pinchhitters) != 0:
                    print "<br/>"
                for num, e in enumerate(t.pinchrunners):
                    print str(num + 1) + "-" + "Ran for " + e.subfor + \
                    " in the " + prettyInning(e.inning) + ". "
            print "</p>"
        
        # Note that in a perfect game there will not be a batting section!
        if len(t.doubles) != 0 or len(t.triples) != 0 or len(t.homeruns) != 0 \
        or t.hits != 0 or t.rbi != 0 or len(t.rbi2out) != 0 or len(t.lisp2out)\
        != 0 or len(t.batters_with_sh) != 0 or len(t.batters_with_sf) != 0 or \
        len(t.batters_with_gidp) != 0 or t.wrisp[0] != '0' or t.lob != 0:
            
            print "<h4>Batting</h4>"
            print "<dl>"
    
            # Doubles, listed in game order.
            if len(t.doubles) != 0:        
                print "<dt>2B:&nbsp;</dt>"
                print "<dd>",
                for pID in t.doubles:
                    # Step 1. Insert player's name.
                    write(pID)
                    p = t.players[pID]
                    doubles = [e for e in p.events if e.type == 'double']
                    if len(doubles) != 1:
                        # Step 2. If he has multiples, print the number.
                        print " "+str(len(doubles)),
                        # Step 3. Print the total for the season.
                        write(" (" + printHittingTotal(self.BATTERS_DB, \
                              str(p.name), int(p.date), 'double') + ", ")
                        for e in doubles:
                            # Step 4. List the pitchers who gave up the 2B's.
                            write(e.pitcher)
                            if e != doubles[-1]:
                                write(", ")
                    else:
                        write(" (" + printHittingTotal(self.BATTERS_DB, \
                              str(p.name), int(p.date), 'double') + ", ")
                        write(doubles[0].pitcher)
                    write(")")
                    if pID == t.doubles[-1]:
                        write(".")
                    else:
                        write(", ")
                print "</dd>"
            
            # Triples, listed in game order.
            if len(t.triples) != 0:
                print "<dt>3B:&nbsp;</dt>"
                print "<dd>",
                for pID in t.triples:
                    write(pID)
                    p = t.players[pID]
                    triples = [e for e in p.events if e.type == 'triple']
                    if len(triples) != 1:
                        print " "+str(len(triples)),
                        write(" (" + printHittingTotal(self.BATTERS_DB, \
                              str(p.name), int(p.date), 'triple') + ", ")
                        for e in triples:
                            write(e.pitcher)
                            if e != triples[-1]:
                                write(", ")
                    else:
                        write(" (" + printHittingTotal(self.BATTERS_DB, \
                              str(p.name), int(p.date), 'triple') + ", ")
                        write(triples[0].pitcher)
                    write(")")
                    if pID == t.triples[-1]:
                        write(".")
                    else:
                        write(", ")
                print "</dd>"
            
            # Homeruns, listed in game order.
            if len(t.homeruns) != 0:
                print "<dt>HR:&nbsp;</dt>"
                print "<dd>",
                for pID in t.homeruns:
                    write(pID)
                    p = t.players[pID]
                    homeruns = [e for e in p.events if e.type == 'hr']
                    if len(homeruns) != 1:
                        print " "+str(len(homeruns)),
                        write(" (" + printHittingTotal(self.BATTERS_DB, \
                              str(p.name), int(p.date), 'hr') + ", ")
                        for e in homeruns:
                            write(prettyInning(e.inning) + " inning off " + \
                                  e.pitcher + ", " + str(e.on) + " on, " + \
                                  str(e.outs) + " out")
                            if e != homeruns[-1]:
                                write(", ")
                    else:
                        write(" (" + printHittingTotal(self.BATTERS_DB, \
                              str(p.name), int(p.date), 'hr') + ", ")
                        e = homeruns[0]
                        write(prettyInning(e.inning) + " inning off " + \
                              e.pitcher + ", " + str(e.on) + " on, " + \
                              str(e.outs) + " out")
                    write(")")
                    if pID == t.homeruns[-1]:
                        write(".")
                    else:
                        write(", ")
                print "</dd>"        
    
            # Total bases per player, listed in lineup order.
            if t.hits != 0:
                batters_with_hits = []
                for spot in t.lineup:
                    for pID in spot:
                        if t.players[pID].hitting.h != 0:
                            batters_with_hits.append(t.players[pID])
                            
                print "<dt>TB:&nbsp;</dt>"
                print "<dd>",
                for p in batters_with_hits:
                    h = p.hitting
                    bases = h.h + h.double + 2 * h.triple + 3 * h.hr
                    write(p.id)
                    if bases != 1:
                        write(" " + str(bases))
                    if p != batters_with_hits[-1]:
                        write("; ")
                    else:
                        write(".")
                print "</dd>"
                
            # RBI, listed in game order.
            if t.rbi != 0:                      
                print "<dt>RBI:&nbsp;</dt>"
                print "<dd>",
                for pID in t.batters_with_rbi:
                    rbi = t.players[pID].hitting.rbi
                    if rbi != 1:
                        write(pID + " " + str(rbi))
                    else:
                        write(pID)
                    
                    write(" (" + printHittingTotal(self.BATTERS_DB, \
                          str(t.players[pID].name), int(t.players[pID].date),\
                          'rbi') + ")") 
                    
                    if pID != t.batters_with_rbi[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"             
                
            # 2-out RBI, listed in game order.
            if len(t.rbi2out) != 0:                      
                print "<dt>2-out RBI:&nbsp;</dt>"
                print "<dd>",
                for pID in t.rbi2out:
                    rbi2out = t.players[pID].hitting.rbi2out
                    if rbi2out != 1:
                        write(pID + " " + str(rbi2out))
                    else:
                        write(pID)
                    if pID != t.rbi2out[-1]:
                        write("; ")
                    else:
                        write(".")                    
                print "</dd>"
                
            # Runners left in scoring position, 2 out, listed in game order.
            if len(t.lisp2out) != 0:                      
                print "<dt>Runners left in scoring position, 2 out:&nbsp;</dt>"
                print "<dd>",
                for pID in t.lisp2out:
                    lisp2out = t.players[pID].hitting.lisp2out
                    if lisp2out != 1:
                        write(pID + " " + str(lisp2out))
                    else:
                        write(pID)
                    if pID != t.lisp2out[-1]:
                        write("; ")
                    else:
                        write(".")                    
                print "</dd>"            
                
            # Sacrifice hits (bunts), listed in game order.
            if len(t.batters_with_sh) != 0:                      
                print "<dt>S:&nbsp;</dt>"
                print "<dd>",
                for pID in t.batters_with_sh:
                    sh = t.players[pID].hitting.sh
                    if sh != 1:
                        write(pID + " " + str(sh))
                    else:
                        write(pID)
                    if pID != t.batters_with_sh[-1]:
                        write("; ")
                    else:
                        write(".")
                print "</dd>"
                
            # Sacrifice flies, listed in game order.
            if len(t.batters_with_sf) != 0:                      
                print "<dt>SF:&nbsp;</dt>"
                print "<dd>",
                for pID in t.batters_with_sf:
                    sf = t.players[pID].hitting.sf
                    if sf != 1:
                        write(pID + " " + str(sf))
                    else:
                        write(pID)
                    if pID != t.batters_with_sf[-1]:
                        write("; ")
                    else:
                        write(".")
                print "</dd>"
                
            # Ground into double plays, listed in game order.
            if len(t.batters_with_gidp) != 0:                      
                print "<dt>GIDP:&nbsp;</dt>"
                print "<dd>",
                for pID in t.batters_with_gidp:
                    gdp = t.players[pID].hitting.gdp
                    if gdp != 1:
                        write(pID + " " + str(gdp))
                    else:
                        write(pID)
                    if pID != t.batters_with_gidp[-1]:
                        write("; ")
                    else:
                        write(".")
                print "</dd>"
                
            # Team with runners in scoring position (e.g. 2-for-3).
            if t.wrisp[0] != 'None':                  
                print "<dt>Team RISP:&nbsp;</dt>"
                print "<dd>",
                write(t.wrisp[0] + "-for-" + t.wrisp[1] + ".")
                print "</dd>"
                
            # Team left on base.
            if t.lob != 0:
                print "<dt>Team LOB:&nbsp;</dt>"
                print "<dd>",
                write(str(t.lob) + ".")
                print "</dd>"                          
            
            print "</dl>"
        
        print
        
        # Make sure there are baserunning events to display.
        if t.sb != 0 or t.cs != 0 or t.pickedoff != 0: 
            print "<h4>Baserunning</h4>"
            print "<dl>"
            
            # Stolen bases, listed in game order.
            if t.sb != 0:
                print "<dt>SB:&nbsp;</dt>"
                print "<dd>",
                for pID in t.players_with_sb:
                    p = t.players[pID]
                    stolenbases = [e for e in p.events if e.type == 'sb']
                    sb = t.players[pID].hitting.sb
                    
                    write(pID + " ")
                    
                    if sb != 1:
                        write(str(sb) + " ")
                                    
                    write("(" + printHittingTotal(self.BATTERS_DB, \
                          str(p.name), int(p.date), 'sb') + ", ")
                    
                    for e in stolenbases:
                        try:
                            write(e.base + " off " + e.pitcher + "/" + \
                                  e.catcher)
                        except:#FIXME: for failed pickoff attempts where the catcher is not involved
                            write(e.base + " off " + e.pitcher)
                        if e != stolenbases[-1]:
                            write(", ")
                        else:
                            write(")")
                    
                    if pID != t.players_with_sb[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"
                
            # Caught Stealings, listed in game order.
            if t.cs != 0:
                print "<dt>CS:&nbsp;</dt>"
                print "<dd>",
                for pID in t.players_with_cs:
                    p = t.players[pID]
                    caughtstealings = [e for e in p.events if e.type == 'cs']
                    cs = t.players[pID].hitting.cs
                    
                    write(pID + " ")
                    
                    if cs != 1:
                        write(str(cs) + " ")
                                    
                    write("(" + printHittingTotal(self.BATTERS_DB, \
                          str(p.name), int(p.date), 'cs') + ", ")
                    
                    for e in caughtstealings:
                        if e.catcher != 0:
                            write(e.base + " by " + e.pitcher + "/" + e.catcher)
                        else:
                            write(e.base + " by " + e.pitcher + " POCS")
                        if e != caughtstealings[-1]:
                            write(", ")
                        else:
                            write(")")
                    
                    if pID != t.players_with_cs[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"      
                
            # Picked off's, listed in game order.
            if t.pickedoff != 0:
                print "<dt>PO:&nbsp;</dt>"
                print "<dd>",
                for pID in t.players_pickedoff:
                    p = t.players[pID]
                    pickedoffs = [e for e in p.events if e.type == 'pickedoff']
                    picked = t.players[pID].hitting.picked
                    
                    write(pID + " ")
                    
                    if picked != 1:
                        write(str(picked) + " ")
                                    
                    write("(")
                    
                    for e in pickedoffs:
                        write(e.base + " base by " + e.picker)
                        if e != pickedoffs[-1]:
                            write(", ")
                        else:
                            write(")")
                    
                    if pID != t.players_pickedoff[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"                                       
            
            
            print "</dl>"
                
        print
        
        if t.intp != 0 or t.indp != 0 or t.players_with_pb != [] or \
        t.errs != 0 or t.players_with_pickoffs != []:
            print "<h4>Fielding</h4>"
            print "<dl>"
            
            # Errors, listed in game order.
            if t.errs != 0:
                print "<dt>E:&nbsp;</dt>"
                print "<dd>",
                for pID in t.players_with_errors:
                    error = t.players[pID].fielding.e
                    if error != 1:
                        write(pID + " " + str(error))
                    else:
                        write(pID)
                        
                    write(" (" + printErrors(self.BATTERS_DB, \
                          self.PITCHERS_DB, str(t.players[pID].name), \
                          int(t.players[pID].date)) + ")")
                    
                    # VERY COMPLEX TO DO TYPES and what to do if type is 
                    # unspecified for one of a player's errors and not the 
                    # other?  Looks bad.  
                    #errors = [y for y in t.players[pID].events \ 
                    #          if y.type == 'error']
                    #
                    #textBlocks = []
                    #for e in errors:
                    #    textBlocks.append(parseErrors(e.narrative,e.numErrors))
                    #    if textBlocks != [None]:
                    #        for block in enumerate(textBlocks):
                    #            
                    #        write(" ("+text+")") 
                     
                    if pID != t.players_with_errors[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"
    
            # Passed balls, listed in game order.
            if t.players_with_pb != []:
                print "<dt>PB:&nbsp;</dt>"
                print "<dd>",
                for pID in t.players_with_pb:
                    pb = t.players[pID].fielding.pb
                    if pb != 1:
                        write(pID + " " + str(pb))
                    else:
                        write(pID)
                        
                    write(" (" + printPassedBalls(self.BATTERS_DB, str(t.players[pID].name), int(t.players[pID].date)) + ")")
                        
                    if pID != t.players_with_pb[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"
                
            # Outfield assists, listed in game order.
            if len(t.outfielders_with_assists) != 0:        
                print "<dt>Outfield assists:&nbsp;</dt>"
                print "<dd>",
                for pID in t.outfielders_with_assists:
                    print pID,
                    p = t.players[pID]
                    ofa = [e for e in p.events if e.type == 'ofa']
                    if len(ofa) != 1:
                        print len(ofa),
                    if pID == t.outfielders_with_assists[-1]:
                        write(".")
                    else:
                        write(", ")
                print "</dd>"                
                            
            # Double plays, listed in game order.
            if t.indp != 0:
                print "<dt>DP:&nbsp;</dt>"
                print "<dd>",
                double_plays = [e for e in t.events if e.type == 'dp']
                if len(double_plays) != 1:
                    write(str(len(double_plays)) + " ")
                write('(')
                for e in double_plays:
                    string = e.narrative
                    poslist = []
                    if string.find('unassisted') != -1:
                        for k, v in e.dpdict.iteritems():
                            poslist.append(k)
                    else:            
                        string = string.replace(';', '')
                        string = string.replace(',', '')
                        string = string.replace('.', '')
                        string = string.split()
                        list = []
                        for z, v in enumerate(string):
                            if v == 'to':
                                list.append(z)
                        #FIXME: Use Regular Expressions Here Instead' 
                        popped = 0
                        for z in list:
                            a = string[z - 1 - popped]
                            b = string[z + 1 - popped]
                            if a != 'p' and a != 'c' and a != '1b' and \
                            a != '2b' and a != '3b' and a != 'ss' and \
                            a != 'lf' and a != 'cf' and a != 'rf' and b != 'p'\
                            and b != 'c' and b != '1b' and b != '2b' and \
                            b != '3b' and b != 'ss' and b != 'lf' and \
                            b != 'cf' and b != 'rf':
                                string.pop(z - popped)                            
                                popped += 1
                        list = []
                        for z, v in enumerate(string):
                            if v == 'to':
                                list.append(z)                            
                        for z in list:
                            poslist.append(string[z - 1])
                            if z == list[-1]:
                                poslist.append(string[z + 1])
                    for i in range(0, len(poslist)):
                        write(e.dpdict[poslist[i]])
                        if i != len(poslist) - 1:
                            write('-')
                        else:
                            if e != double_plays[-1]:
                                write(', ')
                            else:
                                write(').')
                print "</dd>"
                
            # Triple Plays, listed in game order.
            if t.intp != 0:
                print "<dt>TP:&nbsp;</dt>"
                print "<dd>",
                triple_plays = [e for e in t.events if e.type == 'tp']
                if len(triple_plays) != 1:
                    write(str(len(triple_plays)) + " ")
                write('(')
                for e in triple_plays:
                    string = e.narrative
                    poslist = []
                    if string.find('unassisted') != -1:
                        for k, v in e.tpdict.iteritems():
                            poslist.append(k)
                    else:              
                        string = string.replace(';', '')
                        string = string.split()
                        list = []
                        for z, v in enumerate(string):
                            if v == 'to':
                                list.append(z)
                        for z in list:
                            poslist.append(string[z - 1])
                            if z == list[-1]:
                                poslist.append(string[z + 1])
                    for pos in poslist:
                        write(e.tpdict[pos])
                        if pos != poslist[-1]:
                            write('-')
                        else:
                            if e != triple_plays[-1]:
                                write(', ')
                            else:
                                write(').')
                print "</dd>" 

            #FIXME: Pickoffs, listed in game order.
            if t.players_with_pickoffs != []:
                print "<dt>Pickoffs:&nbsp;</dt>"
                print "<dd>",
                for pID in t.players_with_pickoffs:
                    p = t.players[pID]
                    pickoffs = [e for e in p.events if e.type == 'pickoff']
                    picks = t.players[pID].fielding.picks
                    
                    write(pID + " ")
                    
                    if picks != 1:
                        write(str(picks) + " ")
                                    
                    write("(")
                    
                    for e in pickoffs:
                        write(e.runner + " at " + e.base + " base")
                        if e != pickoffs[-1]:
                            write(", ")
                        else:
                            write(")")
                    
                    if pID != t.players_with_pickoffs[-1]:
                        write(", ")
                    else:
                        write(".")
                print "</dd>"                                       
            
            
            print "</dl>"                                         

    def printBox(self, away, home, game, filename):
        consoleOutputAddress = sys.stdout
        dirname = os.path.dirname(filename) + '/HTML/'
        sys.stdout = open(dirname + \
                          os.path.basename(filename).split('.')[0].lower() + \
                          '.htm', 'w')
        
        print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\""
        print "\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
        print "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        print
        print "<head>"
        gameday = game.date
        #gameday = date(int(d[2]),int(d[0]),int(d[1]))
        print "<title>Boxscore: " + game.visname + ' vs. ' + game.homename + \
        " - " + gameday.strftime("%B %e, %Y") + "</title>"
        print "<link rel=\"StyleSheet\" href=\"boxstyle.css\" type=\"text/css\
        \" media=\"screen, print\"/>"
        print "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=\
        utf-8\"/>"
        print "</head>"
        print
        print "<body>"  
        print "<div id=\"wrapper\">"
        print
        print "<div id=\"header\">"
        sys.stdout.write("<h1>" + game.visname + " " + str(away.runs) + ", " +\
                         game.homename + " " + str(home.runs) + "</h1>\n")
        sys.stdout.write("<h3>" + game.stadium + ", " + game.location + "<br>\
                         </h3>\n")
        
        date = int(game.date.strftime("%Y%m%d" + str(game.dhgame)))
        awayRecord = printTeamRecord(self.WL_DB, away.id, date)
        homeRecord = printTeamRecord(self.WL_DB, home.id, date)
        awayStreak = printTeamStreak(self.WL_DB, away.id, date)
        homeStreak = printTeamStreak(self.WL_DB, home.id, date)
        
        sys.stdout.write("<p id=\"awayteam\">" + away.name + " (" + awayRecord\
                         + ")<br/>" + awayStreak + "</p>\n")
        sys.stdout.write("<p id=\"hometeam\">" + home.name + " (" + homeRecord\
                         + ")<br/>" + homeStreak + "</p>\n")
        self.printLinescore(away, home)
        print "</div>"
        print
        print "<div id=\"box_score_container\">"
        print
        print "<div id=\"batting_container\">"
        print "<div id=\"batting_left\">"
        self.printBattingTable(away)
        print
        self.printBattingParagraph(away)
        print "</div>"
        print
        print "<div id=\"batting_right\">"
        self.printBattingTable(home)
        print
        self.printBattingParagraph(home)        
        print "</div>"
        print "</div>"
        print
        print "<div id=\"pitching_container\">"
        print "<div id=\"pitching_left\">"
        self.printPitchingTable(away)
        print "</div>"
        print
        print "<div id=\"pitching_right\">"
        self.printPitchingTable(home)
        print "</div>"
        print "</div> <!--PITCHING CONTAINER-->"
        print
        print "<div id=\"pitching_game_container\">"        
        self.printPitchingParagraph([away, home], game)
        print "</div>"
        print
        print "</div> <!--BOX SCORE CONTAINER-->"
        print
        print "<div id=\"footer\">"
        print "<p>Box score statistics approved by Clark C. Griffith \
        Collegiate Baseball League Offical Scorer</p>"
        print "</div>"
        print
        print "</div> <!--WRAPPER-->"
        print "</body>"
        print "</html>"
        sys.stdout = consoleOutputAddress
        
        
class PlayByPlayPrinter:
    
    def printLinescore(self, linescore):
        print "<table id=\"linescore\">"
        self.printLineHeader(len(linescore[0].line))
        self.printLine(linescore[0])
        self.printLine(linescore[1])
        print "</table>"
        
    def printLineHeader(self, num_inn):
        print "<tr>",
        sys.stdout.write("<th></th>")
        for i in range(1, num_inn + 1):
            sys.stdout.write("<th>%s</th>" % i)
        print "<th></th><th>R</th><th>H</th><th>E</th>",
        print "</tr>"
        
    def printLine(self, t):
        print "<tr>",
        sys.stdout.write("<td>" + t.name + "</td>"),
        for x in t.line:
            if x != '0' and x != 'X':
                sys.stdout.write("<td class=\"b\">%s</td>" % x)
            else:
                sys.stdout.write("<td>%s</td>" % x)
        print "<td></td><td class=\"score\">%(r)2d</td><td>%(h)2d</td>\
               <td>%(e)2d</td>" % {'r': t.runs, 'h': t.hits, 'e': t.errs},
        print "</tr>"    
    
    def printPlayByPlay(self, gameData, filename):    
        consoleOutputAddress = sys.stdout
        dirname = os.path.dirname(filename) + '/HTML/'
	basename = os.path.basename(filename).split('.')[0].lower()
        sys.stdout = open(dirname + basename + '_pbp.htm', 'w')
        
        print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\""
        print "\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
        print "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        print
        print "<head>"
        gameday = gameData.date
        #gameday = date(int(d[2]),int(d[0]),int(d[1]))
        print "<title>Play By Play: " + gameData.visitorLongName + ' vs. ' + \
              gameData.homeLongName + " - " + gameday.strftime("%B %e, %Y") + \
              "</title>"
        print "<link rel=\"StyleSheet\" href=\"pbpstyle.css\" \
              type=\"text/css\" media=\"screen, print\" />"
        print "<meta http-equiv=\"Content-Type\" \
              content=\"text/html;charset=utf-8\" />"
        print "</head>"
        print
        print "<body>"  
        print "<div id=\"wrapper\">"
        print
        print "<div id=\"header\">"
        sys.stdout.write("<h1>" + gameData.visitorLongName + " " + \
                         str(gameData.linescore[0].runs) + ", " + \
                         gameData.homeLongName + " " + \
                         str(gameData.linescore[1].runs) + "</h1>\n")
        sys.stdout.write("<h3>" + gameData.stadium + ", " + \
                         gameData.location + "</h3>\n")
        
        gameData.linescore[1].name = gameData.visitorShortName
        gameData.linescore[0].name = gameData.homeShortName
        self.printLinescore(gameData.linescore)
        print "</div>"
        print
        print "<table id=\"playbyplay\">"
        for inningNumber, eachInning in enumerate(gameData.innings):
            for top, eachHalf in enumerate(eachInning.halfs):
                
                if top:
                    print "<tr class=\"visitor\"><td>"
                    print gameData.visitorShortName + ' - Bottom of ' + \
                          prettyInning(inningNumber + 1)
                else:
                    print "<tr class=\"home\"><td>"
                    print gameData.homeShortName + ' - Top of ' + \
                          prettyInning(inningNumber + 1)              
                print "</td><td class=\"score_header\" colspan=2>SCORE</td>\
                       </tr>"
                print "<tr class=\"wrap\"><td>"
                if top:
                    print eachHalf.pitcherStartingInning + ' pitching for ' + \
                          gameData.homeShortName
                else:
                    print eachHalf.pitcherStartingInning + ' pitching for ' + \
                          gameData.visitorShortName                 
                
                print "</td><td class=\"runs\">" + gameData.visid + \
                      "</td><td class=\"runs\">" + gameData.homeid + \
                      "</td></tr>"
                
                correction = 0
                for on, eachEvent in enumerate(eachHalf.events):
                    if eachEvent.text == 'No play.':
                        correction = 1
                    else:
                        if (on + correction) % 2 == 0:
                            print "<tr class=\"on\">"
                        else:
                            print "<tr class=\"off\">"
                        if eachEvent.type == 'SCORING':
                            print "<td class=\"scoring\">"
                        elif eachEvent.type == 'RELIEVER':
                            print "<td class=\"reliever\">"
                        else:
                            print "<td>"
                        edText = eachEvent.text
                        edText = edText.replace('left field', 'left')
                        edText = edText.replace('center field', 'center')
                        edText = edText.replace('right field', 'right')
                        edText = edText.replace('advanced to', 'to')
                        
                        if edText.find('/  for') != -1:
                            edText = 'Designated Hitter Terminated.'
                        
                        try:
                            edText = edText.replace('to p for', 'relieved ' + \
                                     eachEvent.leavingPitcher + '.')
                            edText = edText.split('.')
                            edText = edText[0] + '.'
                        except AttributeError:
                            edText = edText.replace('to p for', 'relieved')
                        try:
                            edText = edText.replace('to p.', 'relieved ' + \
                                     eachEvent.leavingPitcher)
                        except AttributeError:
                            edText = edText.replace('to p.', 'to pitcher.')
                        edText = edText.replace(' p ', ' pitcher ')
                        
                        for eachError in eachEvent.errorFielders:   
                            name = eachEvent.errorFielders[eachError]
                            edText = edText.replace('by p', 'by pitcher ' + \
                                                    name)
                            edText = edText.replace('by 1b', \
                                                    'by first baseman ' + name)
                            edText = edText.replace('by 2b', \
                                                    'by second baseman ' + name)
                            edText = edText.replace('by 3b', \
                                                    'by third baseman ' + name)
                            edText = edText.replace('by ss', \
                                                    'by shortstop ' + name)
                            edText = edText.replace('by lf', \
                                                    'by left fielder ' + name)
                            edText = edText.replace('by cf', \
                                                    'by center fielder ' + name)
                            edText = edText.replace('by rf', \
                                                    'by right fielder ' + name)
                            edText = edText.replace('by c ', \
                                                    'by catcher ' + name)
                            edText = edText.replace('by c.', \
                                                    'by catcher ' + name + '.')
                            edText = edText.replace('by c,', \
                                                    'by catcher ' + name + ',')
                                                
                        edText = edText.replace('to c.', 'to catcher.')
                        edText = edText.replace('to c ', 'to catcher ')
                        edText = edText.replace(' 1b', ' first')
                        edText = edText.replace(' 2b', ' second')
                        edText = edText.replace(' 3b', ' third')
                        edText = edText.replace(' ss', ' shortstop')
                        edText = edText.replace(' lf', ' left')
                        edText = edText.replace(' cf', ' center')
                        edText = edText.replace(' rf', ' right')
                        
                        edText = edText.replace('double play', 'double play,')
                        
                        if eachEvent.type == 'SUB':
                            edText = edText.replace('to first', 'at first')
                            edText = edText.replace('to second', 'at second')
                            edText = edText.replace('to third', 'at third')
                            edText = edText.replace('to shortstop', \
                                                    'at shortstop')
                            edText = edText.replace('to left', 'in left')
                            edText = edText.replace('to center', 'in center')
                            edText = edText.replace('to right', 'in right')
                            
                        print edText
                        print "</td><td class=\"runs\">"
                        print str(eachEvent.scoreVisitor) + \
                              "</td><td class=\"runs\">" + \
                              str(eachEvent.scoreHome)           
                        print "</td></tr>" 
                print "<tr class=\"wrap\"><td colspan=3>"
                if eachHalf.runs == '1':
                    print eachHalf.runs + " Run, "
                else:
                    print eachHalf.runs + " Runs, "
                if eachHalf.hits == '1':
                    print eachHalf.hits + " Hit, "
                else:
                    print eachHalf.hits + " Hits, "
                if eachHalf.errors == '1':
                    print eachHalf.errors + " Error, "
                else:
                    print eachHalf.errors + " Errors, "
                print eachHalf.leftonbase + " LOB"
                print "</td></tr>"                                   
        print "</table>"
        print "</div>"
        print "</body>"
        print "</html>"        
        sys.stdout = consoleOutputAddress
