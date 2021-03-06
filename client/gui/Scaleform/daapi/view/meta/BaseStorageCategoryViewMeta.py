# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseStorageCategoryViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BaseStorageCategoryViewMeta(BaseDAAPIComponent):

    def setActiveState(self, isActive):
        self._printOverrideError('setActiveState')

    def playInfoSound(self):
        self._printOverrideError('playInfoSound')

    def scrolledToBottom(self):
        self._printOverrideError('scrolledToBottom')

    def as_showDummyScreenS(self, show):
        return self.flashObject.as_showDummyScreen(show) if self._isDAAPIInited() else None

    def as_showFilterWarningS(self, data):
        return self.flashObject.as_showFilterWarning(data) if self._isDAAPIInited() else None

    def as_getCardsDPS(self):
        return self.flashObject.as_getCardsDP() if self._isDAAPIInited() else None

    def as_scrollToItemS(self, itemIntCD):
        return self.flashObject.as_scrollToItem(itemIntCD) if self._isDAAPIInited() else None
