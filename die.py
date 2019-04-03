#!/usr/bin/env python
__author__ = "Arana Fireheart"

from random import randint

class Die(object):
    def __init__(self, startingNumberOfSides = 6):
        self.numberOfSides = startingNumberOfSides
        self.color = "white"
        self.value = 6
        self.minValue = 1
        self.maxValue = self.numberOfSides

    def __str__(self):
        return "{0}".format(self.value)

    def setNumberOfSides(self, newNumberOfSides):
        self.numberOfSides = newNumberOfSides

    def getNumberOfSides(self):
        return self.numberOfSides

    def setColor(self, newColor):
        self.color = newColor

    def getColor(self):
        return self.color

    def setValue(self, newValue):
        self.value = newValue

    def getValue(self):
        return self.value

    def roll(self):
        self.value = randint(1, self.getNumberOfSides())
        return self.getValue()
