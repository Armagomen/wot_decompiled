# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_setups_ctrl.py
import logging
import typing
import BigWorld
from constants import ARENA_PERIOD, VEHICLE_SIEGE_STATE
from gui.battle_control.arena_info.interfaces import IPrebattleSetupsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.items_parameters.functions import getVehicleFactors
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.MethodsRules import MethodsRules
from gui.veh_post_progression.helpers import getVehicleState, getInstalledShells, updateInvInstalled
from gui.veh_post_progression.sounds import playSound, Sounds
from gui.veh_post_progression.battle_cooldown_manager import BattleCooldownManager
from helpers import dependency
from items import vehicles
from items.components.post_progression_components import getActiveModifications
from items.utils import getCircularVisionRadius, getFirstReloadTime
from PerksParametersController import PerksParametersController
from post_progression_common import EXT_DATA_PROGRESSION_KEY, EXT_DATA_SLOT_KEY, TANK_SETUP_GROUPS, TankSetupLayouts, TankSetups
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescr
_logger = logging.getLogger(__name__)
_SWITCH_SETUPS_ACTION = 0
_EXT_ENHANCEMENTS_KEY = 'extEnhancements'
_EXT_PROGRESSION_MODS = 'extActiveProgression'
_EXT_RESPAWN_BOOST = 'respawnReloadTimeFactor'
_EXT_SIEGE_STATE_KEY = 'extSiegeState'
_SETUP_NAME_TO_LAYOUT = {TankSetups.SHELLS: TankSetupLayouts.SHELLS,
 TankSetups.EQUIPMENT: TankSetupLayouts.EQUIPMENT,
 TankSetups.OPTIONAL_DEVICES: TankSetupLayouts.OPTIONAL_DEVICES,
 TankSetups.BATTLE_BOOSTERS: TankSetupLayouts.BATTLE_BOOSTERS}

class _States(CONST_CONTAINER):
    IDLE = 0
    VEHICLE_ID = 1
    CREW = 2
    DYN_SLOT = 4
    ENHANCEMENTS = 8
    PERKS = 16
    PROGRESSION = 32
    RESPAWN = 64
    SETUPS = 128
    SETUPS_INDEXES = 256
    INIT_COMPLETE = 512
    SELECTION_AVAILABLE = 1024
    SELECTION_STOPPED = 2048
    INIT_READY = VEHICLE_ID | CREW | DYN_SLOT | ENHANCEMENTS | PERKS | PROGRESSION | RESPAWN | SETUPS | SETUPS_INDEXES


class IPrebattleSetupsListener(object):

    def setSetupsVehicle(self, vehicle):
        pass

    def updateVehicleParams(self, vehicle, factors):
        pass

    def updateVehicleSetups(self, vehicle):
        pass

    def stopSetupsSelection(self):
        pass


