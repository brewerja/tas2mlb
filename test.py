#!/usr/bin/python

import pickle
from bsddb3 import db

class Player:
    def __init__(self,gameID,name,hits):
        self.gameID = gameID
        self.name = name
        self.hits = hits
        self.string = gameID+name

def getName(player):
    return pickle.loads(player).name

def getGame(player):
    return pickle.loads(player).game

if __name__=='__main__':

    playerDB = db.DB()
    playerDB.open(None, None, db.DB_RECNO, db.DB_CREATE)

    gameDB = db.DB()
    gameDB.set_flags(db.DB_DUPSORT)
    gameDB.open(None, None, db.DB_BTREE, db.DB_CREATE)

    nameDB = db.DB()
    nameDB.set_flags(db.DB_DUPSORT)
    nameDB.open(None, None, db.DB_BTREE, db.DB_CREATE)

    p1 = Player('vica729', 'Kyle Hald', '3')
    p2 = Player('vica729', 'Nick Kuroczko', '4')
    p3 = Player('vica729', 'Austin Booker', '2')
    p4 = Player('vica729', 'Nick Boullosa', '1')
    p5 = Player('vica729', 'Ryan Camp', '1')
    p6 = Player('cavi728', 'Kyle Hald', '3')
    p7 = Player('cavi728', 'Nick Kuroczko', '4')
    p8 = Player('cavi728', 'Austin Booker', '2')
    p9 = Player('cavi728', 'Nick Boullosa', '1')
    p10 = Player('cavi728', 'Ryan Camp', '1')
    p11 = Player('fxvi727', 'Kyle Hald', '3')
    p12 = Player('fxvi727', 'Nick Kuroczko', '4')
    p13 = Player('fxvi727', 'Austin Booker', '2')
    p14 = Player('fxvi727', 'Nick Boullosa', '1')
    p15 = Player('fxvi727', 'Ryan Camp', '1')

    players = (p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15)

    for each in players:
        playerDB.append(pickle.dumps(each))

    playerDB.associate(nameDB,getName)
    playerDB.associate(gameDB,getGame)

    cursor = playerDB.cursor()
    rec = cursor.first()
    print "------------ Primary DB ---------------"
    while rec:
        print str(rec[0])+' '+getName(rec[1])
        rec = cursor.next()

    print "---------------------------------------"
    cursor2 = gameDB.cursor()
    rec = cursor2.first()
    while rec:
        print getName(rec[0])
        rec = cursor2.next()

    gameDB.close()
    nameDB.close()
    playerDB.close()
