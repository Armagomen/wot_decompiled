# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_control/arena_info/halloween_squad_finder.py
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder

class HalloweenTeamScopeNumberingFinder(TeamScopeNumberingFinder):
    __slots__ = ()

    @classmethod
    def _getSquadRange(cls):
        return xrange(2, 6)
