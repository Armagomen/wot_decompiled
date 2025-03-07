# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/member_change_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.game_control import restore_contoller
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.filter_panel_widget_model import FilterPanelType
from gui.impl.gen.view_models.views.lobby.crew.member_change_tankman_model import MemberChangeTankmanModel
from gui.impl.gen.view_models.views.lobby.crew.member_change_view_model import MemberChangeViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanCardState, TankmanKind
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.base_crew_view import BaseCrewView
from gui.impl.lobby.crew.base_tankman_list_view import BaseTankmanListView
from gui.impl.lobby.crew.crew_helpers.model_setters import setRecruitTankmanModel, setTankmanModel, setTmanSkillsModel
from gui.impl.lobby.crew.filter import getTankmanKindSettings, getTankmanLocationSettings, getTankmanRoleSettings, getVehicleTierSettings, getVehicleTypeSettings
from gui.impl.lobby.crew.filter.data_providers import CompoundDataProvider, RecruitsChangeDataProvider, TankmenChangeDataProvider
from gui.impl.lobby.crew.filter.filter_panel_widget import FilterPanelWidget
from gui.impl.lobby.crew.filter.state import FilterState, Persistor
from gui.impl.lobby.crew.utils import discountPercent
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import VehicleSkillPreviewParamsView
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared.gui_items.Tankman import NO_SLOT
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.items_actions import factory
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.game_control import IRestoreController, ISpecialSoundCtrl
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils.requesters import IShopRequester
from PlayerEvents import g_playerEvents
from AccountCommands import LOCK_REASON

