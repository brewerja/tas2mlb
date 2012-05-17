#!/usr/bin/python

from bsddb3 import db
import pickle


def getShortName(name):
    if name == 'Vienna Senators':
        name = 'Vienna'
    elif name == 'Carney Pirates':
        name = 'Carney'
    elif name == 'S Maryland Cardinals':
        name = 'Southern Maryland'
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
   #     name = 'Maryland'
   # elif name == 'Maryland Nationals':
   #     name = 'Maryland'
   # elif name == 'Maryland Orioles':
   #     name = 'Maryland'
    return name


def printERA(dbName, playerName, date):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    er, ipWhole, ipThirds = 0, 0, 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            er += p.pitching.er
            ipWhole += int(float(p.pitching.ip))
            ipThirds += int(round(float(p.pitching.ip) % 1 / .1, 2))
        rec = cursor.next()
    playerDB.close()
    if er == 0 and ipWhole == 0 and ipThirds == 0:
        return '0.00'
    elif er > 0 and ipWhole == 0 and ipThirds == 0:
        return 'Inf'
    else:
        era = round(9 * er / (ipWhole + ipThirds / 3.), 2)
        return '%.2f' % era


def printAVG(dbName, playerName, date):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    h, ab = 0, 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            h += p.hitting.h
            ab += p.hitting.ab
        rec = cursor.next()
    playerDB.close()
    if h == 0 and ab == 0:
        avg = 0.000
    else:
        avg = round(float(h) / float(ab), 3)
    if ab > 0 and h == ab:
        return '1.000'
    else:
        return str.lstrip('%.3f' % avg, '0')


def printOBP(dbName, playerName, date):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    h, bb, hbp, ab, sf = 0, 0, 0, 0, 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            h += p.hitting.h
            bb += p.hitting.bb
            hbp += p.hitting.hbp
            ab += p.hitting.ab
            sf += p.hitting.sf
        rec = cursor.next()
    playerDB.close()

    topFrac = h + bb + hbp
    bottomFrac = ab + bb + hbp + sf

    if bottomFrac != 0:
        obp = round(float(topFrac) / float(bottomFrac), 3)
        if topFrac == bottomFrac:
            return '1.000'
        else:
            return str.lstrip('%.3f' % obp, '0')
    else:
        return 'NaN'


def printHittingTotal(dbName, playerName, date, stat):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    total = 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            total += getattr(p.hitting, stat, 0)
        rec = cursor.next()
    playerDB.close()
    return str(total)


def printPassedBalls(dbName, playerName, date):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    pb = 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            pb += p.fielding.pb
        rec = cursor.next()
    playerDB.close()
    return str(pb)


