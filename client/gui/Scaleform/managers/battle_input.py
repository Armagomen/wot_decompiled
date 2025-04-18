# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/battle_input.py
import Keys
from AvatarInputHandler import aih_global_binding
from aih_constants import CTRL_MODE_NAME
from gui.battle_control import avatar_getter
from gui.battle_control import event_dispatcher
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import ICommendationsController
from soft_exception import SoftException
import CommandMapping

class BattleGUIKeyHandler(object):

    def handleEscKey(self, isDown):
        return False


class BattleGameInputMgr(object):
    __slots__ = ('__consumers', '__keyHandlers')
    __ctrlModeName = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.CTRL_MODE_NAME)
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    commendationsCtrl = dependency.descriptor(ICommendationsController)

    def __init__(self):
        super(BattleGameInputMgr, self).__init__()
        self.__consumers = []
        self.__keyHandlers = []

    def start(self):
        pass

    def stop(self):
        del self.__consumers[:]
        del self.__keyHandlers[:]

    def enterGuiControlMode(self, consumerID, cursorVisible=True, enableAiming=True, stopVehicle=False):
        if consumerID not in self.__consumers:
            if not self.__consumers:
                avatar_getter.setForcedGuiControlMode(True, stopVehicle=stopVehicle, cursorVisible=cursorVisible, enableAiming=enableAiming)
            self.__consumers.append(consumerID)

    def leaveGuiControlMode(self, consumerID):
        if consumerID in self.__consumers:
            self.__consumers.remove(consumerID)
            if not self.__consumers and isPlayerAvatar():
                avatar_getter.setForcedGuiControlMode(False)

    def hasGuiControlModeConsumers(self, *consumersIDs):
        for consumerID in consumersIDs:
            if consumerID in self.__consumers:
                return True

        return False

    def registerGuiKeyHandler(self, handler):
        if not isinstance(handler, BattleGUIKeyHandler):
            raise SoftException('Handler should extends BattleGUIKeyHandler')
        if handler not in self.__keyHandlers:
            self.__keyHandlers.append(handler)

    def unregisterGuiKeyHandler(self, handler):
        if handler in self.__keyHandlers:
            self.__keyHandlers.remove(handler)

    def handleKey(self, isDown, key, mods):
        isEventBattle = self.guiSessionProvider.arenaVisitor.gui.isEventBattle()
        if key == Keys.KEY_ESCAPE:
            if self.__keyHandlers:
                for handler in self.__keyHandlers[:]:
                    if handler.handleEscKey(isDown):
                        return True

            if isDown and self.__ctrlModeName != CTRL_MODE_NAME.MAP_CASE:
                if isEventBattle:
                    event_dispatcher.toggleEventStats(False)
                else:
                    event_dispatcher.toggleFullStats(False)
                event_dispatcher.showIngameMenu()
            return True
        if isDown and CommandMapping.g_instance.isFired(CommandMapping.CMD_UPGRADE_PANEL_SHOW, key):
            event_dispatcher.hideBattleVehicleConfigurator()
        if key in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
            if not self.__consumers:
                avatar_getter.setForcedGuiControlMode(isDown, enableAiming=False)
            return True
        if key == Keys.KEY_TAB and (mods != Keys.MODIFIER_CTRL or not isDown):
            if self.commendationsCtrl.isCommendationsEnabled and self.guiSessionProvider.shared.calloutCtrl.handleTabScreenKeyPress(key, isDown):
                return True
            if isEventBattle:
                event_dispatcher.toggleEventStats(isDown)
            else:
                event_dispatcher.hideBattleVehicleConfigurator()
                event_dispatcher.toggleFullStats(isDown)
            return True
        if key == Keys.KEY_TAB and mods == Keys.MODIFIER_CTRL and isDown:
            if not self.__consumers:
                event_dispatcher.setNextPlayerPanelMode()
            return True
        return False
