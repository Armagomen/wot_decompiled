# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingViewMeta.py
from gui.Scaleform.framework.entities.View import View

class WaitingViewMeta(View):

    def as_showWaitingS(self, message, softStart, showBg):
        return self.flashObject.as_showWaiting(message, softStart, showBg) if self._isDAAPIInited() else None

    def as_showBackgroundImgS(self, img):
        return self.flashObject.as_showBackgroundImg(img) if self._isDAAPIInited() else None

    def as_hideWaitingS(self):
        return self.flashObject.as_hideWaiting() if self._isDAAPIInited() else None