def printErrors(db1Name, db2Name, playerName, date):
    errors = 0

    playerDB = db.DB()
    playerDB.open(db1Name, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            errors += p.fielding.e
        rec = cursor.next()
    playerDB.close()

    playerDB = db.DB()
    playerDB.open(db2Name, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            errors += p.fielding.e
        rec = cursor.next()
    playerDB.close()

    return str(errors)


def printPitcherRecord(dbName, playerName, date):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    wins = 0
    losses = 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            if p.pitching.win != 0:
                wins += 1
            if p.pitching.loss != 0:
                losses += 1
        rec = cursor.next()
    playerDB.close()
    return str(wins) + "-" + str(losses)


def printSaves(dbName, playerName, date):
    playerDB = db.DB()
    playerDB.open(dbName, None, db.DB_BTREE)
    cursor = playerDB.cursor()
    rec = cursor.set(playerName)
    saves = 0
    while rec:
        p = pickle.loads(rec[1])
        if p.name != playerName:
            break
        if int(p.date) <= date:
            if p.pitching.save != 0:
                saves += 1
        rec = cursor.next()
    playerDB.close()
    return str(saves)


def printTeamRecord(dbName, teamID, date):
    teamDB = db.DB()
    teamDB.open(dbName, None, db.DB_BTREE)
    cursor = teamDB.cursor()
    rec = cursor.first()
    wins = 0
    losses = 0
    while rec:
        if int(rec[0]) <= date:
            dict = pickle.loads(rec[1])
            if dict['winner'] == teamID:
                wins += 1
            elif dict['loser'] == teamID:
                losses += 1
        rec = cursor.next()
    teamDB.close()
    return str(wins) + "-" + str(losses)


def printTeamStreak(dbName, teamID, date):
    teamDB = db.DB()
    teamDB.open(dbName, None, db.DB_BTREE)
    cursor = teamDB.cursor()
    recFinal = cursor.last()
    recFirst = cursor.first()

    rec = cursor.set(str(date))  # Need to be last of that date

    while rec:
        if int(rec[0]) > date:
            rec = cursor.prev()
            break
        elif rec == recFinal:
            break
        else:
            rec = cursor.next()

    winning = 0
    losing = 0

    while rec:
        dict = pickle.loads(rec[1])
        if dict['winner'] == teamID:
            winning = 1
            rec = cursor.prev()
            break
        elif dict['loser'] == teamID:
            losing = 1
            rec = cursor.prev()
            break
        else:
            if rec == recFirst:
                break
            else:
                rec = cursor.prev()

    while rec:
        dict = pickle.loads(rec[1])
        if dict['winner'] == teamID or dict['loser'] == teamID:
            if winning != 0:
                if dict['winner'] == teamID:
                    winning += 1
                if dict['loser'] == teamID:
                    return 'Won ' + str(winning)
            elif losing != 0:
                if dict['winner'] == teamID:
                    return 'Lost ' + str(losing)
                if dict['loser'] == teamID:
                    losing += 1
            elif winning == 0 and losing == 0:
                return ""
        rec = cursor.prev()

    if losing != 0:
        return 'Lost ' + str(losing)
    elif winning != 0:
        return 'Won ' + str(winning)


def prettyInning(inning):
    if inning == 11 or inning == 12 or inning == 13:
        suffix = "th"
    else:
        mod = inning % 10
        if mod == 1:
            suffix = "st"
        elif mod == 2:
            suffix = "nd"
        elif mod == 3:
            suffix = "rd"
        else:
            suffix = "th"
    return str(inning) + suffix


def parseErrors(text, numErrors):
    typesOfErrors = {'an error': '', 'fielding error': 'fielding',
                     'throwing error': 'throw', 'muffed throw': 'muffed throw',
                     'dropped fly': 'dropped fly',
                     "catcher's interference": 'catcher interference',
                     'Dropped foul ball': 'dropped foul'}
    x, y = -1, -1
    returnText = ''
    for i in range(0, numErrors):
        for type in typesOfErrors:
            x = text.find(type, x + 1)
            if x != -1:
                if returnText != '':
                    returnText = returnText + ", " + typesOfErrors[type]
                else:
                    returnText = typesOfErrors[type]
                break
    if returnText == '':
        return
    else:
        return returnText


def translateNarrative(text):
    if text.find('singled') != -1:
        return 'singled'
    elif text.find('doubled') != -1:
        return 'doubled'
    elif text.find('tripled') != -1:
        return 'tripled'
    elif text.find('homered') != -1:
        return 'homered'
    elif text.find('walked') != -1:
        return 'walked'
    elif text.find('hit by pitch') != -1:
        return 'hit by pitch'
    elif text.find('struck out') != -1:
        return 'struck out'
    elif text.find('grounded out') != -1:
        return 'grounded out'
    elif text.find('reached on a fielder\'s choice') != -1:
        return 'reached on a fielder\'s choice'
    elif text.find('lined out') != -1:
        return 'lined out'
    elif text.find('popped up') != -1:
        return 'popped out'
    elif text.find('flied out') != -1:
        return 'flied out'
    elif text.find('fouled out') != -1:
        return 'fouled out'
    elif text.find('reached on a fielding error') != -1:
        return 'reached on a fielding error'
    elif text.find('reached on an error') != -1:
        return 'reached on an error'
    elif text.find('reached on a throwing error') != -1:
        return 'reached on a throwing error'
    elif text.find('reached on a dropped fly') != -1:
        return 'reached on a dropped fly'
    elif text.find('reached on a muffed throw') != -1:
        return 'reached on a muffed throw'
    elif text.find('grounded into double play') != -1:
        return 'grounded into double play'
    elif text.find('lined into double play') != -1:
        return 'lined into double play'
    elif text.find('hit into double play') != -1:
        return 'hit into double play'
    elif text.find('fouled into double play') != -1:
        return 'fouled into double play'
    elif text.find('flied into double play') != -1:
        return 'flied into double play'
    elif text.find('popped into double play') != -1:
        return 'popped into double play'
    elif text.find('grounded into triple play') != -1:
        return 'grounded into triple play'
    elif text.find('lined into triple play') != -1:
        return 'lined into triple play'
    elif text.find('hit into triple play') != -1:
        return 'hit into triple play'
    elif text.find('fouled into triple play') != -1:
        return 'fouled into triple play'
    elif text.find('flied into triple play') != -1:
        return 'flied into triple play'
    elif text.find('popped into triple play') != -1:
        return 'popped into triple play'
    elif text.find('reached on catcher\'s interference') != -1:
        return 'reached on catcher\'s interference'
    elif text.find('out on batter\'s interference') != -1:
        return 'out on batter\'s interference'
    elif text.find('infield fly') != -1:
        return 'infield fly'
    elif text.find('out at first') != -1:
        return 'out at first'
    elif text.find('No play.') != -1:
        return ''
    elif text.find('Dropped foul ball') != -1:
        return ''
