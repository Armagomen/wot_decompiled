# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineMissionsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FrontlineMissionsPanelMeta(BaseDAAPIComponent):

    def as_setPrimaryMissionS(self, messageData):
        return self.flashObject.as_setPrimaryMission(messageData) if self._isDAAPIInited() else None

    def as_setNearestHQS(self, index):
        return self.flashObject.as_setNearestHQ(index) if self._isDAAPIInited() else None

    def as_setMissionDescriptionValueS(self, descValue):
        return self.flashObject.as_setMissionDescriptionValue(descValue) if self._isDAAPIInited() else None
