# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/consumables_panel.py
import logging
import math
import weakref
from functools import partial
import BigWorld
from typing import TYPE_CHECKING
import CommandMapping
from constants import EQUIPMENT_STAGES, SHELL_TYPES, DAMAGE_INTERPOLATION_DIST_FIRST, DAMAGE_INTERPOLATION_DIST_LAST
from gui import GUI_SETTINGS
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
from gui.Scaleform.daapi.view.meta.ConsumablesPanelMeta import ConsumablesPanelMeta
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_control.battle_constants import VEHICLE_DEVICE_IN_COMPLEX_ITEM, CROSSHAIR_VIEW_ID, VEHICLE_VIEW_STATE, DEVICE_STATE_DESTROYED, FEEDBACK_EVENT_ID
from gui.battle_control.controllers.consumables.ammo_ctrl import IAmmoListener
from gui.battle_control.controllers.consumables.equipment_ctrl import IgnoreEntitySelection
from gui.battle_control.controllers.consumables.equipment_ctrl import NeedEntitySelection
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import NO_DATA
from gui.shared.items_parameters.params import ShellParams
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
from items.artefacts import SharedCooldownConsumableConfigReader
from shared_utils import forEach
from items.utils import getVehicleShotSpeedByFactors
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
if TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import _OrderItem, _EquipmentItem
_logger = logging.getLogger(__name__)
ASTERISK = '*'
R_AMMO_ICON = R.images.gui.maps.icons.ammopanel.battle_ammo
NO_AMMO_ICON = 'NO_{}'
COMMAND_AMMO_CHOICE_MASK = 'CMD_AMMO_CHOICE_{0:d}'
PERMANENT_GLOW_TAG = 'permanentGlow'
HAS_NO_BACK_TAG = 'hasNoBack'
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
TOOLTIP_NO_BODY_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}'
EMPTY_EQUIPMENT_TOOLTIP = backport.text(R.strings.ingame_gui.consumables_panel.equipment.tooltip.empty())

def _isEquipmentAvailableToUse(eq):
    return eq.isAvailableToUse


class _PythonReloadTicker(PythonTimer):

    def __init__(self, viewObject):
        super(_PythonReloadTicker, self).__init__(viewObject, 0, 0, 0, 0, interval=0.1)
        self.__index = 0

    def _hideView(self):
        pass

    def _showView(self, isBubble):
        pass

    def startAnimation(self, index, actualTime, baseTime):
        self.__index = index
        self._stopTick()
        if actualTime > 0:
            self._totalTime = baseTime
            self._finishTime = BigWorld.serverTime() + actualTime
            self.show()

    def _setViewSnapshot(self, timeLeft):
        if self._totalTime > 0:
            timeGone = self._totalTime - timeLeft
            progressInPercents = float(timeGone) / self._totalTime * 100
            self._viewObject.as_setCoolDownPosAsPercentS(self.__index, progressInPercents)

    def _stopTick(self):
        super(_PythonReloadTicker, self)._stopTick()
        self._viewObject.as_setCoolDownPosAsPercentS(self.__index, 100.0)