class PrebattleSetupsController(MethodsRules, IPrebattleSetupsController):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__state', '__playerVehicleID', '__perksController', '__vehicle', '__invData', '__extData', '__hasValidCaps', '__cooldown')

    def __init__(self):
        super(PrebattleSetupsController, self).__init__()
        self.__state = _States.IDLE
        self.__invData = {}
        self.__extData = {}
        self.__playerVehicleID = None
        self.__perksController = None
        self.__vehicle = None
        self.__hasValidCaps = False
        self.__cooldown = BattleCooldownManager()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL

    def startControl(self, battleCtx, arenaVisitor):
        self.__hasValidCaps = arenaVisitor.bonus.hasSwitchSetups()
        self.__extData[_EXT_SIEGE_STATE_KEY] = VEHICLE_SIEGE_STATE.DISABLED

    def stopControl(self):
        self.clear(reset=True)
        self.__state = _States.IDLE
        self.__invData.clear()
        self.__extData.clear()
        self.__playerVehicleID = None
        self.__perksController = None
        self.__vehicle = None
        self.__hasValidCaps = False
        self.__cooldown.reset(_SWITCH_SETUPS_ACTION)
        return

    def isSelectionAvailable(self):
        return bool(self.__state & _States.SELECTION_AVAILABLE)

    @MethodsRules.delayable()
    def setPlayerVehicle(self, vehicleID, vehDescr):
        if self.__isSelectionStopped() or self.__state & _States.VEHICLE_ID:
            return
        self.__playerVehicleID = vehicleID
        self.__vehicle = Vehicle(strCompactDescr=vehDescr.makeCompactDescr())
        self.__onInitStepCompleted(_States.VEHICLE_ID)

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    @MethodsRules.delayable('setPlayerVehicle')
    def setCrew(self, vehicleID, crew):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.CREW:
            return
        self.__invData['battleCrewCDs'] = crew
        self.__onInitStepCompleted(_States.CREW)

    @MethodsRules.delayable('setPlayerVehicle')
    def setDynSlotType(self, vehicleID, dynSlotTypeID):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.DYN_SLOT:
            return
        self.__extData[EXT_DATA_SLOT_KEY] = dynSlotTypeID
        self.__onInitStepCompleted(_States.DYN_SLOT)

    @MethodsRules.delayable('setPlayerVehicle')
    def setEnhancements(self, vehicleID, enhancements):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.ENHANCEMENTS:
            return
        self.__extData[_EXT_ENHANCEMENTS_KEY] = enhancements
        self.__onInitStepCompleted(_States.ENHANCEMENTS)

    @MethodsRules.delayable('setPlayerVehicle')
    def setPerks(self, vehicleID, perks):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.PERKS:
            return
        self.__perksController = PerksParametersController(self.__vehicle.compactDescr, perks)
        self.__onInitStepCompleted(_States.PERKS)

    @MethodsRules.delayable('setPlayerVehicle')
    def setPostProgression(self, vehicleID, itemCDs):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.PROGRESSION:
            return
        self.__extData[_EXT_PROGRESSION_MODS] = getActiveModifications(itemCDs, vehicles.g_cache.postProgression())
        self.__extData[EXT_DATA_PROGRESSION_KEY] = getVehicleState(itemCDs)
        self.__onInitStepCompleted(_States.PROGRESSION)

    @MethodsRules.delayable('setPlayerVehicle')
    def setRespawnReloadFactor(self, vehicleID, reloadFactor):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.RESPAWN:
            return
        self.__extData[_EXT_RESPAWN_BOOST] = reloadFactor
        self.__onInitStepCompleted(_States.RESPAWN)

    @MethodsRules.delayable('setPlayerVehicle')
    def setSetups(self, vehicleID, setups):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.SETUPS:
            return
        self.__invData.update({_SETUP_NAME_TO_LAYOUT[key]:value for key, value in setups.iteritems()})
        self.__onInitStepCompleted(_States.SETUPS)

    @MethodsRules.delayable('setPlayerVehicle')
    def setSetupsIndexes(self, vehicleID, setupsIndexes):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped():
            return
        self.__invData['layoutIndexes'] = setupsIndexes
        updateInvInstalled(self.__invData, setupsIndexes)
        if self.__state & _States.SETUPS_INDEXES:
            self.__updateSetupIndexes()
            return
        self.__onInitStepCompleted(_States.SETUPS_INDEXES)

    @MethodsRules.delayable('setPlayerVehicle')
    def setSiegeState(self, vehicleID, siegeState):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped():
            return
        self.__extData[_EXT_SIEGE_STATE_KEY] = siegeState
        if self.__state & _States.SELECTION_AVAILABLE:
            self.__updateSiegeState()

    def setViewComponents(self, *components):
        super(PrebattleSetupsController, self).setViewComponents(*components)
        if self.isSelectionAvailable():
            for component in components:
                component.setSetupsVehicle(self.__vehicle)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        if not self.__isSelectionStopped():
            self.__updatePeriod(period)

    def switchLayout(self, groupID, layoutIdx):
        if self.__sessionProvider.isReplayPlaying:
            return
        elif not self.isSelectionAvailable():
            return
        elif self.__cooldown.isInProcess(_SWITCH_SETUPS_ACTION):
            return
        elif not self.__vehicle.isSetupSwitchActive(groupID):
            return
        else:
            playerVehicle = BigWorld.entities.get(self.__playerVehicleID)
            if playerVehicle is None:
                return
            self.__cooldown.process(_SWITCH_SETUPS_ACTION)
            playerVehicle.cell.switchSetup(groupID, layoutIdx)
            playSound(Sounds.GAMEPLAY_SETUP_SWITCH)
            return

    def __isSelectionAvailable(self):
        if not self.__hasValidCaps:
            return False
        for groupID in TANK_SETUP_GROUPS.iterkeys():
            if self.__vehicle.isSetupSwitchActive(groupID):
                return True

        return False

    def __isSelectionStopped(self):
        return bool(self.__state & _States.SELECTION_STOPPED)

    def __onInitStepCompleted(self, stepState):
        if self.__state & _States.INIT_COMPLETE:
            return
        self.__updateState(stepState)
        if self.__state & _States.INIT_READY == _States.INIT_READY:
            shellsCDs = [ shell.intCD for shell in self.__vehicle.gun.defaultAmmo ]
            shellsLayoutKey = (self.__vehicle.turret.intCD, self.__vehicle.gun.intCD)
            self.__invData['shells'] = getInstalledShells(shellsCDs, self.__invData[TankSetupLayouts.SHELLS])
            self.__invData[TankSetupLayouts.SHELLS] = {shellsLayoutKey: self.__invData[TankSetupLayouts.SHELLS]}
            self.__updateGuiVehicle()
            self.__updateState(_States.INIT_COMPLETE)
        if self.__state & _States.INIT_COMPLETE and self.__isSelectionAvailable():
            self.__updateState(_States.SELECTION_AVAILABLE)

    def __updateAmmoCtrl(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        currentShellCD, nextShellCD = ammoCtrl.getCurrentShellCD(), ammoCtrl.getNextShellCD()
        ammoCtrl.clear(leave=False)
        ammoCtrl.setGunSettings(self.__vehicle.descriptor.gun)
        for shell in self.__vehicle.shells.installed.getItems():
            ammoCtrl.setShells(shell.intCD, shell.count, 0)

        ammoCtrl.resetShellsSettings(currentShellCD, nextShellCD)

    def __updateAmmoCtrlParams(self, factors):
        ammoCtrl = self.__sessionProvider.shared.ammo
        hasAmmo = any((shell.count for shell in self.__vehicle.shells.installed.getItems()))
        reloadTime = getFirstReloadTime(self.__vehicle.descriptor, factors) if hasAmmo else 0.0
        ammoCtrl.setGunReloadTime(-1, reloadTime, skipAutoLoader=True)

    def __updateFeedbackParams(self, factors):
        feedbackCtrl = self.__sessionProvider.shared.feedback
        newAttrs = feedbackCtrl.getVehicleAttrs()
        newAttrs['circularVisionRadius'] = getCircularVisionRadius(self.__vehicle.descriptor, factors)
        feedbackCtrl.setVehicleAttrs(self.__playerVehicleID, newAttrs)

    def __updateGuiVehicle(self):
        invData, extData = self.__invData.copy(), self.__extData.copy()
        vehicle = self.__vehicle = Vehicle(strCompactDescr=self.__vehicle.strCD, extData=extData, invData=invData)
        vehicle.installPostProgressionItem(self.__itemsFactory.createVehPostProgression(vehicle.compactDescr, self.__extData[EXT_DATA_PROGRESSION_KEY], vehicle.typeDescr))
        vehicle.setPerksController(self.__perksController)
        vehicle.descriptor.onSiegeStateChanged(self.__extData[_EXT_SIEGE_STATE_KEY])
        vehicle.descriptor.installModifications(self.__extData[_EXT_PROGRESSION_MODS], rebuildAttrs=False)
        vehicle.descriptor.installEnhancements(self.__extData[_EXT_ENHANCEMENTS_KEY], rebuildAttrs=False)
        vehicle.descriptor.installOptDevsSequence(vehicle.optDevices.installed.getIntCDs())
        newFactors = getVehicleFactors(vehicle)
        newFactors[_EXT_RESPAWN_BOOST] = self.__extData[_EXT_RESPAWN_BOOST]
        return newFactors

    def __updatePeriod(self, period):
        if period >= ARENA_PERIOD.BATTLE:
            self.__updateState(_States.SELECTION_STOPPED)

    def __updateState(self, addMask):
        if addMask == _States.SELECTION_AVAILABLE:
            for component in self._viewComponents:
                component.setSetupsVehicle(self.__vehicle)

        if addMask == _States.SELECTION_STOPPED and self.isSelectionAvailable():
            self.__state &= ~_States.SELECTION_AVAILABLE
            self.__vehicle.stopPerksController()
            for component in self._viewComponents:
                component.stopSetupsSelection()

        self.__state |= addMask
        _logger.debug('[PrebattleSetupsController] addMask %s modifiedState %s', addMask, self.__state)

    def __updateSetupIndexes(self):
        newFactors = self.__updateGuiVehicle()
        self.__updateAmmoCtrl()
        self.__updateAmmoCtrlParams(newFactors)
        self.__updateFeedbackParams(newFactors)
        for component in self._viewComponents:
            component.updateVehicleParams(self.__vehicle, newFactors)

        for component in self._viewComponents:
            component.updateVehicleSetups(self.__vehicle)

        if self.__sessionProvider.isReplayPlaying:
            playSound(Sounds.GAMEPLAY_SETUP_SWITCH)

    def __updateSiegeState(self):
        newFactors = self.__updateGuiVehicle()
        self.__updateAmmoCtrlParams(newFactors)
        self.__updateFeedbackParams(newFactors)
        for component in self._viewComponents:
            component.updateVehicleParams(self.__vehicle, newFactors)
