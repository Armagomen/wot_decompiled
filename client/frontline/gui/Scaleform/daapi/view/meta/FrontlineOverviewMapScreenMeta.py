# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineOverviewMapScreenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FrontlineOverviewMapScreenMeta(BaseDAAPIComponent):

    def as_setKeyBindingsS(self, data):
        return self.flashObject.as_setKeyBindings(data) if self._isDAAPIInited() else None

    def as_updateLaneButtonNamesS(self, west, center, east):
        return self.flashObject.as_updateLaneButtonNames(west, center, east) if self._isDAAPIInited() else None
