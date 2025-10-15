# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/messages/vehicle_errors.py
from gui.Scaleform.daapi.view.battle.shared.messages import VehicleErrorMessages

class HalloweenVehicleErrorMessages(VehicleErrorMessages):

    def _addGameListeners(self):
        super(HalloweenVehicleErrorMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
        return

    def _removeGameListeners(self):
        super(HalloweenVehicleErrorMessages, self)._removeGameListeners()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.clear()
