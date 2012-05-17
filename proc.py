#!/usr/bin/python

# This defines the ParseStats class for parsing XML game files.
# This class inherits from saxutils.handler.ContentHandler.
# Inputs for constructor: Game object 'game', 'home' and 'away' Team objects.

import copy
import datetime

from xml.sax import saxutils

from team import Player, Event
from utils import getShortName


class ParseStats(saxutils.handler.ContentHandler):

    def __init__(self, game, home, away):
        # The Game and Team objects for populating.
        self.game, self.home, self.away = game, home, away
        # Flags and temporary variables used for processing.
        self.playerID = -1
        self.activePickedoff = 0
        self.isPinchHitter = 0
        self.wasBatterAction = 0
        self.activeError = 0
        self.activeErringFielders = []

    def startElement(self, name, attrs):
        # Game Stats
        if (name == 'venue'):
            self.game.gameid = attrs.get('gameid')
            self.away.id = attrs.get('visid')
            self.home.id = attrs.get('homeid')
            self.game.visname = attrs.get('visname')
            self.game.homename = attrs.get('homename')
            self.away.name = getShortName(self.game.visname)
            self.home.name = getShortName(self.game.homename)
            date = attrs.get('date').split('/')
            self.game.date = datetime.date(int(date[2]),int(date[0]),\
                                           int(date[1]))
            self.game.location = attrs.get('location')
            self.game.stadium = attrs.get('stadium')
            self.game.duration = attrs.get('duration')
            self.game.attend = attrs.get('attend')
            self.game.nitegame = attrs.get('nitegame')
            self.game.start = attrs.get('start')
            self.game.schedinn = attrs.get('schedinn')
            self.game.weather = attrs.get('weather') 
            self.game.dhgame = int(attrs.get('dhgame',0))
        elif (name == 'umpires'):
            self.game.umpires = []
            hp = attrs.get('hp')
            first = attrs.get('first')
            second = attrs.get('second')
            third = attrs.get('third')
            if hp != None:
                self.game.umpires.append([['HP'],[hp]])
            if first != None:
                self.game.umpires.append([['1B'],[first]])
            if second != None:
                self.game.umpires.append([['2B'],[second]])
            if third != None:
                self.game.umpires.append([['3B'],[third]])      
        
        # Team Stats        
        elif (name == 'team'):
            if (attrs.get('vh') == 'V'):
                self.curTeam = self.away
            else:
                self.curTeam = self.home
            self.curTeam.treatas = attrs.get('treatas')
            self.curTeam.record = attrs.get('record','0-0')
        elif (name == 'linescore'):
            self.curTeam.linescore = attrs.get('line').split(",")
            self.curTeam.runs = int(attrs.get('runs'))
            self.curTeam.hits = int(attrs.get('hits'))
            self.curTeam.errs = int(attrs.get('errs'))
            self.curTeam.lob = int(attrs.get('lob'))          
        elif (name == 'starter'):
            # Get starting pitcher, others will show up in batting lineup.
            if attrs.get('pos') == 'p':
                self.curTeam.pitcher = attrs.get('name')
        # Team hitting stats.
        elif (name == 'hitting' and self.playerID == -1):
            self.curTeam.ab = int(attrs.get('ab', 0))
            self.curTeam.rbi = int(attrs.get('rbi', 0))
            self.curTeam.bb = int(attrs.get('bb', 0))
            self.curTeam.so = int(attrs.get('so', 0)) 
            self.curTeam.sb = int(attrs.get('sb', 0))           
            self.curTeam.cs = int(attrs.get('cs', 0))
            self.curTeam.pickedoff = int(attrs.get('picked', 0))        
        # Team fielding stats.
        elif (name == 'fielding' and self.playerID == -1):
            self.curTeam.indp = int(attrs.get('indp', 0))
            self.curTeam.intp = int(attrs.get('intp', 0))        
        # Team situational hitting stats.
        elif (name == 'hsitsummary' and self.playerID == -1):
            self.curTeam.wrisp = attrs.get('wrbiops', 'None').split(",")
        # Team pitching stats.
        elif (name == 'pitching' and self.playerID == -1):
            self.curTeam.wp = int(attrs.get('wp', 0))
            self.curTeam.balks = int(attrs.get('bk', 0))        
        # Team situational pitching stats (psitsummary, not used)
        
        # Player Table Stats
        elif (name == 'player'):
            # Ensure that this is not a duplicate entry for the same player
            if not self.curTeam.players.has_key(attrs.get('shortname')):
                #FIXME: shouldn't we use full name as the id?
                # do we need pos in the constructor?
                # Instantiate the new Player object.
                p = Player(attrs.get('shortname'), attrs.get('name'), \
                           attrs.get('pos'))
                # Set operating playerID.
                self.playerID = p.id
                # Set player's spot in the lineup.
                self.curTeam.setLineupSpot(int(attrs.get('spot')), p.id)
                # Create first entry in the ordered list of the player's
                # positions in the game.
                p.poslist.append(attrs.get('pos'))
                # This is appended because we intend to overwrite the poslist
                # if an fsituation tag is available for the player. So far,
                # only one time have I found a case where an fsituation tag was
                # not available.
                p.poslist.append(-1)               
                # Insert the new Player object into the players dictionary.
                self.curTeam.players[p.id] = p
        elif (name == 'hitting' and self.playerID != -1):
            # Access the current Player object from the players dictionary.
            p = self.curTeam.players[self.playerID]
            # Tag this Player object with a a YYYYMMDDA date 
            # for access in the database.
            p.date = self.game.date.strftime("%Y%m%d"+str(self.game.dhgame))
            # Record all of the player's hitting stats for the game.
            p.hitting.ab = int(attrs.get('ab', 0))
            p.hitting.r = int(attrs.get('r', 0))
            p.hitting.h = int(attrs.get('h', 0))
            p.hitting.double = int(attrs.get('double', 0))
            p.hitting.triple = int(attrs.get('triple', 0))
            p.hitting.hr = int(attrs.get('hr', 0))
            p.hitting.rbi = int(attrs.get('rbi', 0))            
            p.hitting.bb = int(attrs.get('bb', 0))
            p.hitting.hbp = int(attrs.get('hbp', 0))            
            p.hitting.so = int(attrs.get('so', 0))
            p.hitting.kl = int(attrs.get('kl', 0))
            p.hitting.hitdp = int(attrs.get('hitdp', 0))
            p.hitting.gdp = int(attrs.get('gdp', 0))
            p.hitting.sf = int(attrs.get('sf', 0))
            p.hitting.sh = int(attrs.get('sh', 0))            
            p.hitting.sb = int(attrs.get('sb', 0))
            p.hitting.cs = int(attrs.get('cs', 0))
            p.hitting.ground = int(attrs.get('ground', 0))
            p.hitting.fly = int(attrs.get('fly', 0))
            p.hitting.picked = int(attrs.get('picked', 0))  
        elif (name == 'fielding' and self.playerID != -1):
            p = self.curTeam.players[self.playerID]
            p.fielding.po = int(attrs.get('po', 0))
            p.fielding.a = int(attrs.get('a', 0))
            p.fielding.e = int(attrs.get('e', 0))
            p.fielding.pb = int(attrs.get('pb', 0))            
        elif (name == 'hsitsummary' and self.playerID != -1):
            p = self.curTeam.players[self.playerID]
            p.hitting.rbi2out = int(attrs.get('rbi-2out', 0))
        elif (name == 'fsituation' and self.playerID != -1):
            # Access current player's ordered list of positions
            poslist = self.curTeam.players[self.playerID].poslist
            # FIXME: Does this need to be done this way?
            # Or can we just always do this and overwrite?
            if poslist[-1] == -1:
                poslist = []
            # Each fsituation tag should have a new position,
            # append them to the list.
            poslist.append(attrs.get('pos'))
            # Return the edited list to the dictionary of Player objects.
            self.curTeam.players[self.playerID].poslist  = poslist
        #elif (name == 'hsituation' and self.playerID != -1):
        elif (name == 'pitching' and self.playerID != -1):
            p = self.curTeam.players[self.playerID]
            # Set appearance order of each pitcher.
            self.curTeam.setPitchingSpot(int(attrs.get('appear')), p.id)
            # Tag this Player object with a date for access in the database.            
            p.date = self.game.date.strftime("%Y%m%d"+str(self.game.dhgame))
            # Record all of the player's hitting stats for the game.
            p.pitching.appear = int(attrs.get('appear', 0))
            p.pitching.win = attrs.get('win', 0)
            p.pitching.loss = attrs.get('loss', 0)
            p.pitching.save = attrs.get('save', 0)
            p.pitching.gs = int(attrs.get('h', 0))
            # Record as a string due to inning thirds.
            p.pitching.ip = attrs.get('ip')
            p.pitching.h = int(attrs.get('h', 0))
            p.pitching.r = int(attrs.get('r', 0))
            p.pitching.er = int(attrs.get('er', 0))
            p.pitching.bb = int(attrs.get('bb', 0))
            p.pitching.so = int(attrs.get('so', 0))
            p.pitching.sha = int(attrs.get('sha', 0))
            p.pitching.bf = int(attrs.get('bf', 0))
            p.pitching.ab = int(attrs.get('ab', 0))
            p.pitching.double = int(attrs.get('double', 0))
            p.pitching.triple = int(attrs.get('triple', 0))
            p.pitching.hr = int(attrs.get('hr', 0))
            p.pitching.wp = int(attrs.get('wp', 0))
            p.pitching.bk = int(attrs.get('bk', 0))
            p.pitching.kl = int(attrs.get('kl', 0))
            p.pitching.fly = int(attrs.get('fly', 0))
            p.pitching.ground = int(attrs.get('ground', 0))
            p.pitching.inherits = int(attrs.get('inherits', 0))
            p.pitching.inheritr = int(attrs.get('inheritr', 0))
            # Not all games will have pitches recorded, but store if available.
            p.pitching.pitches = attrs.get('pitches')
            if p.pitching.pitches != None:
                p.pitching.pitches = int(p.pitching.pitches)
            p.pitching.strikes = attrs.get('strikes')
            if p.pitching.strikes != None:
                p.pitching.strikes = int(p.pitching.strikes)
                
        #-----------START OF PLAY BY PLAY XML----------------------
        elif (name == 'inning'):
            self.curInning = int(attrs.get('number'))
        elif (name == 'batting'):
            self.outsSincePitchingChange = 0
            self.battersSincePitchingChange = 0
            if (attrs.get('vh') == "V"):
                self.curTeam = self.away
            else:
                self.curTeam = self.home
        elif (name == 'play'):
            self.seq = int(attrs.get('seq'))
            # Number of outs at the start of the play.
            self.outs = int(attrs.get('outs'))
            self.batter = attrs.get('batter')
            self.batprof = attrs.get('batprof')
            self.pitcher = attrs.get('pitcher')
            self.pchprof = attrs.get('pchprof')
            self.onFirst = attrs.get('first', 0)
            self.onSecond = attrs.get('second', 0)
            self.onThird = attrs.get('third', 0)
            # Batter LOB Stuff
            self.rawlob = 0
            self.rawlisp2out = 0
            self.fielderschoice = 0
            self.fcout = 0
            if self.onFirst !=0:
                self.rawlob += 1
            if self.onSecond !=0: 
                self.rawlob += 1
                if self.outs == 2:
                    self.rawlisp2out += 1
            if self.onThird !=0:
                self.rawlob += 1
                if self.outs == 2:
                    self.rawlisp2out += 1
        elif (name == 'batter'):
            self.wasBatterAction = 1
            self.battersSincePitchingChange += 1
            # If any number of outs are recorded on the play, this is 1.
            if (attrs.get('out') == '1'):  
                self.outsSincePitchingChange += 1
            # Batter LOB Stuff
            if self.rawlob:
                if (attrs.get('ab') != '1'):
                    self.rawlob = 0
                else:
                    if attrs.get('out') != '1' and attrs.get('rchfc') != '1':
                        self.rawlob = 0
                    else:
                        if self.rawlisp2out:
                            batter = self.curTeam.players[self.batter].hitting
                            batter.lisp2out += self.rawlisp2out
                            if self.batter not in self.curTeam.lisp2out:
                                self.curTeam.lisp2out.append(self.batter)                        
                        if attrs.get('rchfc')=='1':
                            self.fielderschoice = 1
            # Hit by pitch.
            # Create an Event, add it to the team's list of events.
            if (attrs.get('hbp') == '1'):
                e = Event('hbp', attrs.get('name'),self.seq)
                # Record the pitcher who hit the batter.
                e.pitcher = self.pitcher
                self.curTeam.events.append(e)
                self.curTeam.been_hbp += 1
            # Intentional walk.
            # Create an Event, add it to the team's list of events.
            if (attrs.get('ibb') == '1'):
                e = Event('ibb', attrs.get('name'),self.seq)
                # Record the pitcher who intentionally walked the batter.
                e.pitcher = self.pitcher
                self.curTeam.events.append(e)
                self.curTeam.been_ibb += 1
            # Doubles.
            # Create an Event, add it to the player's list of events.       
            if (attrs.get('double') == '1'):
                e = Event('double',attrs.get('name'),self.seq)
                # Record the pitcher who gave up the double.
                e.pitcher = self.pitcher
                self.curTeam.players[self.batter].events.append(e)
                # Also, add the player to the team's ordered, 
                # no-duplicates list of doubles.
                if self.batter not in self.curTeam.doubles:               
                    self.curTeam.doubles.append(self.batter)
            # Triples.
            # Create an Event, add it to the player's list of events.
            elif (attrs.get('triple') == '1'):
                e = Event('triple',attrs.get('name'),self.seq)
                # Record the pitcher who gave up the triple.
                e.pitcher = self.pitcher
                self.curTeam.players[self.batter].events.append(e)
                # Also, add the player to the team's ordered, 
                # no-duplicates list of triples.                
                if self.batter not in self.curTeam.triples: 
                    self.curTeam.triples.append(self.batter)
            # Homeruns.
            # Create and Event, add it to the player's list of events.
            elif (attrs.get('hr') == '1'):
                e = Event('hr',attrs.get('name'),self.seq)
                # Record the pitcher who gave up the homer and on/out/inning.
                e.pitcher = self.pitcher
                e.on = 0
                if self.onFirst !=0: e.on += 1
                if self.onSecond !=0: e.on += 1
                if self.onThird != 0: e.on += 1
                e.outs = self.outs
                e.inning = self.curInning
                self.curTeam.players[self.batter].events.append(e)  
                # Also, add the player to the team's ordered, 
                # no-duplicates list of homeruns.                                  
                if self.batter not in self.curTeam.homeruns: 
                    self.curTeam.homeruns.append(self.batter)
            # RBI, add the player to the team's ordered, 
            # no-duplicates list of RBI.
            if (attrs.get('rbi', 0) != 0):
                if self.batter not in self.curTeam.batters_with_rbi:
                    self.curTeam.batters_with_rbi.append(self.batter)                     
            # 2-out RBI, add the player to the team's ordered, 
            # no-duplicates list of 2-out RBI.
            if (attrs.get('rbi', 0) != 0 and self.outs == 2):
                if self.batter not in self.curTeam.rbi2out:
                    self.curTeam.rbi2out.append(self.batter)
            # Ground into double plays, add the player to the team's ordered, 
            # no-duplicates list of G(I)DP.
            if (attrs.get('gdp', 0) !=0):
                if self.batter not in self.curTeam.batters_with_gidp:
                    self.curTeam.batters_with_gidp.append(self.batter)
            # Sacrifice hits (bunts), add the player to the team's ordered, 
            # no-duplicates list of SAC bunts.
            if (attrs.get('sh', 0) !=0):
                if self.batter not in self.curTeam.batters_with_sh:
                    self.curTeam.batters_with_sh.append(self.batter)
            # Sacrifice flies, add the player to the team's ordered, 
            # no-duplicates list of SAC flies.
            if (attrs.get('sf', 0) !=0):
                if self.batter not in self.curTeam.batters_with_sf:
                    self.curTeam.batters_with_sf.append(self.batter)
        elif (name == 'runner'):
            if (attrs.get('out') == '1'):
                self.outsSincePitchingChange += 1
            # Batter LOB Stuff
            if self.rawlob:
                if self.fielderschoice: # FIELDER'S CHOICE EXCEPTIONS
                    if attrs.get('out') == '1':
                        self.fcout = 1
                if (attrs.get('scored') == '1'):
                    self.rawlob -= 1
            # Stolen bases.
            # Create an Event, add it to the player's list of events.
            if (attrs.get('sb', 0) != 0):
                # Record base stolen and pitcher off whom the base was stolen.
                sb = int(attrs.get('sb', 0))
                base = int(attrs.get('base', 0)) + sb
                if (sb == 1):
                    e = Event('sb', attrs.get('name'), self.seq)
                    e.pitcher = self.pitcher
                    if base == 2: e.base = '2nd'
                    elif base == 3: e.base = '3rd'
                    elif base == 4: e.base = 'home'
                self.curTeam.players[e.name].events.append(e)
                #FIXME: Explain curStealers purpose
                self.curTeam.curStealers.append(e.name)
                # Add the player to the team's ordered, 
                # no-duplicates list of stolen bases.
                if e.name not in self.curTeam.players_with_sb:
                    self.curTeam.players_with_sb.append(e.name)
            # Pickoffs. Create an Event, add it to the player's list of events.
            if (attrs.get('pickoff', 0) != 0):
                e = Event('pickedoff', attrs.get('name'), self.seq)
                e.runner = e.name
                # Record the base where the pickoff occurred.
                base = int(attrs.get('base'), 0)
                if base == 1: e.base = '1st'
                elif base == 2: e.base = '2nd'
                elif base == 3: e.base = '3rd'
                self.curTeam.players[e.name].events.append(e)
                # Add the player to the team's ordered, 
                # no-duplicates list of players picked off.
                if e.name not in self.curTeam.players_pickedoff:
                    self.curTeam.players_pickedoff.append(e.name)
                # Set flag and save event for further processing.
                self.activePickedoff = 1
                self.activeEvent = e
            # Caught Stealings.
            # Create an Event, add it to the player's list of events.
            if (attrs.get('cs', 0) != 0):
                cs = int(attrs.get('cs', 0))
                base = 1 + int(attrs.get('base', 0))
                # Record the base the runner was trying to steal.
                if (cs == 1):
                    e = Event('cs', attrs.get('name'), self.seq)
                    e.pitcher = self.pitcher
                    if base == 2: e.base = '2nd'
                    elif base == 3: e.base = '3rd'
                    elif base == 4: e.base = 'home'
                    # to be changed later, if the catcher is involved
                    e.catcher = 0 
                self.curTeam.players[e.name].events.append(e)
                # FIXME: explain curCaughtStealers purpose
                self.curTeam.curCaughtStealers.append(e.name)
                # Add the player to the team's ordered, 
                # no-duplicates list of players caught stealing.
                if e.name not in self.curTeam.players_with_cs:
                    self.curTeam.players_with_cs.append(e.name) 
        # Substitutions 
        elif (name == 'sub'):
            pos = attrs.get('pos')
            # Pinch Runners
            if pos == 'pr':
                e = Event('pr',attrs.get('who'),attrs.get('seq'))
                e.subfor = attrs.get('for')
                e.inning = self.curInning
                self.curTeam.pinchrunners.append(e)
            # Pinch Hitters
            elif pos == 'ph':
                e = Event('ph',attrs.get('who'),attrs.get('seq'))
                e.subfor = attrs.get('for')
                e.inning = self.curInning
                self.curTeam.pinchhitters.append(e)
                self.isPinchHitter = 1
            # Pitching Change
            elif pos == 'p':
                # Switch Team objects, temporarily.
                if self.curTeam == self.away: self.curTeam = self.home
                elif self.curTeam == self.home: self.curTeam = self.away
                # If the pitching change occurs before the pitcher being 
                # relieved has recorded an out, store a note saying how many 
                # batters he faced and the inning.                 
                if self.outsSincePitchingChange == 0 and \
                self.battersSincePitchingChange > 0:
                    # Create an Event, add it to the team's list of pitcher
                    # notes.
                    e = Event('pitcherText',self.curTeam.pitcher,self.seq)
                    e.inning = self.curInning
                    e.battersSincePitchingChange = \
                    self.battersSincePitchingChange
                    self.curTeam.pitcherTexts.append(e)
                # Set the reliever as the active pitcher.
                self.curTeam.pitcher = attrs.get('who')
                # Reset counters.
                self.outsSincePitchingChange = 0
                self.battersSincePitchingChange = 0
                # Switch back the Team objects.
                if self.curTeam == self.away: self.curTeam = self.home
                elif self.curTeam == self.home: self.curTeam = self.away                 
        elif (name == 'fielder'):
            pos = attrs.get('pos')
            fielder = attrs.get('name')
                        
            # Get the catcher involved in the stolen base to complete the
            # battery.                                   
            if (pos == 'c' and int(attrs.get('sba',0)) != 0):
                for x in self.curTeam.curStealers:
                    self.curTeam.players[x].events[-1].catcher = fielder
                self.curTeam.curStealers = []
                
            # Get the catcher involved in the caught stealing to complete the 
            # battery.
            if (pos == 'c' and self.curTeam.curCaughtStealers != []):
                for x in self.curTeam.curCaughtStealers:
                    self.curTeam.players[x].events[-1].catcher = fielder                
                
            # Switch Team objects, temporarily.
            if self.curTeam == self.away: self.curTeam = self.home
            elif self.curTeam == self.home: self.curTeam = self.away    

            # Outfield Assists.
            # Create an Event and add it to player's list of events.
            if ((pos=='lf' or pos=='cf' or pos=='rf') and \
                int(attrs.get('a',0))==1):
                self.curTeam.players[fielder].fielding.ofa += 1
                e = Event('ofa', fielder, self.seq)
                self.curTeam.players[fielder].events.append(e)
                # Add the player to the team's ordered, no-duplicates list of
                # outfielders with assists.
                if fielder not in self.curTeam.outfielders_with_assists:
                    self.curTeam.outfielders_with_assists.append(fielder)
                    
            # Pickoffs.
            # Create a dictionary of the fielders involved in the pickoff.
            if (self.activePickedoff == 1):
                self.curTeam.podict[pos] = fielder
            # Double plays.
            # Create a dictionary of the fielders invovled in the DP.
            if (int(attrs.get('indp',0)) != 0):
                self.curTeam.dpdict[pos] = fielder
            # Triple plays.
            # Create a dictionary of the fielders invovled in the TP.
            if (int(attrs.get('intp',0)) != 0):
                self.curTeam.tpdict[pos] = fielder
                
            # Errors.
            # Create an Event and add it to the player's list of events.
            if (int(attrs.get('e', 0)) != 0):
                err = int(attrs.get('e',0))
                # This 'if' statement is in case the error is incorrectly 
                # assigned. This has only occurred once--not sure of the cause.
                if fielder != '/':                        
                    #FIXME: Much of the error code is not used, namely the Event objects
                    self.activeError = 1
                    self.activeErringFielders.append(fielder)                    
                    e = Event('error',fielder,self.seq)
                    e.numErrors = err
                    e.pos = pos
                    self.curTeam.players[fielder].events.append(e)
                    # Add the player to the team's ordered, 
                    # no-duplicates list of fielders with errors.
                    if fielder not in self.curTeam.players_with_errors:
                        self.curTeam.players_with_errors.append(fielder)

            # Passed Balls. Add the player to the team's ordered, 
            # no-duplicates list of catchers with passed balls.
            if (int(attrs.get('pb', 0)) != 0):
                if fielder not in self.curTeam.players_with_pb:
                    self.curTeam.players_with_pb.append(fielder)

            # Switch back the Team objects.
            if self.curTeam == self.away: self.curTeam = self.home
            elif self.curTeam == self.home: self.curTeam = self.away

        elif (name == 'narrative'):
            text = attrs.get('text')
            self.curTeam.curCaughtStealers = []
            
            # Get text of the pinch hitter's actions for footnote in box score.
            if self.wasBatterAction and self.isPinchHitter:
                self.isPinchHitter = 0
                self.curTeam.pinchhitters[-1].narrative = text
                
            # Batter LOB Stuff
            if self.rawlob and self.wasBatterAction:
                if not (self.fielderschoice and self.fcout==0):
                    self.curTeam.players[self.batter].hitting.lob += \
                    self.rawlob
            self.wasBatterAction = 0
            
            # Switch Team objects, temporarily.
            if self.curTeam == self.away: self.curTeam = self.home
            elif self.curTeam == self.home: self.curTeam = self.away
            
            # Get text of the play and attach it to the error Event.
            if self.activeError:
                for fielder in self.activeErringFielders:
                    self.curTeam.players[fielder].events[-1].narrative = text
                self.activeError = 0
                self.activeErringFielders = []            
           
            # Double plays.
            # Create an Event and add it to the team's list of dp's turned.
            if ((self.home.dpdict != {} or self.away.dpdict != {})):                    
                e = Event('dp', self.batter, self.seq)
                # Access the DP dictionary created earlier to associate it 
                # with the Event object.
                e.dpdict = self.curTeam.dpdict
                e.narrative = text
                self.curTeam.events.append(e)
                self.curTeam.dpdict = {}

            # Double plays.
            # Create an Event and add it to the team's list of tp's turned.
            if ((self.home.tpdict != {} or self.away.tpdict != {})):
                e = Event('tp', self.batter, self.seq)
                # Access the TP dictionary created earlier to associate it 
                # with the Event object.
                e.tpdict = self.curTeam.tpdict
                e.narrative = text
                self.curTeam.events.append(e)
                self.curTeam.tpdict = {}
            
            # Parsing narratives for the order of the pickoff.
            if (self.curTeam.podict != {}):
                
                # Text processing to allow for extracting of players from the 
                # narrative.
                text = text.replace(',','')
                text = text.replace(';','')
                text = text.replace('.','')
                text = text.split()
                tolist = []
                for wordLocation, word in enumerate(text):
                    if word == 'to':
                        tolist.append(wordLocation)
                for eachTo in tolist:
                    a = text[eachTo-1]
                    b = text[eachTo+1]                        
                    if (a == 'p' or a == 'c') and \
                    (b == 'p' or b == 'c' or b == '1b' or b == '2b' or \
                     b == '3b' or b == 'ss' or b == 'lf' or b == 'cf' or \
                     b == 'rf'):
                        starter_of_pickoff_pos = text[eachTo-1]
                        break
                
                # Copy the active Event object for editing.
                f = copy.copy(self.activeEvent)
                f.name = self.curTeam.podict[starter_of_pickoff_pos]
                self.activeEvent.picker = f.name
                f.type = 'pickoff'     

                # Add either the pitcher or the catcher's name to the team's
                # ordered, no-duplicates list of players with pickoffs.
                if f.name not in self.curTeam.players_with_pickoffs:
                    self.curTeam.players_with_pickoffs.append(f.name)
                    
                # Add the (edited) active Event to the player's list of events.
                self.curTeam.players[f.name].events.append(f)
                self.curTeam.players[f.name].fielding.picks += 1
                
                self.curTeam.podict = {}
                self.activePickedoff = 0
                self.activeEvent = None
            
            # Switch back the Team objects.
            if self.curTeam == self.away: self.curTeam = self.home
            elif self.curTeam == self.home: self.curTeam = self.away            

    def endElement(self, name):
        if (name == 'player'):
            self.playerID = -1
