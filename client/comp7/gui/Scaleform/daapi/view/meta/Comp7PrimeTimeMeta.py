# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/meta/Comp7PrimeTimeMeta.py
from gui.Scaleform.daapi.view.lobby.prime_time_view_base import PrimeTimeViewBase

class Comp7PrimeTimeMeta(PrimeTimeViewBase):

    def as_setHeaderTextS(self, value):
        return self.flashObject.as_setHeaderText(value) if self._isDAAPIInited() else None

    def as_setBackgroundSourceS(self, source):
        return self.flashObject.as_setBackgroundSource(source) if self._isDAAPIInited() else None
