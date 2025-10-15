# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWPersonalDeathZone.py
import BigWorld
from PersonalDeathZone import PersonalDeathZone

class HWPersonalDeathZone(PersonalDeathZone):

    def __init__(self):
        super(HWPersonalDeathZone, self).__init__()
        self._startTime = BigWorld.serverTime()

    def onTriggerActivated(self, args):
        if self._isOwnTrigger(args):
            self._hideMarker()
        super(HWPersonalDeathZone, self).onTriggerActivated(args)

    def onTriggerDeactivated(self, args):
        if self._isOwnTrigger(args):
            self._showMarker()
        super(HWPersonalDeathZone, self).onTriggerDeactivated(args)

    def _showMarker(self):
        if not self._equipment.areaVisibleToEnemies:
            if self._isAttackerEnemy():
                return
            equipmentsCtrl = self.sessionProvider.shared.equipments
            delay = self.delay - (BigWorld.serverTime() - self._startTime)
            self._markerItem = equipmentsCtrl and delay > 0 and equipmentsCtrl.showMarker(self._equipment, self.position, self._direction, delay)
