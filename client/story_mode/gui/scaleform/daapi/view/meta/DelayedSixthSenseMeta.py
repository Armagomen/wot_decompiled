# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/meta/DelayedSixthSenseMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DelayedSixthSenseMeta(BaseDAAPIComponent):

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self, force):
        return self.flashObject.as_hide(force) if self._isDAAPIInited() else None

    def as_updateS(self, value):
        return self.flashObject.as_update(value) if self._isDAAPIInited() else None
