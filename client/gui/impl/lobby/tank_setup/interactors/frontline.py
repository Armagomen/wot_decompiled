# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/frontline.py
from BWUtil import AsyncReturn
from adisp import adisp_process
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from gui.impl.lobby.tank_setup.interactors.base_equipment import BaseEquipmentInteractor
from gui.shared.event_dispatcher import showFrontlineConfirmDialog
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from wg_async import wg_await, wg_async

class ReservesAutoRenewal(BaseAutoRenewal):
    __slots__ = ()

    def getValue(self):
        return True

    @adisp_process
    def processVehicleAutoRenewal(self, callback):
        action = ActionsFactory.getAction(ActionsFactory.FRONTLINE_INSTALL_RESERVES, vehicle=self._vehicle, skillsInteractor=None, skipConfirm=True)
        if action is not None:
            result = yield action.doAction()
            if not result:
                callback(result)
                return
        self.setLocalValue(None)
        callback(None)
        return


class FrontlineInteractor(BaseEquipmentInteractor):
    __slots__ = ('_checkboxState',)

    def __init__(self, vehItem):
        super(FrontlineInteractor, self).__init__(vehItem)
        self._checkboxState = False

    def getName(self):
        return TankSetupConstants.BATTLE_ABILITIES

    def getInstalledLayout(self):
        return self.getItem().battleAbilities.installed

    def getCurrentLayout(self):
        return self.getItem().battleAbilities.layout

    def getSetupLayout(self):
        return self.getItem().battleAbilities.setupLayouts

    def getCheckboxState(self):
        return self._checkboxState

    def revert(self):
        self.getItem().battleAbilities.setLayout(*self.getPlayerLayout())
        self._resetInstalledIndices()
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(FrontlineInteractor, self).updateFrom(vehicle, onlyInstalled)
        items = self.getItem().battleAbilities
        items.setInstalled(*vehicle.battleAbilities.installed)
        items.setupLayouts.setSetups(vehicle.battleAbilities.setupLayouts.setups)
        self._playerLayout = vehicle.battleAbilities.layout.copy()
        if not onlyInstalled:
            self.getItem().battleAbilities.setLayout(*vehicle.battleAbilities.layout)

    @adisp_process
    def confirm(self, callback, skipDialog=False):
        vehicle = self.getItem()
        action = ActionsFactory.getAction(ActionsFactory.FRONTLINE_INSTALL_RESERVES, vehicle=vehicle, skillsInteractor=self, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @adisp_process
    def buyAbilities(self, skillIds, callback):
        action = ActionsFactory.getAction(ActionsFactory.BUY_BATTLE_ABILITIES, skillIds)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def setCheckboxState(self, state):
        self._checkboxState = state

    @wg_async
    def showBuyConfirmDialog(self):
        vehicle = self.getItem()
        result = yield wg_await(showFrontlineConfirmDialog(skillsInteractor=self, vehicleType=vehicle.type))
        raise AsyncReturn(result)

    @wg_async
    def showExitConfirmDialog(self):
        vehicle = self.getItem()
        result = yield wg_await(showFrontlineConfirmDialog(isBuy=False, vehicleType=vehicle.type, skillsInteractor=self))
        raise AsyncReturn(result)

    def getChangedList(self):
        return self.getCurrentLayout() or [] if self._checkboxState else super(FrontlineInteractor, self).getChangedList() or []

    def _createAutoRenewal(self):
        return ReservesAutoRenewal(self.getItem())