class ConsumablesPanel(IAmmoListener, ConsumablesPanelMeta, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _PANEL_MAX_LENGTH = 12
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 2
    _EQUIPMENT_START_IDX = 3
    _EQUIPMENT_END_IDX = 5
    _ORDERS_START_IDX = 6
    _ORDERS_END_IDX = 8
    _OPT_DEVICE_START_IDX = 9
    _OPT_DEVICE_END_IDX = 11
    _EQUIPMENT_GLOW_TIME = 7
    _R_ARTEFACT_ICON = R.images.gui.maps.icons.artefact

    def __init__(self):
        super(ConsumablesPanel, self).__init__()
        self.__ammoRange = range(self._AMMO_START_IDX, self._AMMO_END_IDX + 1)
        self.__ammoFullMask = sum([ 1 << idx for idx in self.__ammoRange ])
        self.__equipmentRange = range(self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX + 1)
        self.__equipmentFullMask = sum([ 1 << idx for idx in self.__equipmentRange ])
        self.__ordersRange = range(self._ORDERS_START_IDX, self._ORDERS_END_IDX + 1)
        self.__ordersFullMask = sum([ 1 << idx for idx in self.__ordersRange ])
        self.__optDeviceRange = range(self._OPT_DEVICE_START_IDX, self._OPT_DEVICE_END_IDX + 1)
        self.__optDeviceFullMask = sum([ 1 << idx for idx in self.__optDeviceRange ])
        self._emptyEquipmentsSlice = [0] * (self._EQUIPMENT_END_IDX - self._EQUIPMENT_START_IDX + 1)
        self._cds = [None] * self._PANEL_MAX_LENGTH
        self._mask = 0
        self._keys = {}
        self._extraKeys = {}
        self.__currentActivatedSlotIdx = -1
        self._equipmentsGlowCallbacks = {}
        if self.sessionProvider.isReplayPlaying:
            self.__reloadTicker = _PythonReloadTicker(weakref.proxy(self))
        else:
            self.__reloadTicker = None
        self.delayedReload = None
        self.__delayedNextShellID = None
        self.__isViewActive = False
        self.ammoReloadingStatus = {}
        return

    @property
    def isActive(self):
        return self.__isViewActive

    def onClickedToSlot(self, bwKey, idx):
        self.__handleBWKey(int(bwKey), idx)

    def onPanelShown(self):
        self.__isViewActive = True

    def onPanelHidden(self):
        self.__isViewActive = False

    def _populate(self):
        self.as_setPanelSettingsS(self._getPanelSettings())
        super(ConsumablesPanel, self)._populate()
        if self.sessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()
        if BigWorld.player().isObserver():
            self.as_handleAsObserverS()
        self._addListeners()

    def _dispose(self):
        self._clearAllEquipmentGlow()
        self._removeListeners()
        self._keys.clear()
        self._extraKeys.clear()
        if self.sessionProvider.isReplayPlaying:
            self.__reloadTicker.clear()
        super(ConsumablesPanel, self)._dispose()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.DEFAULT_SETTINGS_ID

    def _resetDelayedReload(self):
        self.delayedReload = None
        self.__delayedNextShellID = None
        return

    def _resetCds(self):
        self._cds = [None] * self._PANEL_MAX_LENGTH
        return

    def _reset(self):
        self._resetCds()
        self._mask = 0
        self._keys.clear()
        self._extraKeys.clear()
        self.__currentActivatedSlotIdx = -1
        self._resetDelayedReload()
        self.as_resetS()

    def _resetAmmo(self):
        self.__resetStorages(self.__ammoRange, self.__ammoFullMask, True)
        self.__currentActivatedSlotIdx = -1
        self._resetDelayedReload()

    def _resetEquipments(self):
        self._clearAllEquipmentGlow()
        self.__resetStorages(self.__equipmentRange, self.__equipmentFullMask, True)
        self.__resetStorages(self.__ordersRange, self.__ordersFullMask, True)
        self.__currentActivatedSlotIdx = -1

    def _isEquipmentSlot(self, slotIdx):
        return slotIdx in self.__equipmentRange

    def _resetOptDevices(self):
        self.__resetStorages(self.__optDeviceRange, self.__optDeviceFullMask)

    def __resetStorages(self, storageRange, storageMask, clearKeys=False):
        for idx in storageRange:
            self._cds[idx] = None
            if clearKeys:
                if idx in self._extraKeys:
                    del self._extraKeys[idx]
                keyCode, _ = self._genKey(idx)
                if keyCode in self._keys:
                    del self._keys[keyCode]

        self._mask &= ~storageMask
        self.as_resetS(storageRange)
        return

    def _addShellSlot(self, idx, intCD, descriptor, quantity, gunSettings, isInfinite):
        self._cds[idx] = intCD
        bwKey, sfKeyCode = self._genKey(idx)
        self._extraKeys[idx] = self._keys[bwKey] = partial(self.__handleAmmoPressed, intCD)
        tooltipText = self.__makeShellTooltip(descriptor, int(round(gunSettings.getPiercingPower(intCD))), gunSettings.getShotSpeed(intCD))
        icon = descriptor.icon[0]
        iconName = icon.split('.png')[0]
        shellIconPath = backport.image(R_AMMO_ICON.dyn(iconName)())
        noShellIconPath = backport.image(R_AMMO_ICON.dyn(NO_AMMO_ICON.format(iconName))())
        self.as_addShellSlotS(idx, bwKey, sfKeyCode, quantity, gunSettings.clip.size, shellIconPath, noShellIconPath, tooltipText, isInfinite)

    def _updateEquipmentSlotTooltipText(self, idx, item):
        toolTip = self._buildEquipmentSlotTooltipText(item)
        self.as_updateTooltipS(idx=idx, tooltipStr=toolTip)

    def _buildEquipmentSlotTooltipText(self, item):
        descriptor = item.getDescriptor()
        reloadingTime = item.getTotalTime()
        isSharedCooldownConfig = isinstance(descriptor, SharedCooldownConsumableConfigReader)
        body = descriptor.description
        consumeAmmo = descriptor.consumeAmmo if isSharedCooldownConfig else False
        if not consumeAmmo and reloadingTime > 0:
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            if isSharedCooldownConfig:
                cdSecVal = descriptor.cooldownTime
            else:
                cdSecVal = item.getTotalTime()
            paramsString = backport.text(tooltipStr, cooldownSeconds=str(int(cdSecVal)))
            body = '\n\n'.join((body, paramsString))
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
        return toolTip

    def _getToolTipEquipmentSlot(self, item):
        return self._buildEquipmentSlotTooltipText(item)

    def _addEquipmentSlot(self, idx, intCD, item):
        self._cds[idx] = intCD
        if item is None:
            bwKey, sfKey = self._genKey(idx)
            self.as_addEquipmentSlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=0, timeRemaining=0, reloadingTime=0, iconPath='', tooltipText=EMPTY_EQUIPMENT_TOOLTIP, animation=ANIMATION_TYPES.NONE)
            snap = self._cds[self._EQUIPMENT_START_IDX:self._EQUIPMENT_END_IDX + 1]
            if snap == self._emptyEquipmentsSlice:
                self.as_showEquipmentSlotsS(False)
        else:
            bwKey, sfKey = self._generateEquipmentKey(idx, item)
            if bwKey is not None:
                handler = self._getEquipmentKeyHandler(intCD, idx)
                if item.getQuantity() > 0:
                    self._extraKeys[idx] = self._keys[bwKey] = handler
            descriptor = item.getDescriptor()
            quantity = item.getQuantity()
            timeRemaining = item.getTimeRemaining()
            reloadingTime = item.getTotalTime()
            iconPath = self._getEquipmentIcon(idx, item, descriptor.icon[0])
            animationType = item.getAnimationType()
            self.as_addEquipmentSlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=quantity, timeRemaining=timeRemaining, reloadingTime=reloadingTime, iconPath=iconPath, tooltipText=self._getToolTipEquipmentSlot(item), animation=animationType)
        return

    def _addOptionalDeviceSlot(self, idx, optDeviceInBattle):
        self._cds[idx] = optDeviceInBattle.getIntCD()
        descriptor = optDeviceInBattle.getDescriptor()
        iconPath = self._getOptionalDeviceIcon(descriptor.icon[0])
        self.as_addOptionalDeviceSlotS(idx, -1 if optDeviceInBattle.getStatus() else 0, iconPath, TOOLTIPS_CONSTANTS.BATTLE_OPT_DEVICE, True, optDeviceInBattle.getIntCD(), optDeviceInBattle.isUsed())

    def _getOptionalDeviceIcon(self, icon):
        return backport.image(self._R_ARTEFACT_ICON.dyn(icon)())

    def _getEquipmentIcon(self, idx, item, icon):
        return backport.image(self._getEquipmentIconPath(item).dyn(icon)())

    def _isIdxInKeysRange(self, idx):
        return idx in self.__equipmentRange or idx in self.__ordersRange

    def _updateShellSlot(self, idx, quantity):
        self.as_setItemQuantityInSlotS(idx, quantity)

    def _updateEquipmentSlot(self, idx, item):
        quantity = item.getQuantity()
        currentTime = item.getTimeRemaining()
        maxTime = item.getTotalTime()
        self.as_setItemTimeQuantityInSlotS(idx, quantity, currentTime, maxTime, item.getAnimationType())
        bwKey, _ = self._genKey(idx)
        self._setEquipmentKeyHandler(item, bwKey, idx)
        self._updateEquipmentGlow(idx, item)
        self._updateActivatedSlot(idx, item)
        self._updateEquipmentSlotTooltipText(idx, item)

    def _updateEquipmentGlow(self, idx, item):
        if item.isReusable or item.isAvatar():
            isPermanentGlow = PERMANENT_GLOW_TAG in item.getTags()
            if item.getStage() != EQUIPMENT_STAGES.PREPARING:
                if self._canApplyingGlowEquipment(item):
                    self._showEquipmentGlow(idx)
                elif item.wasPreparationCanceled and isPermanentGlow:
                    glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_ESPECIAL_NO_ANIM
                    self._showEquipmentGlow(idx, glowType, isPermanentGlow)
                elif item.becomeReady or isPermanentGlow and item.alreadyReady:
                    glowType = self._getActiveItemGlowType(item)
                    self._showEquipmentGlow(idx, glowType, isPermanentGlow)
                elif isPermanentGlow and item.getStage() == EQUIPMENT_STAGES.ACTIVE:
                    self._showEquipmentGlow(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_USAGE, isPermanentGlow)
                elif isPermanentGlow and item.isInCooldown():
                    self.as_hideGlowS(idx)
                elif idx in self._equipmentsGlowCallbacks:
                    self.__clearEquipmentGlow(idx)
            elif isPermanentGlow:
                self.as_hideGlowS(idx)

    @staticmethod
    def _getActiveItemGlowType(item):
        isPermanentGlow = PERMANENT_GLOW_TAG in item.getTags()
        if item.isAvatar():
            if isPermanentGlow:
                glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_ESPECIAL
            else:
                glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL
        else:
            glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN
        return glowType

    def _updateActivatedSlot(self, idx, item):
        hasNoBack = HAS_NO_BACK_TAG in item.getTags()
        if item.getStage() == EQUIPMENT_STAGES.PREPARING:
            self.__currentActivatedSlotIdx = idx
            self.as_setEquipmentActivatedS(idx, True, isNoBack=hasNoBack)
        elif item.getStage() != EQUIPMENT_STAGES.PREPARING and self.__currentActivatedSlotIdx == idx:
            self.__currentActivatedSlotIdx = -1
        elif item.getStage() != EQUIPMENT_STAGES.PREPARING:
            self.as_setEquipmentActivatedS(idx, False, isNoBack=hasNoBack)

    def _setEquipmentKeyHandler(self, item, bwKey, idx):
        if item.getQuantity() > 0 and bwKey not in self._keys:
            handler = partial(self._handleEquipmentPressed, self._cds[idx])
            self._keys[bwKey] = handler

    def _updateOptionalDeviceSlot(self, idx, optDeviceInBattle):
        intCD = optDeviceInBattle.getIntCD()
        duration = -1 if optDeviceInBattle.getStatus() else 0
        idx = self._cds.index(intCD)
        self.as_setOptionalDeviceUsedS(idx, optDeviceInBattle.isUsed())
        if optDeviceInBattle.isNeedGlow():
            self.as_setGlowS(idx, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        self.as_setCoolDownTimeS(self._cds.index(intCD), duration, duration, 0)

    def _resetEquipmentSlot(self, idx, intCD, item):
        self._cds[idx] = intCD
        bwKey, _ = self._genKey(idx)
        if bwKey in self._keys:
            self._keys.pop(bwKey)
        self._updateEquipmentSlot(idx, item)

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE, isPermanentGlow=False):
        if BigWorld.player().isObserver():
            return
        if equipmentIndex in self._equipmentsGlowCallbacks:
            BigWorld.cancelCallback(self._equipmentsGlowCallbacks[equipmentIndex])
            del self._equipmentsGlowCallbacks[equipmentIndex]
        else:
            self.as_setGlowS(equipmentIndex, glowID=glowType)
        if not isPermanentGlow:
            self._equipmentsGlowCallbacks[equipmentIndex] = BigWorld.callback(self._EQUIPMENT_GLOW_TIME, partial(self._hideEquipmentGlowCallback, equipmentIndex))

    def _onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings, isInfinite):
        idx = self.__genNextIdx(self.__ammoFullMask, self._AMMO_START_IDX)
        self._addShellSlot(idx, intCD, descriptor, quantity, gunSettings, isInfinite)

    def _onShellsUpdated(self, intCD, quantity, *args):
        if intCD in self._cds:
            self._updateShellSlot(self._cds.index(intCD), quantity)
        else:
            _logger.error('Ammo with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onNextShellChanged(self, intCD):
        if intCD in self._cds:
            self.__delayedNextShellID = intCD
            self.as_setNextShellS(self._cds.index(intCD))
        else:
            _logger.error('Ammo with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onCurrentShellChanged(self, intCD):
        if intCD in self._cds:
            self.as_setCurrentShellS(self._cds.index(intCD))
        else:
            _logger.error('Ammo with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onGunSettingsSet(self, _):
        self._resetAmmo()

    def __onShellsCleared(self, _):
        self._resetAmmo()

    def _onEquipmentsCleared(self):
        self._resetEquipments()

    def __onOptionalDevicesCleared(self):
        self._resetOptDevices()

    def _onGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        if currShellCD not in self._cds:
            _logger.error('Ammo with cd=%d is not found in panel %s', currShellCD, str(self._cds))
            return
        shellIndex = self._cds.index(currShellCD)
        if self.delayedReload > 0:
            self.delayCallback(self.delayedReload, self.__startReloadDelayed, shellIndex, state)
            self.as_setCoolDownPosAsPercentS(shellIndex, 0)
        else:
            self.__startReload(shellIndex, state)

    def _onEquipmentAdded(self, intCD, item):
        if item is None:
            idx = self.__genNextIdx(self.__equipmentFullMask + self.__ordersFullMask, self._EQUIPMENT_START_IDX)
        elif self._isAvatarEquipment(item):
            idx = self.__genNextIdx(self.__ordersFullMask, self._ORDERS_START_IDX)
        else:
            idx = self.__genNextIdx(self.__equipmentFullMask, self._EQUIPMENT_START_IDX)
        self._addEquipmentSlot(idx, intCD, item)
        return

    def _onEquipmentUpdated(self, intCD, item):
        if item.index > 0:
            self._updateEquipmentSlot(item.index + self._ORDERS_START_IDX - 1, item)
        elif intCD in self._cds:
            self._updateEquipmentSlot(self._cds.index(intCD), item)
        else:
            _logger.error('Equipment with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onEquipmentCooldownInPercent(self, key, percent):
        index = self._getEquipmentIdxByKey(key)
        if index is None:
            _logger.error('Equipment with cd, idx is not found in panel, %s', str(key))
        self.as_setCoolDownPosAsPercentS(index, percent)
        return

    def _onEquipmentCooldownTime(self, key, timeLeft, isBaseTime, isFlash):
        index = self._getEquipmentIdxByKey(key)
        if index is None:
            _logger.error('Equipment with cd, idx is not found in panel, %s', str(key))
        self.as_setCoolDownTimeSnapshotS(index, timeLeft, isBaseTime, isFlash)
        return

    def _onEquipmentReset(self, oldIntCD, intCD, item):
        self._resetEquipmentSlot(self._cds.index(oldIntCD), intCD, item)

    def _isAvatarEquipment(self, item):
        return item.isAvatar()

    def _getEquipmentIconPath(self, *_):
        return self._R_ARTEFACT_ICON

    def __onVehicleFeedbackReceived(self, eventID, _, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_ATTRS_CHANGED:
            for payload in self.sessionProvider.shared.ammo.getOrderedShellsLayout():
                intCD, descriptor, _, _, gunSettings = payload[:5]
                self.as_updateTooltipS(idx=self._cds.index(intCD), tooltipStr=self.__makeShellTooltip(descriptor, int(round(gunSettings.getPiercingPower(intCD))), gunSettings.getShotSpeed(intCD)))

    def _addListeners(self):
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self._onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self._onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            self.__fillShells(ammoCtrl)
            ammoCtrl.onShellsAdded += self._onShellsAdded
            ammoCtrl.onShellsUpdated += self._onShellsUpdated
            ammoCtrl.onNextShellChanged += self._onNextShellChanged
            ammoCtrl.onCurrentShellChanged += self._onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet += self._onGunReloadTimeSet
            ammoCtrl.onGunSettingsSet += self._onGunSettingsSet
            ammoCtrl.onDebuffStarted += self.__onDebuffStarted
            ammoCtrl.onShellsCleared += self.__onShellsCleared
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            self.__fillEquipments(eqCtrl)
            eqCtrl.onEquipmentAdded += self._onEquipmentAdded
            eqCtrl.onEquipmentReset += self._onEquipmentReset
            eqCtrl.onEquipmentUpdated += self._onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent += self._onEquipmentCooldownInPercent
            eqCtrl.onEquipmentCooldownTime += self._onEquipmentCooldownTime
            eqCtrl.onEquipmentsCleared += self._onEquipmentsCleared
        optDevicesCtrl = self.sessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            self.__fillOptionalDevices(optDevicesCtrl)
            optDevicesCtrl.onOptionalDeviceAdded += self.__onOptionalDeviceAdded
            optDevicesCtrl.onOptionalDeviceUpdated += self.__onOptionalDeviceUpdated
            optDevicesCtrl.onOptionalDevicesCleared += self.__onOptionalDevicesCleared
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            currentSpgShotsState = self.sessionProvider.shared.crosshair.getSPGShotsIndicatorState()
            if vehicleCtrl is not None and ammoCtrl is not None and currentSpgShotsState:
                self.__onSPGShotsIndicatorStateChanged(currentSpgShotsState)
            crosshairCtrl.onSPGShotsIndicatorStateChanged += self.__onSPGShotsIndicatorStateChanged
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        CommandMapping.g_instance.onMappingChanged += self._onMappingChanged
        g_eventBus.addListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def _onSlotWaited(self, index, quantity):
        pass

    def _onSlotBlocked(self, index, quantity):
        pass

    def _removeListeners(self):
        g_eventBus.removeListener(GameEvent.CHOICE_CONSUMABLE, self.__handleConsumableChoice, scope=EVENT_BUS_SCOPE.BATTLE)
        CommandMapping.g_instance.onMappingChanged -= self._onMappingChanged
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onSPGShotsIndicatorStateChanged -= self.__onSPGShotsIndicatorStateChanged
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self._onRespawnBaseMoving
            vehicleCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self._onShellsAdded
            ammoCtrl.onShellsUpdated -= self._onShellsUpdated
            ammoCtrl.onNextShellChanged -= self._onNextShellChanged
            ammoCtrl.onCurrentShellChanged -= self._onCurrentShellChanged
            ammoCtrl.onGunReloadTimeSet -= self._onGunReloadTimeSet
            ammoCtrl.onGunSettingsSet -= self._onGunSettingsSet
            ammoCtrl.onDebuffStarted -= self.__onDebuffStarted
            ammoCtrl.onShellsCleared -= self.__onShellsCleared
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentAdded -= self._onEquipmentAdded
            eqCtrl.onEquipmentReset -= self._onEquipmentReset
            eqCtrl.onEquipmentUpdated -= self._onEquipmentUpdated
            eqCtrl.onEquipmentCooldownInPercent -= self._onEquipmentCooldownInPercent
            eqCtrl.onEquipmentCooldownTime -= self._onEquipmentCooldownTime
            eqCtrl.onEquipmentsCleared -= self._onEquipmentsCleared
        optDevicesCtrl = self.sessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            optDevicesCtrl.onOptionalDeviceAdded -= self.__onOptionalDeviceAdded
            optDevicesCtrl.onOptionalDeviceUpdated -= self.__onOptionalDeviceUpdated
            optDevicesCtrl.onOptionalDevicesCleared -= self.__onOptionalDevicesCleared
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl is not None:
            feedbackCtrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        return

    def __genNextIdx(self, full, start):
        bits = self._mask & full
        if not bits:
            idx = start
        else:
            idx = int(math.log(bits, 2)) + 1
        self._mask |= 1 << idx
        return idx

    def _generateEquipmentKey(self, idx, item):
        return self._genKey(idx) if item.getTags() else (None, None)

    def _genKey(self, idx):
        cmdMappingKey = COMMAND_AMMO_CHOICE_MASK.format(idx + 1 if idx < 9 else 0)
        bwKey = CommandMapping.g_instance.get(cmdMappingKey)
        sfKey = 0
        if bwKey is not None:
            sfKey = getScaleformKey(bwKey)
        return (bwKey, sfKey)

    def __makeShellTooltip(self, descriptor, piercingPower, shotSpeed):
        kind = descriptor.kind
        projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
        vehAttrs = self.sessionProvider.shared.feedback.getVehicleAttrs()
        shotSpeed, _ = getVehicleShotSpeedByFactors(vehAttrs, shotSpeed)
        header = backport.text(R.strings.item_types.shell.kinds.dyn(kind)())
        if GUI_SETTINGS.technicalInfo:
            vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
            vehicleDescriptor = vehicle.typeDescriptor if vehicle else None
            shellParams = ShellParams(descriptor, vehicleDescriptor)
            piercingPowerTable = shellParams.piercingPowerTable
            isDistanceDependent = piercingPowerTable is not None
            params = []
            damageValue = backport.getNiceNumberFormat(shellParams.avgDamage)
            showDistanceAsterisk = False
            note = ''
            footNotes = []
            if descriptor.isDamageMutable:
                damageValue = '%s-%s' % (backport.getNiceNumberFormat(shellParams.avgMutableDamage[0]), backport.getNiceNumberFormat(shellParams.avgMutableDamage[1]))
                showDistanceAsterisk = True
                note = ASTERISK
                footNotes.append(ASTERISK + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=int(DAMAGE_INTERPOLATION_DIST_FIRST), maxDist=int(min(vehicleDescriptor.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST))))
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=damageValue) + note)
            if vehicleDescriptor is not None and vehicleDescriptor.isAutoShootGunVehicle:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.damagePerSecond(), value=backport.getIntegralFormat(int(round(descriptor.armorDamage[0] / vehicle.typeDescriptor.gun.clip[1])))))
            if piercingPower != 0:
                value = backport.getNiceNumberFormat(piercingPower)
                if piercingPowerTable != NO_DATA and isDistanceDependent:
                    note = ASTERISK
                    value = '%s-%s' % (backport.getNiceNumberFormat(piercingPowerTable[0][1]), backport.getNiceNumberFormat(piercingPowerTable[-1][1]))
                    if not showDistanceAsterisk:
                        footNotes.append(note + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=backport.getNiceNumberFormat(piercingPowerTable[0][0]), maxDist=backport.getNiceNumberFormat(piercingPowerTable[-1][0])))
                else:
                    note = ASTERISK if not showDistanceAsterisk else ASTERISK * 2
                    footNotes.append(note + backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnote()))
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=value) + note)
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(int(round(shotSpeed / projSpeedFactor)))))
            if kind == SHELL_TYPES.HIGH_EXPLOSIVE and descriptor.type.explosionRadius > 0.0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=backport.getNiceNumberFormat(descriptor.type.explosionRadius)))
            if descriptor.hasStun and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stun = descriptor.stun
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.stunDuration(), minValue=backport.getNiceNumberFormat(stun.guaranteedStunDuration * stun.stunDuration), maxValue=backport.getNiceNumberFormat(stun.stunDuration)))
            for footNote in footNotes:
                params.append('\n' + footNote)

            body = text_styles.concatStylesToMultiLine(*params)
            fmt = TOOLTIP_FORMAT
        else:
            body = ''
            fmt = TOOLTIP_NO_BODY_FORMAT
        return fmt.format(header, body)

    def _getEquipmentKeyHandler(self, intCD, idx):
        return partial(self._handleEquipmentPressed, intCD)

    def __getKeysGenerator(self):
        hasEquipment = self.sessionProvider.shared.equipments.hasEquipment
        getEquipment = self.sessionProvider.shared.equipments.getEquipment
        for idx, intCD in enumerate(self._cds):
            if not intCD:
                yield (idx,
                 None,
                 None,
                 None)
            bwKey, sfKey = self._genKey(idx)
            handler = None
            if idx in self.__ammoRange:
                handler = partial(self.__handleAmmoPressed, intCD)
            elif self._isIdxInKeysRange(idx) and hasEquipment(intCD):
                item = getEquipment(intCD)
                if item is not None and item.getTags():
                    handler = self._getEquipmentKeyHandler(intCD, idx)
            yield (idx,
             bwKey,
             sfKey,
             handler)

        return

    def _onMappingChanged(self, *args):
        keys = {}
        extraKeys = {}
        slots = []
        for idx, bwKey, sfKey, handler in self.__getKeysGenerator():
            if handler:
                keys[bwKey] = handler
                extraKeys[idx] = handler
                slots.append((idx, bwKey, sfKey))

        self.as_setKeysToSlotsS(slots)
        self._keys.clear()
        self._keys = keys
        self._extraKeys.clear()
        self._extraKeys = extraKeys

    def __handleConsumableChoice(self, event):
        self.__handleBWKey(event.ctx['key'])

    def handleAmmoKey(self, key):
        self.__handleBWKey(key)

    def __handleBWKey(self, bwKey, idx=None):
        if bwKey == 0 and idx is not None:
            handler = self._extraKeys.get(idx)
        else:
            handler = self._keys.get(bwKey)
        if handler and callable(handler):
            handler()
        return

    def __handleAmmoPressed(self, intCD):
        ctrl = self.sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.changeSetting(intCD)
        return

    def _handleEquipmentPressed(self, intCD, entityName=None, idx=None):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        elif not self.as_isVisibleS():
            return
        else:
            result, error = ctrl.changeSetting(intCD, entityName=entityName, avatar=BigWorld.player(), idx=idx)
            self._handleEquipmentPressedResult(result, error)
            return

    def _handleEquipmentPressedResult(self, result, error):
        if not result and error:
            ctrl = self.sessionProvider.shared.messages
            if ctrl is not None:
                ctrl.showVehicleError(error.key, error.ctx)
        return

    def _getEquipmentIdxByKey(self, key):
        return self._cds.index(key) if key in self._cds else None

    def __onDebuffStarted(self, debuffTime=None):
        self.delayedReload = debuffTime

    def __startReloadDelayed(self, shellIndex, state):
        if self.delayedReload is None:
            return
        else:
            leftTimeDelayed = state.getActualValue() - self.delayedReload
            baseTimeDelayed = state.getBaseValue() - self.delayedReload
            if leftTimeDelayed > 0 and baseTimeDelayed > 0:
                shellReload = shellIndex
                if self.__delayedNextShellID is not None:
                    shellReload = self._cds.index(self.__delayedNextShellID)
                    self.__delayedNextShellID = None
                self.as_setCoolDownTimeS(shellReload, leftTimeDelayed, baseTimeDelayed, 0)
            else:
                _logger.error('Incorrect delayed reload timings: %f, %f', leftTimeDelayed, baseTimeDelayed)
            self.delayedReload = None
            return

    def __startReload(self, shellIndex, state):
        if self.__reloadTicker:
            self.__reloadTicker.startAnimation(shellIndex, state.getActualValue(), state.getBaseValue())
        else:
            actualValue = state.getActualValue()
            reloadingFinished = state.isReloadingFinished()
            if actualValue > 0 or reloadingFinished and not self.ammoReloadingStatus.get(shellIndex):
                self.ammoReloadingStatus[shellIndex] = reloadingFinished
                self.as_setCoolDownTimeS(shellIndex, actualValue, state.getBaseValue(), state.getTimePassed())

    def __onOptionalDeviceAdded(self, optDeviceInBattle):
        if optDeviceInBattle.getIntCD() not in self._cds:
            idx = self.__genNextIdx(self.__optDeviceFullMask, self._OPT_DEVICE_START_IDX)
            self._addOptionalDeviceSlot(idx, optDeviceInBattle)

    def __onOptionalDeviceUpdated(self, optDeviceInBattle):
        intCD = optDeviceInBattle.getIntCD()
        if intCD in self._cds:
            self._updateOptionalDeviceSlot(self._cds.index(intCD), optDeviceInBattle)
        else:
            _logger.error('Optional device with cd=%d is not found in panel=%s', intCD, str(self._cds))

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._reset()
        if noRespawnPossible:
            if not BigWorld.player().isObserver():
                self._removeListeners()

    def _onRespawnBaseMoving(self):
        self._reset()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self._clearAllEquipmentGlow()
            return
        elif self._cds.count(None) == self._PANEL_MAX_LENGTH:
            return
        else:
            ctrl = self.sessionProvider.shared.equipments
            if ctrl is None:
                return
            if state == VEHICLE_VIEW_STATE.DEVICES:
                deviceName, deviceState, actualState = value
                itemName = VEHICLE_DEVICE_IN_COMPLEX_ITEM.get(deviceName, deviceName)
                equipmentTag = 'medkit' if itemName in TANKMEN_ROLES_ORDER_DICT['enum'] else 'repairkit'
                if deviceState == actualState and deviceState == DEVICE_STATE_DESTROYED:
                    for intCD, _ in ctrl.iterEquipmentsByTag(equipmentTag, _isEquipmentAvailableToUse):
                        self._showEquipmentGlow(self._cds.index(intCD))

                elif deviceState != DEVICE_STATE_DESTROYED:
                    for intCD, equipment in ctrl.iterEquipmentsByTag(equipmentTag):
                        if not self._canApplyingGlowEquipment(equipment):
                            self.__clearEquipmentGlow(self._cds.index(intCD))

            elif state == VEHICLE_VIEW_STATE.STUN:
                if value.duration > 0:
                    for intCD, _ in ctrl.iterEquipmentsByTag('medkit', _isEquipmentAvailableToUse):
                        self._showEquipmentGlow(self._cds.index(intCD))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('medkit'):
                        if not self._canApplyingGlowEquipment(equipment):
                            self.__clearEquipmentGlow(self._cds.index(intCD))

            elif state == VEHICLE_VIEW_STATE.FIRE:
                if value:
                    hasReadyAutoExt = False
                    glowCandidates = []
                    for intCD, equipment in ctrl.iterEquipmentsByTag('extinguisher'):
                        if not equipment.isReady:
                            continue
                        if equipment.getDescriptor().autoactivate:
                            hasReadyAutoExt = True
                        glowCandidates.append(intCD)

                    if not hasReadyAutoExt:
                        for cID in glowCandidates:
                            self._showEquipmentGlow(self._cds.index(cID))

                else:
                    for intCD, equipment in ctrl.iterEquipmentsByTag('extinguisher'):
                        if not equipment.getDescriptor().autoactivate:
                            self.__clearEquipmentGlow(self._cds.index(intCD))

            return

    def _canApplyingGlowEquipment(self, equipment):
        equipmentTags = equipment.getTags()
        if 'extinguisher' in equipmentTags or 'regenerationKit' in equipmentTags:
            correction = True
            entityName = None
        elif equipment.isAvatar():
            correction = False
            entityName = None
        else:
            entityNames = [ name for name, state in equipment.getEntitiesIterator() if state == DEVICE_STATE_DESTROYED ]
            correction = hasDestroyed = len(entityNames)
            entityName = entityNames[0] if hasDestroyed else None
        canActivate, info = equipment.canActivate(entityName)
        infoType = type(info)
        return correction and (canActivate or infoType == NeedEntitySelection) or infoType == IgnoreEntitySelection

    def _hideEquipmentGlowCallback(self, equipmentIndex):
        return self.__clearEquipmentGlow(equipmentIndex, cancelCallback=False)

    def __clearEquipmentGlow(self, equipmentIndex, cancelCallback=True):
        if equipmentIndex in self._equipmentsGlowCallbacks:
            self.as_hideGlowS(equipmentIndex)
            if cancelCallback:
                BigWorld.cancelCallback(self._equipmentsGlowCallbacks[equipmentIndex])
            del self._equipmentsGlowCallbacks[equipmentIndex]

    def _clearAllEquipmentGlow(self):
        for equipmentIndex, callbackID in self._equipmentsGlowCallbacks.items():
            BigWorld.cancelCallback(callbackID)
            self.as_hideGlowS(equipmentIndex)
            del self._equipmentsGlowCallbacks[equipmentIndex]

    def __fillShells(self, ctrl):
        forEach(lambda args: self._onShellsAdded(*args), ctrl.getOrderedShellsLayout())
        shellCD = ctrl.getNextShellCD()
        if shellCD is not None:
            self._onNextShellChanged(shellCD)
        shellCD = ctrl.getCurrentShellCD()
        if shellCD is not None:
            self._onCurrentShellChanged(shellCD)
        return

    def __fillEquipments(self, ctrl):
        forEach(lambda args: self._onEquipmentAdded(*args), ctrl.getOrderedEquipmentsLayout())

    def __fillOptionalDevices(self, ctrl):
        forEach(lambda args: self.__onOptionalDeviceAdded(*args), ctrl.getOrderedOptionalDevicesLayout())

    def __onSPGShotsIndicatorStateChanged(self, shotStates):
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        ammoCtrl = self.sessionProvider.shared.ammo
        if vehicle is not None:
            vehicleDescriptor = vehicle.typeDescriptor
            for i, shotDescr in enumerate(vehicleDescriptor.gun.shots):
                intCD = shotDescr.shell.compactDescr
                if intCD in self._cds and ammoCtrl.shellInAmmo(intCD):
                    quantity, _ = ammoCtrl.getShells(intCD)
                    shotState, _ = shotStates.get(i, (-1, None)) if quantity > 0 else (-1, None)
                    self.as_setSPGShotResultS(self._cds.index(intCD), int(shotState))

        return

    def __onCrosshairViewChanged(self, viewID):
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        needClear = viewID not in (CROSSHAIR_VIEW_ID.STRATEGIC,)
        if vehicle is not None and needClear:
            vehicleDescriptor = vehicle.typeDescriptor
            for shotDescr in vehicleDescriptor.gun.shots:
                intCD = shotDescr.shell.compactDescr
                if intCD in self._cds:
                    self.as_setSPGShotResultS(self._cds.index(intCD), -1)

        return
