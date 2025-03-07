# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/battle_results.py
import typing
from Event import Event
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl

class IBattleResultsService(object):
    __slots__ = ()
    onResultPosted = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def requestResults(self, ctx, callback=None):
        raise NotImplementedError

    def requestEmblem(self, ctx, callback=None):
        raise NotImplementedError

    def postResult(self, result, needToShowUI=True):
        raise NotImplementedError

    def areResultsPosted(self, arenaUniqueID):
        raise NotImplementedError

    def getResultsVO(self, arenaUniqueID):
        raise NotImplementedError

    def getPresenter(self, arenaUniqueID):
        raise NotImplementedError

    def saveStatsSorting(self, bonusType, iconType, sortDirection):
        raise NotImplementedError

    def applyAdditionalBonus(self, arenaUniqueID):
        raise NotImplementedError

    def isAddXPBonusApplied(self, arenaUniqueID):
        raise NotImplementedError

    def isAddXPBonusEnabled(self, arenaUniqueID):
        raise NotImplementedError

    def getAdditionalXPValue(self, arenaUniqueID):
        raise NotImplementedError

    def submitPlayerSatisfactionRating(self, areneUniqueID, rating):
        raise NotImplementedError

    def getPlayerSatisfactionRating(self, arenaUniqueID):
        raise NotImplementedError

    def isCrewSameForArena(self, arenaUniqueID):
        raise NotImplementedError

    def isXPToTManSameForArena(self, arenaUniqueID):
        raise NotImplementedError

    def getVehicleForArena(self, arenaUniqueID):
        raise NotImplementedError
