#!/usr/bin/python

# Where possible, class attributes use the same attribute name as the XML spec

class Game:
    def __init__(self):
        pass

# Represent one team in a game.  Mainly just a collection of player objects.
class Team:
    def __init__(self):
        # Roster.  A list of all the players on the team, indexed b player id.
        self.players = {}
        # Inning by inning score.
        self.linescore = []
        self.runs = 0 # Runs
        self.hits = 0 # Hits
        self.errs = 0 # Errors
        self.ab = 0   # At Bats
        self.rbi = 0  # RBI
        self.bb = 0   # Walks
        self.so = 0   # Strikeouts
        self.sb = 0   # Stolen Bases
        self.cs = 0   # Caught Stealings
        self.indp = 0 # Double Plays Turned
        self.intp = 0 # Triple Plays Turned
        self.pickedoff = 0 # Number of times picked off

        # Lineup.  A list of batters 1-n.  Each spot in the lineup is a list,
        # if a substitution is made, the new batter is appeneded to the list
        # for his spot in the lineup.  Entries are just player IDs, the roster
        # must be referenced to obtain full information (name, stats, etc.)
        # We'll accept as many spots as the user wants
        self.lineup = []
        self.pitchingorder = []
        self.doubles = []
        self.triples = []
        self.homeruns = []
        self.rbi2out = []
        self.batters_with_rbi = []
        self.batters_with_lob2out = []
        self.batters_with_gidp = []
        self.batters_with_sh = []
        self.batters_with_sf = []        
        self.wrisp = []
        self.lob = 0
        self.playerlob = 0
        self.players_with_errors = []
        self.players_with_pb = []
        self.players_with_sb = []
        self.curStealers = []
        self.players_with_cs = []
        self.curCaughtStealers = []
        self.dpdict = {} 
        self.tpdict = {}
        self.podict = {}
        self.events = []
        self.players_pickedoff = []
        self.been_hbp = 0
        self.been_ibb = 0
        self.lisp2out = []
        self.players_with_pickoffs = []
        self.activePickoff = 0
        self.outfielders_with_assists = []
        self.pinchhitters = []
        self.pinchrunners = []
        self.pitcherTexts = []
        

    # Set the given spot in the lineup.  Can be used for substitution or to
    # initialize the lineup
    def setLineupSpot(self, spot, playerID):
        # The interface takes spots as 1-n, but the index starts at 0.  We
        # adjust internally to hide the complexity from the parser/printer.
        # If given a spot beyond what we have, pad with empty lists
        if (spot < 1):
            return
        sz = len(self.lineup)
        if (spot > sz):
            for i in range(spot - sz):
                self.lineup.append([])
        self.lineup[spot-1].append(playerID)
        
    def setPitchingSpot(self, appear, playerID):
        # The interface takes spots as 1-n, but the index starts at 0.  We
        # adjust internally to hide the complexity from the parser/printer.
        # If given a spot beyond what we have, pad with empty lists
        if (appear < 1):
            return
        sz = len(self.pitchingorder)
        if (appear > sz):
            for i in range(appear - sz):
                self.pitchingorder.append([])
        self.pitchingorder[appear-1].append(playerID)
        print       

    # Return the list of all the players who batted in the pos-th spot
    # If the requested spot does not exist, an empty list is returned.
    def getLineupSpot(self, spot):
        # The interface takes spots as 1-9, but the index starts at 0.  We
        # adjust internally to hide the complexity from the parser/printer.
        if (spot > len(self.lineup) or spot < 1 or spot > 9):
            return []
        return self.lineup[spot-1] 
    
    def getPitchingSpot(self, appear):
        if (appear > len(self.pitchingorder) or appear < 1 ):
            return []
        return self.pitchingorder[appear-1]     

    def getLineupLength(self):
        return len(self.lineup)
    
    def getPitchingOrderLength(self):
        return len(self.pitchingorder)    

# Represent one player in a game.  Mainly a collection of stats.
# id is a unique identifier, currently the shortname attribute
# name is the player's full name
class Player:
    def __init__(self, id, name, pos):
        self.id, self.name, self.pos = id, name, pos
        self.hitting = Hitting()
        self.pitching = Pitching()
        self.fielding = Fielding()
        self.events =[]
        self.poslist = []
        
class Event:
    def __init__(self, type, name, play):
        self.type, self.name, self.play = type, name, play 
        
class Hitting:
    def __init__(self):
        # HITTING STATS
        self.ab = 0     # at bats
        self.r = 0      # runs
        self.h = 0      # hits
        self.double = 0 # doubles
        self.triple = 0 # triples
        self.hr = 0     # home runs
        self.rbi = 0    # rbis        
        self.bb = 0     # walks
        self.hbp = 0    # hit by pitch
        self.so = 0     # strikeouts        
        self.kl = 0     # strikeouts looking
        self.hitdp = 0  # double plays hit into
        self.gdp = 0    # double plays grounded into
        self.sf = 0     # sacrifice flies
        self.sh = 0     # sac bunts
        self.sb = 0     # stolen bases
        self.cs = 0     # caught stealings
        self.ground = 0 # ground ball
        self.fly = 0    # fly ball
        self.picked = 0 # picked offs
        self.lob = 0    # left on base
        self.rbi2out = 0 # 2-out rbi
        self.lisp2out = 0 # Runners left in scoring position, 2-out
        
class Fielding:
    def __init__(self):
        # FIELDING STATS
        self.po = 0     # put outs
        self.a = 0      # assists
        self.e = 0      # errors
        self.pb = 0     # passed balls
        self.picks = 0  # pickoffs (catcher or pitcher)
        self.ofa = 0    # outfield assists
        
class Pitching:
    def __init__(self):
        # PITCHING STATS
        self.appear = 0
        self.win = None 
        self.loss = None
        self.gs = 0
        self.ip = 0
        self.h = 0
        self.r = 0
        self.er = 0
        self.bb = 0
        self.so = 0
        self.sha = 0
        self.bf = 0
        self.ab = 0
        self.double = 0
        self.triple = 0
        self.hr = 0
        self.kl = 0
        self.fly = 0
        self.ground = 0
        self.inherits = 0
        self.inheritr = 0  
        self.bk = 0
        self.wp = 0 
        self.pitches = None
            