#!/usr/bin/python

from xml.sax import saxutils
from team2 import *
import copy
import datetime

class parsePlayByPlay(saxutils.handler.ContentHandler):
    def __init__(self, gameData):
        # The home and away teams
        self.gameData = gameData
        self.inPlays = -1
        self.firstPlay = -1
        self.homeScore = 0
        self.visitorScore = 0
        self.topHalf = 1
        self.activeSub = 0
        self.curPitcher = ''
        self.playHasOccurred = -1
        
    def startElement(self, name, attrs):
        if (name == 'venue'):
            self.gameData.stadium = attrs.get('stadium')
            self.gameData.location = attrs.get('location')            
            date = attrs.get('date').split('/')
            self.gameData.date = datetime.date(int(date[2]),int(date[0]),int(date[1]))
            self.gameData.visitorLongName = attrs.get('visname')
            self.gameData.homeLongName = attrs.get('homename')
            self.gameData.visid = attrs.get('visid')
            self.gameData.homeid = attrs.get('homeid')
            longNames = [self.gameData.visitorLongName, self.gameData.homeLongName]
            for first, name in enumerate(longNames):
                if name == 'Vienna Senators':
                    name = 'Vienna'
                elif name == 'Carney Pirates':
                    name = 'Carney'
                elif name == 'S Maryland Cardinals':
                    name =  'Southern Maryland'                   
                elif name == 'Fairfax Nationals':
                    name = 'Fairfax'
                elif name == 'DC Grays':
                    name = 'DC'
                elif name == 'Beltway Blue Caps':
                    name = 'Beltway'
                elif name == 'McLean Raiders':
                    name = 'McLean'                                                                                
                elif name == 'Arlington Diamonds':
                    name = 'Arlington'                                                                                
                elif name == 'Gaithersburg Giants':
                    name = 'Gaithersburg'
                elif name == 'Western HC Renegades':
                    name = 'Western Howard Co.'
                elif name == 'Columbia Reds':
                    name = 'Columbia'
                elif name == 'Putty Hill PB':
                    name = 'Putty Hill (Blue)'
                elif name == 'Putty Hill PG':
                    name = 'Putty Hill (Gold)'
                # elif name == 'MD Black Barons':
                #    name = 'Maryland'
                #elif name == 'Maryland Nationals':
                #    name = 'Maryland'                   
                #elif name == 'Maryland Orioles':
                #    name = 'Maryland' 
                if first:
                    self.gameData.visitorShortName = name
                else:
                    self.gameData.homeShortName = name
        elif (name == 'linescore'):
            line = Line()
            line.line = attrs.get('line').split(",")
            line.runs = int(attrs.get('runs'))
            line.hits = int(attrs.get('hits'))
            line.errs = int(attrs.get('errs'))
            line.lob = int(attrs.get('lob'))
            self.gameData.linescore.append(line)                            
        elif (name == 'plays'):
            self.inPlays = 1
        elif (name == 'inning'):
            self.curInning = Inning()
            self.gameData.innings.append(self.curInning)
        elif (name == 'batting'):
            self.curHalf = HalfInning()
            self.curInning.halfs.append(self.curHalf)
            self.firstPlay = 1
            self.playHasOccurred = -1
            if attrs.get('vh')=='V':
                self.topHalf = 1
            else:
                self.topHalf = 0
        elif (name == 'play'):
            self.curEvent = Event(self.visitorScore,self.homeScore)
            self.curHalf.events.append(self.curEvent)
            if self.firstPlay == 1:
                self.curHalf.pitcherStartingInning = attrs.get('pitcher')
            self.oldcurPitcher = self.curPitcher
            self.curPitcher = attrs.get('pitcher')
        elif (name == 'sub'):
            if attrs.get('pos') == 'p':
                self.curEvent.type = 'RELIEVER'
                if attrs.get('for',0) == 0:
                        self.curEvent.leavingPitcher = self.curPitcher                
                if self.playHasOccurred == -1:
                    self.curHalf.pitcherStartingInning = attrs.get('who')
                if self.curPitcher == '/':
                    print self.oldcurPitcher
                    self.curEvent.leavingPitcher = self.oldcurPitcher
            else:
                self.curEvent.type = 'SUB'
            self.activeSub = 1
            
        elif (name == 'batter'):
            self.activeSub = 0
            self.playHasOccurred = 1
            if attrs.get('scored',0) != 0:
                self.curEvent.type = 'SCORING'
                if self.topHalf:
                    self.visitorScore += 1
                else:
                    self.homeScore += 1
        elif (name == 'runner'):
            if attrs.get('scored',0) != 0:
                self.curEvent.type = 'SCORING'            
                if self.topHalf:
                    self.visitorScore += 1
                else:
                    self.homeScore += 1
        elif (name == 'fielder'):
            if (attrs.get('e',0) != 0):
                self.curEvent.errorFielders[attrs.get('pos')] = attrs.get('name')
        elif (name == 'narrative'):
            self.curEvent.text = attrs.get('text')
        elif (name == 'innsummary'):
            self.curHalf.runs = attrs.get('r')
            self.curHalf.hits = attrs.get('h')
            self.curHalf.errors = attrs.get('e')
            self.curHalf.leftonbase = attrs.get('lob')

    def endElement(self, name):
        if (name == 'plays'):
            self.inPlays = -1
        elif (name == 'play'):
            self.firstPlay = -1
            self.curEvent.scoreHome = self.homeScore
            self.curEvent.scoreVisitor = self.visitorScore
            
