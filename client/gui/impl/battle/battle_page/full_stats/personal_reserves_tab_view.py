# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/full_stats/personal_reserves_tab_view.py
import logging
import typing

import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf import ViewModel
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import \
    getPersonalBoosterModelDataByResourceType, addPersonalBoostersGroup, addEventGroup
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_page.personal_reserves_tab_view_model import \
    PersonalReservesTabViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.goodies import IBoostersStateProvider

if typing.TYPE_CHECKING:
    pass
_logger = logging.getLogger(__name__)

class PersonalReservesTabView(ViewImpl):
    __slots__ = ()
    boostersStateProvider = dependency.descriptor(IBoostersStateProvider)

    def __init__(self):
        settings = ViewSettings(R.views.battle.battle_page.PersonalReservesTabView(), ViewFlags.COMPONENT, PersonalReservesTabViewModel())
        super(PersonalReservesTabView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalReservesTabView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.personal_reserves.ReservesDisabledTooltip():
            settings = ViewSettings(layoutID=R.views.common.personal_reserves.ReservesDisabledTooltip(), model=ViewModel())
            return ViewImpl(settings)
        return super(PersonalReservesTabView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(PersonalReservesTabView, self)._initialize(*args, **kwargs)
        PersonalReservesTabView.boostersStateProvider.onStateUpdated += self.onBoostersStateChanged
        self.viewModel.onBoosterActivate += self.onBoosterActivate

    def _finalize(self):
        PersonalReservesTabView.boostersStateProvider.onStateUpdated -= self.onBoostersStateChanged
        self.viewModel.onBoosterActivate -= self.onBoosterActivate
        super(PersonalReservesTabView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(PersonalReservesTabView, self)._onLoading(*args, **kwargs)
        self.fillViewModel()

    def activatePersonalReserve(self, boosterId):
        BigWorld.player().activateGoodie(boosterId)

    @args2params(int)
    def onBoosterActivate(self, boosterId):
        booster = PersonalReservesTabView.boostersStateProvider.getBooster(boosterId)
        if booster.boosterType in PersonalReservesTabView.boostersStateProvider.getActiveBoosterTypes():
            _logger.warning('[PersonalReservesTabView] Booster %d cannot be activated as another booster of the same type is already active in this battle.', booster.boosterID)
            return
        if booster.isInAccount:
            self.activatePersonalReserve(boosterId)
        else:
            _logger.warning('[PersonalReservesTabView] Cannot activate booster %d, player does not have this booster in inventory. Buy and activate action is not possible during battle.', booster.boosterID)

    def onBoostersStateChanged(self):
        self.fillViewModel()

    def fillViewModel(self):
        boosterModelsArgsByType = getPersonalBoosterModelDataByResourceType(PersonalReservesTabView.boostersStateProvider)
        with self.viewModel.transaction() as model:
            groupArray = model.getReserveGroups()
            groupArray.clear()
            for resourceType in PERSONAL_RESOURCE_ORDER:
                addPersonalBoostersGroup(resourceType, boosterModelsArgsByType, groupArray)

            addEventGroup(groupArray, PersonalReservesTabView.boostersStateProvider)
            groupArray.invalidate()
