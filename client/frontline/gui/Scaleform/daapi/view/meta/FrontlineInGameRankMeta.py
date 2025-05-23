# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineInGameRankMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FrontlineInGameRankMeta(BaseDAAPIComponent):

    def levelUpAnimationComplete(self):
        self._printOverrideError('levelUpAnimationComplete')

    def as_triggerLevelUpS(self, previousProgress):
        return self.flashObject.as_triggerLevelUp(previousProgress) if self._isDAAPIInited() else None

    def as_updateProgressS(self, previousProgress, currentProgress):
        return self.flashObject.as_updateProgress(previousProgress, currentProgress) if self._isDAAPIInited() else None

    def as_setRankS(self, data):
        return self.flashObject.as_setRank(data) if self._isDAAPIInited() else None