class MemberChangeView(BaseCrewView, BaseTankmanListView):
    itemsCache = dependency.descriptor(IItemsCache)
    restore = dependency.descriptor(IRestoreController)
    specialSounds = dependency.descriptor(ISpecialSoundCtrl)

    def __init__(self, layoutID, **kwargs):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=MemberChangeViewModel(), kwargs=kwargs)
        vehicleInvID = kwargs.get('vehicleInvID', NO_VEHICLE_ID)
        slotIdx = kwargs.get('slotIdx', NO_SLOT)
        self.__currentVehicle = self.itemsCache.items.getVehicle(vehicleInvID)
        self.__tankmanId = None
        self.__slotIdx = None
        self.__requiredRole = None
        self.__tankman = None
        self.__filterPanelWidget = None
        self.__updateTankmanData(slotIdx)
        self.__filterState = FilterState(initialState=self._getDefaultFilters(), isWotPlus=self.__currentVehicle.isWotPlus, persistor=Persistor(storageKey='memberChange', persistentGroups=[FilterState.GROUPS.LOCATION.value]))
        self.__dataProviders = self._createDataProvider()
        self.__requiredNation = self.__currentVehicle.nationName
        self.__paramsView = None
        self.__hasFilters = False
        super(MemberChangeView, self).__init__(settings)
        return

    @property
    def _tankmenProvider(self):
        return self.__dataProviders['tankmen']

    @property
    def _recruitsProvider(self):
        return self.__dataProviders['recruits']

    @property
    def _filterState(self):
        return self.__filterState

    @property
    def viewModel(self):
        return super(MemberChangeView, self).getViewModel()

    def selectSlot(self, slotIdx):
        self._onChangeSlotIdx(slotIdx)
        self._crewWidget.updateSlotIdx(self.__slotIdx)
        with self.viewModel.transaction() as tx:
            tx.setRequiredRole(self.__requiredRole)
            self._fillTankmenList(tx)

    def _createDataProvider(self):
        bonusRoles = self.__currentVehicle.descriptor.type.crewRoles[self.__slotIdx][1:]
        _providerKwargs = dict(state=self.__filterState, tankman=self.__tankman, vehicle=self.__currentVehicle, role=self.__requiredRole, bonusRoles=bonusRoles)
        return CompoundDataProvider(tankmen=TankmenChangeDataProvider(**_providerKwargs), recruits=RecruitsChangeDataProvider(**_providerKwargs))

    def _getDefaultFilters(self):
        if self.__currentVehicle.isWotPlus:
            return {FilterState.GROUPS.TANKMANROLE.value: self.__requiredRole}
        return {FilterState.GROUPS.TANKMANROLE.value: self.__requiredRole,
         FilterState.GROUPS.VEHICLETYPE.value: self.__currentVehicle.type} if self.__currentVehicle.isPremium else {}

    def _getEvents(self):
        eventsTuple = super(MemberChangeView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onResetFilters, self._onResetFilters),
         (self.viewModel.onTankmanSelected, self._onTankmanSelected),
         (self.viewModel.onRecruitSelected, self._onRecruitSelected),
         (self.viewModel.onRecruitNewTankman, self._onRecruitNewTankman),
         (self.viewModel.onTankmanRestore, self._onTankmanRestore),
         (self.viewModel.onPlayRecruitVoiceover, self._onPlayRecruitVoiceover),
         (self.viewModel.onLoadCards, self._onLoadCards),
         (self.__filterState.onStateChanged, self._onFilterStateUpdated),
         (self.__dataProviders.onDataChanged, self._onDataChanged),
         (self.itemsCache.onSyncCompleted, self._onItemsCacheSyncCompleted),
         (g_playerEvents.onVehicleLockChanged, self._onVehicleLockChanged))

    def _getCallbacks(self):
        return (('inventory.1.crew', self._onCrewChanged),
         ('inventory.8.compDescr', self._onCrewChanged),
         ('tokens', self._onCrewChanged),
         ('potapovQuests', self._onCrewChanged))

    def _setWidgets(self, **kwargs):
        super(MemberChangeView, self)._setWidgets(**kwargs)
        self.__paramsView = VehicleSkillPreviewParamsView()
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self.__paramsView)
        self.__filterPanelWidget = FilterPanelWidget(getTankmanLocationSettings(), self.__getPopoverGroupSettings(), R.strings.crew.filter.popup.default.title(), self.__filterState, title=R.strings.crew.tankmanList.filter.title(), panelType=FilterPanelType.MEMBERCHANGE, popoverTooltipHeader=R.strings.crew.tankmanList.tooltip.popover.header(), popoverTooltipBody=R.strings.crew.tankmanList.tooltip.popover.body(), hasDiscountAlert=self.__isChangeRoleDiscountAvailable)
        self.setChildView(FilterPanelWidget.LAYOUT_ID(), self.__filterPanelWidget)

    def _fillTankmen(self, cardsList, limit, offset):
        selectedTankman = self.itemsCache.items.getTankman(self.__tankmanId)
        if selectedTankman:
            self._fillTankmanCard(cardsList, selectedTankman)
            limit -= 1
        recruitsAmount, visibleAmount = super(MemberChangeView, self)._fillTankmen(cardsList, limit, offset)
        if selectedTankman:
            recruitsAmount += 1
            visibleAmount += 1
        return (recruitsAmount, visibleAmount)

    def _fillViewModel(self, vm):
        super(MemberChangeView, self)._fillViewModel(vm)
        vm.setVehicle(self.__currentVehicle.descriptor.type.shortUserString)
        vm.setRequiredRole(self.__requiredRole)
        vm.setNation(self.__requiredNation)
        vm.setRoleChangeDiscountPercent(self.__roleChangeDiscountPercent)
        vm.setHasCrew(self.__currentVehicle.hasCrew)
        fillVehicleInfo(vm.vehicleInfo, self.__currentVehicle, separateIGRTag=True)
        self._fillTankmenList(vm)
        vm.setIsRecruitDisabled(self.itemsCache.items.freeTankmenBerthsCount() < 1)

    def _fillTankmenList(self, tx):
        self.__filterPanelWidget.updateAmountInfo(self.__dataProviders.itemsCount, self.__dataProviders.initialItemsCount)
        self.__filterPanelWidget.applyStateToModel()
        tx.setHasFilters(self.__hasFilters)
        itemsCount = self.__dataProviders.itemsCount
        if self.itemsCache.items.getTankman(self.__tankmanId):
            itemsCount += 1
        tx.setItemsAmount(itemsCount)
        tx.setItemsOffset(self._itemsOffset)
        self._fillVisibleCards(tx.getTankmanList())

    def _fillVisibleCards(self, cardsList):
        cardsList.clear()
        cardsList.invalidate()
        recruitsAmount, visibleAmount = self._fillTankmen(cardsList, self._itemsLimit, self._itemsOffset)
        tankmanOffset = max(self._itemsOffset - recruitsAmount, 0)
        self._fillRecruits(cardsList, self._itemsLimit - visibleAmount, tankmanOffset)

    def _fillTankmanCard(self, cardsList, tankman):
        cardsList.addViewModel(self.__createTankmanModelByTankman(tankman))

    def _fillRecruitCard(self, cardsList, recruitInfo):
        tm = MemberChangeTankmanModel()
        setRecruitTankmanModel(tm, recruitInfo, useOnlyFullSkills=False)
        cardsList.addViewModel(tm)

    def _onLoading(self, *args, **kwargs):
        super(MemberChangeView, self)._onLoading(*args, **kwargs)
        self.__dataProviders.subscribe()
        self.__dataProviders.update()
        if self.__dataProviders.itemsCount < 1:
            self.__filterState.reinit({})

    def widgetAutoSelectSlot(self, **kwargs):
        self._crewWidget.updateSlotIdx(self.__slotIdx)

    def _finalize(self):
        self.__dataProviders.unsubscribe()
        super(MemberChangeView, self)._finalize()
        self.__currentVehicle = None
        self.__tankman = None
        self.__filterState = None
        self.__filterPanelWidget = None
        self.__paramsView = None
        self.__dataProviders = None
        self.__paramsView = None
        return

    def _onItemsCacheSyncCompleted(self, reason, _):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__updatedRoleChangeCost()

    def _onVehicleLockChanged(self, _, lockReason):
        if lockReason[0] == LOCK_REASON.NONE:
            self._onFilterStateUpdated()

    def _onEmptySlotClick(self, tankmanID, slotIdx):
        self.selectSlot(slotIdx)

    def _onFilterStateUpdated(self):
        self.__hasFilters = self.__filterPanelWidget.hasAppliedFilters()
        self.__dataProviders.update()

    def _onClose(self, params=None):
        if self.__currentVehicle.hasCrew and self.isPersonalFileOpened:
            self._onBack()
        else:
            self._destroySubViews()

    def _onDataChanged(self):
        self._updateViewModel()

    def _onWidgetChangeCrewClick(self, _, slotIdx, __):
        self.selectSlot(slotIdx)

    def _onResetFilters(self):
        self.__filterPanelWidget.resetState()

    def _onCrewChanged(self, *_, **__):
        self._onChangeSlotIdx(self.__slotIdx)

    def _onChangeSlotIdx(self, slotIdx):
        self.__updateTankmanData(slotIdx)
        self.viewModel.setHasCrew(self.__currentVehicle.hasCrew)
        bonusRoles = self.__currentVehicle.descriptor.type.crewRoles[slotIdx][1:]
        self.__dataProviders.reinit(tankman=self.__tankman, role=self.__requiredRole, bonusRoles=bonusRoles)
        self.__filterState.reinit(self._getDefaultFilters())
        if self.__dataProviders.itemsCount < 1:
            self.__filterState.reinit({})

    @args2params(int)
    def _onTankmanSelected(self, tankmanID):
        if tankmanID == self.__tankmanId:
            return
        newTankman = self.itemsCache.items.getTankman(tankmanID)
        if not newTankman or newTankman.isDismissed:
            return
        if newTankman.role == self.__requiredRole:
            self.__equipTankman(newTankman)
        else:
            self.__changeRoleAndEquipConfirm(newTankman)

    @args2params(str)
    def _onPlayRecruitVoiceover(self, recruitID):
        self._onPlayVoiceover(recruitID)

    @args2params(str)
    def _onRecruitSelected(self, recruitID):
        showRecruitWindow(recruitID, vehicleSlotToUnpack=self.__slotIdx, vehicle=self.__currentVehicle)

    @args2params(int)
    def _onTankmanRestore(self, tankmanID):
        dialogs.showRestoreTankmanDialog(tankmanID, self.__currentVehicle.invID, self.__slotIdx)

    def _onRecruitNewTankman(self):
        dialogs.showRecruitNewTankmanDialog(self.__currentVehicle.intCD, self.__slotIdx, putInTank=True)

    @property
    def __roleChangeDiscountPercent(self):
        shopRequester = self.itemsCache.items.shop
        return discountPercent(shopRequester.changeRoleCost, shopRequester.defaults.changeRoleCost) if shopRequester.defaults.changeRoleCost else 0

    @property
    def __isChangeRoleDiscountAvailable(self):
        return self.__roleChangeDiscountPercent > 0

    def __getPopoverGroupSettings(self):
        return (getTankmanRoleSettings(self.__isChangeRoleDiscountAvailable),
         getVehicleTypeSettings(customTooltipBody=R.strings.crew.filter.tooltip.crewMemberVehicleType.body()),
         getVehicleTierSettings(),
         getTankmanKindSettings(labelResId=R.strings.crew.filter.group.other.title(), options=(TankmanKind.DISMISSED,)))

    def __updatedRoleChangeCost(self):
        self.__filterPanelWidget.updateHasDiscountAlert(self.__isChangeRoleDiscountAvailable)
        self.__filterPanelWidget.updatePopoverGroupSettings(self.__getPopoverGroupSettings())
        self.__filterPanelWidget.applyStateToModel()
        with self.viewModel.transaction() as tx:
            tx.setRoleChangeDiscountPercent(self.__roleChangeDiscountPercent)

    def __equipTankman(self, newTankman):
        if self.__currentVehicle:
            factory.doAction(factory.EQUIP_TANKMAN, newTankman.invID, self.__currentVehicle.invID, int(self.__slotIdx))

    def __changeRoleAndEquipConfirm(self, newTankman):
        dialogs.showRetrainSingleDialog(newTankman.invID, self.__currentVehicle.intCD, targetSlotIdx=int(self.__slotIdx))

    def __createTankmanModelByTankman(self, tankman):
        tm = MemberChangeTankmanModel()
        tankmanCurrVehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
        setTankmanModel(tm, tankman, tmanNativeVeh=self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr), tmanVeh=tankmanCurrVehicle)
        if tankman.invID == self.__tankmanId:
            tm.setCardState(TankmanCardState.SELECTED)
        elif tankman.isInTank and self.__currentVehicle.intCD == tankmanCurrVehicle.intCD and tankman.role in self.__currentVehicle.descriptor.type.crewRoles[self.__slotIdx]:
            tm.setIsInSameVehicle(True)
        tm.setHasRolePenalty(self.__requiredRole != tankman.role)
        setTmanSkillsModel(tm.skills, tankman, compVeh=self.__currentVehicle)
        if tankman.isDismissed:
            _, time = restore_contoller.getTankmenRestoreInfo(tankman)
            tm.setTimeToDismiss(time)
        return tm

    def __updateTankmanData(self, slotIdx):
        self.__slotIdx = int(slotIdx)
        self.__currentVehicle = self.itemsCache.items.getVehicle(self.__currentVehicle.invID)
        self.__tankmanId = self.__currentVehicle.getTankmanIDBySlotIdx(self.__slotIdx)
        self.__tankman = self.itemsCache.items.getTankman(self.__tankmanId)
        self.__requiredRole = self.__currentVehicle.descriptor.type.crewRoles[self.__slotIdx][0]
