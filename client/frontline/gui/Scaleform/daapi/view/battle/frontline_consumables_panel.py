# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_consumables_panel.py
from functools import partial
import BigWorld
from ReservesEvents import randomReservesEvents
from frontline.gui.Scaleform.daapi.view.meta.FrontlineBattleConsumablesPanelMeta import FrontlineBattleConsumablesPanelMeta
from frontline.gui.frontline_helpers import getReserveIconPath
from frontline_common.frontline_constants import FLBattleReservesModifier
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from helpers.epic_game import searchRankForSlot
from items import EQUIPMENT_TYPES
from items.vehicles import getVehicleClassFromVehicleType
from vehicle_systems.stricted_loading import makeCallbackWeak

class FrontlineBattleConsumablesPanel(FrontlineBattleConsumablesPanelMeta, ConsumablesPanel):
    _EMPTY_LOCKED_SLOT = -1
    _GLOW_DELAY = 0.5
    _WAITED_SLOT_GLOW_TIME = 3
    _R_EPIC_EQUIPMENT_ICON = R.images.gui.maps.icons.epicBattles.skills.c_48x48
    __EMPTY_SCALE_FORM_KEY = -1

    def __init__(self):
        super(FrontlineBattleConsumablesPanel, self).__init__()
        self.__battleReserveSlots = dict()
        self.__glowUpdateInfo = dict()
        self.__indicatedSlots = set()
        self.__currentSlotIdx = None
        return

    @property
    def isRandomBattleReserves(self):
        arenaDP = self.sessionProvider.getArenaDP()
        return arenaDP and arenaDP.getReservesModifier() == FLBattleReservesModifier.RANDOM

    def _addListeners(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onSlotWaited += self._onSlotWaited
            eqCtrl.onSlotBlocked += self._onSlotBlocked
        randomReservesEvents.onShownPanel += self._updateLockedSlot
        super(FrontlineBattleConsumablesPanel, self)._addListeners()
        return

    def _removeListeners(self):
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onSlotWaited -= self._onSlotWaited
            eqCtrl.onSlotBlocked -= self._onSlotBlocked
        randomReservesEvents.onShownPanel -= self._updateLockedSlot
        super(FrontlineBattleConsumablesPanel, self)._removeListeners()
        return

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.EPIC_BATTLE_SETTINGS_ID

    def _reset(self):
        super(FrontlineBattleConsumablesPanel, self)._reset()
        self.__battleReserveSlots.clear()

    def _updateEquipmentSlotTooltipText(self, idx, item):
        self.as_updateTooltipS(idx=idx, tooltipStr=self._getToolTipEquipmentSlot(item, idx))

    def _getEquipmentIdxByKey(self, key):
        if isinstance(key, tuple):
            intCD, index = key
            if index > 0:
                return index + self._ORDERS_START_IDX - 1
            if intCD in self._cds:
                return self._cds.index(intCD)
        return None

    def _getEquipmentKeyHandler(self, intCD, idx=0):
        return partial(self._handleEquipmentPressedStack, intCD, idx) if self._ORDERS_START_IDX <= idx <= self._ORDERS_END_IDX else super(FrontlineBattleConsumablesPanel, self)._getEquipmentKeyHandler(intCD, idx)

    def _setEquipmentKeyHandler(self, item, bwKey, idx):
        if item.getQuantity() > 0 and bwKey not in self._keys:
            if self._ORDERS_START_IDX <= idx <= self._ORDERS_END_IDX:
                handler = partial(self._handleEquipmentPressedStack, self._cds[idx], idx)
                self._keys[bwKey] = handler
            else:
                super(FrontlineBattleConsumablesPanel, self)._setEquipmentKeyHandler(item, bwKey, idx)

    def _handleEquipmentPressedStack(self, intCD, idx):
        serverIdx = idx - self._ORDERS_START_IDX
        self._handleEquipmentPressed(intCD, idx=serverIdx)

    def _getToolTipEquipmentSlot(self, item, idx=None):
        return TOOLTIPS_CONSTANTS.FRONTLINE_RANDOM_RESERVE if self.isRandomBattleReserves and not self._isEquipmentSlot(self.__currentSlotIdx if idx is None else idx) else super(FrontlineBattleConsumablesPanel, self)._getToolTipEquipmentSlot(item)

    def _getSlotIndex(self, index):
        return self._ORDERS_START_IDX + index

    def _onEquipmentAdded(self, intCD, item):
        if item and item.index > 0:
            index = item.index
            slotIndex = self._getSlotIndex(index - 1)
            self._addEquipmentSlot(slotIndex, intCD, item)
            if self.sessionProvider.isReplayPlaying:
                randomReservesEvents.onSelectedReserve(item.getDescriptor().compactDescr, False)
        else:
            super(FrontlineBattleConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def __addEquipmentSlotS(self, index, bwKey, sfKey, quantity, timeRemaining, reloadingTime, iconPath, tooltipText, animation, isTooltipSpecial=False):
        self.as_addEpicBattleEquipmentSlotS(idx=index, keyCode=bwKey, sfKeyCode=sfKey, quantity=quantity, timeRemaining=timeRemaining, reloadingTime=reloadingTime, iconPath=iconPath, isTooltipSpecial=isTooltipSpecial, tooltipText=tooltipText, animation=animation)

    def _onSlotBlocked(self, slotId):
        index = self._getSlotIndex(slotId)
        bwKey, _ = self._genKey(slotId)
        self.as_hideGlowS(index)
        self.__addEquipmentSlotS(index, bwKey, self.__EMPTY_SCALE_FORM_KEY, 0, 0, 0, getReserveIconPath('empty_slot'), self._getToolTipEquipmentSlot(None, slotId), ANIMATION_TYPES.NONE, self.isRandomBattleReserves)
        return

    def _onSlotWaited(self, slotId, quantity):
        index = self._getSlotIndex(slotId)
        bwKey, sfKey = self._genKey(index)
        self.__addEquipmentSlotS(index, bwKey, sfKey, quantity + 1, 0, 0, getReserveIconPath('empty_slot'), '', ANIMATION_TYPES.NONE, self.isRandomBattleReserves)
        if index not in self.__indicatedSlots:
            self.__addLockedInformationToEpicEquipment(index)

    def _addEquipmentSlot(self, idx, intCD, item):
        if item is None:
            return super(FrontlineBattleConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
        else:
            self.__currentSlotIdx = idx
            quantity = item.getQuantity()
            descriptor = item.getDescriptor()
            if quantity > 1 and descriptor.equipmentType == EQUIPMENT_TYPES.battleAbilities:
                self.delayCallback(self._GLOW_DELAY, self.__possibleStacksDelayCB, idx, quantity)
                self.delayCallback(self._GLOW_DELAY + self._EQUIPMENT_GLOW_TIME, self.__stacksHideGrowDelayCB, idx)
            self._cds[idx] = intCD
            tags = item.getTags()
            if tags:
                bwKey, sfKey = self._genKey(idx)
                handler = self._getEquipmentKeyHandler(intCD, idx)
                if item.getQuantity() > 0:
                    self._extraKeys[idx] = self._keys[bwKey] = handler
            else:
                bwKey, sfKey = (None, None)
            iconPath = self._getEquipmentIcon(idx, item, descriptor.icon[0])
            self.__addEquipmentSlotS(idx, bwKey, sfKey, quantity, item.getTimeRemaining(), item.getTotalTime(), iconPath, self._getToolTipEquipmentSlot(item), item.getAnimationType(), self.isRandomBattleReserves and self._ORDERS_START_IDX <= idx <= self._ORDERS_END_IDX)
            if idx < self._ORDERS_START_IDX:
                return
            if idx not in self.__battleReserveSlots:
                self.__battleReserveSlots[idx] = (intCD, item.getQuantity())
                self.__addEquipmentLevelToSlot(idx, item)
                if not self.isRandomBattleReserves:
                    self.__addLockedInformationToEpicEquipment(idx)
            if self.isRandomBattleReserves:
                self.__updateLockedInformation(idx)
            return

    def _getEquipmentIcon(self, idx, item, icon):
        return backport.image(self._R_EPIC_EQUIPMENT_ICON.dyn(icon)()) if idx in self.__battleReserveSlots else super(FrontlineBattleConsumablesPanel, self)._getEquipmentIcon(idx, item, icon)

    def _resetEquipmentSlot(self, idx, intCD, item):
        super(FrontlineBattleConsumablesPanel, self)._resetEquipmentSlot(idx, intCD, item)
        if idx not in self.__battleReserveSlots:
            return
        oldCD, prevQuantity = self.__battleReserveSlots[idx]
        quantity = item.getQuantity()
        self.__battleReserveSlots[idx] = (intCD, quantity)
        self.__addEquipmentLevelToSlot(idx, item)
        if quantity and prevQuantity and oldCD != self._cds[idx]:
            self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_UPGRADE
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)

    def __possibleStacksDelayCB(self, idx, quantity):
        self.as_showPossibleStacksS(idx, quantity)
        self.as_updateStacksS(idx, quantity)

    def __stacksHideGrowDelayCB(self, idx):
        self.as_hideGlowS(idx)
        self.as_showPossibleStacksS(idx, 0)

    def _updateLockedSlot(self, slotId):
        index = self._getSlotIndex(slotId)
        self.__updateLockedInformation(index, isSlotEmpty=self.isRandomBattleReserves)
        if index not in self.__indicatedSlots:
            self.__indicatedSlots.add(index)
            self.__glowUpdateInfo[index] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)
            BigWorld.callback(self._GLOW_DELAY + self._WAITED_SLOT_GLOW_TIME, makeCallbackWeak(self.as_hideGlowS, index))

    def _updateEquipmentSlot(self, idx, item):
        idx = item.index - 1 + self._ORDERS_START_IDX if item and item.index > 0 else idx
        super(FrontlineBattleConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        if idx not in self.__battleReserveSlots:
            return
        oldCD, prevQuantity = self.__battleReserveSlots[idx]
        quantity = item.getQuantity()
        if prevQuantity < quantity:
            self.__updateLockedInformation(idx, isSlotEmpty=self.isRandomBattleReserves)
            self.__battleReserveSlots[idx] = (self._cds[idx], quantity)
            if quantity > 1:
                self.delayCallback(self._GLOW_DELAY, self.__possibleStacksDelayCB, idx, quantity)
                self.delayCallback(self._GLOW_DELAY + self._EQUIPMENT_GLOW_TIME, self.__stacksHideGrowDelayCB, idx)
                self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL
            else:
                self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_UNLOCK
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)
        elif quantity and prevQuantity == quantity and oldCD == self._cds[idx]:
            self.__updateLockedInformation(idx, isSlotEmpty=self.isRandomBattleReserves)
        elif quantity < 1 and not self.isRandomBattleReserves:
            self.__addLockedInformationToEpicEquipment(idx)
        self.__addEquipmentLevelToSlot(idx, item)

    def __updateEquipmentGlowCB(self):
        for idx in self.__glowUpdateInfo:
            self.as_setGlowS(idx, self.__glowUpdateInfo[idx])

        self.__glowUpdateInfo.clear()

    def _onEquipmentReset(self, oldIntCD, intCD, item):
        if item and item.index > 0:
            index = item.index - 1 + self._ORDERS_START_IDX
            self._resetEquipmentSlot(index, intCD, item)
            return
        super(FrontlineBattleConsumablesPanel, self)._onEquipmentReset(oldIntCD, intCD, item)

    def __addLockedInformationToEpicEquipment(self, idx):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if not all((playerDataComp, vehicle, arena)):
            return
        else:
            vehClass = getVehicleClassFromVehicleType(vehicle.typeDescriptor.type)
            if self.isRandomBattleReserves:
                slotEventsConfig = list(([idx] for idx in range(self._ORDERS_END_IDX - self._ORDERS_START_IDX + 1)))
            else:
                slotEventsConfig = arena.settings.get('epic_config', {}).get('epicMetaGame', {}).get('inBattleReservesByRank').get('slotActions', {}).get(vehClass, {})
            if not slotEventsConfig:
                return
            unlockedSlotIdx = idx - self._ORDERS_START_IDX
            rank = searchRankForSlot(unlockedSlotIdx, slotEventsConfig)
            currentRank = playerDataComp.playerRank if playerDataComp.playerRank is not None else 0
            if rank is None or rank <= currentRank - 1:
                return
            rank += 1
            tooltipId = TOOLTIPS_CONSTANTS.EPIC_RANK_UNLOCK_INFO if rank > 1 or self.isRandomBattleReserves else ''
            self.__updateLockedInformation(idx, rank, tooltipId, bool(tooltipId) if self.isRandomBattleReserves else False)
            return

    def __addEquipmentLevelToSlot(self, idx, item):
        itemName = item.getDescriptor().name
        if 'level' not in itemName:
            return
        levelStr = itemName.partition('level')[-1]
        if not levelStr.isdigit():
            return
        self.as_updateLevelInformationS(idx, int(levelStr))

    def __updateLockedInformation(self, idx, lockedID=None, tooltipStr='', isSlotEmpty=False):
        if lockedID is None:
            lockedID = self._EMPTY_LOCKED_SLOT
        self.as_updateLockedInformationS(idx, lockedID, tooltipStr, isSlotEmpty)
        return
