# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/combined_crew_skill.py
from typing import Optional
from items import tankmen

class CombinedCrewSkill(object):
    __slots__ = ('tankmanLevel', 'levelIncrease', 'isTankmanActive', 'hasActiveTankmanForBooster', 'boosterMultiplier')

    def __init__(self, tankmanLevel, levelIncrease, isTankmanActive, hasActiveTankmanForBooster=False, boosterMultiplier=None):
        self.tankmanLevel = tankmanLevel
        self.levelIncrease = levelIncrease
        self.isTankmanActive = isTankmanActive
        self.hasActiveTankmanForBooster = hasActiveTankmanForBooster
        self.boosterMultiplier = boosterMultiplier

    @property
    def level(self):
        return int(round(self._floatLevel()))

    def _floatLevel(self):
        if self.boosterMultiplier is None:
            return self.tankmanLevel + self.levelIncrease
        else:
            return tankmen.MAX_SKILL_LEVEL + self.levelIncrease if self.tankmanLevel < tankmen.MAX_SKILL_LEVEL or not self.isTankmanActive else (tankmen.MAX_SKILL_LEVEL + self.levelIncrease) * self.boosterMultiplier

    @property
    def isActive(self):
        return self.isTankmanActive or self.boosterMultiplier is not None and self.hasActiveTankmanForBooster

    def __str__(self):
        return 'CombinedCrewSkill(level={}, isActive={}, tankmanLevel={}, levelIncrease={}, isTankmanActive={}, boosterMultiplier={})'.format(self.level, self.isActive, self.tankmanLevel, self.levelIncrease, self.isTankmanActive, self.boosterMultiplier)
