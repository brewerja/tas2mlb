#!/usr/bin/python


class Game:
    def __init__(self):
        self.innings = []
        self.linescore = []


class Inning:
    def __init__(self):
        self.halfs = []


class HalfInning:
    def __init__(self):
        self.events = []


class Event:
    def __init__(self, scoreHome, scoreVisitor):
        self.type = 'GENERIC'
        self.scoreHome = scoreHome
        self.scoreVisitor = scoreVisitor
        self.errorFielders = {}


class Line:
    pass
