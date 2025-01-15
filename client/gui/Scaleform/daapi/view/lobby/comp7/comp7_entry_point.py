# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/comp7_entry_point.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.ResizableEntryPointMeta import ResizableEntryPointMeta
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.lobby.comp7.comp7_shared import getBannerSeasonState
from gui.impl.lobby.comp7.tooltips.banner_tooltip import BannerTooltip
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.banner_model import BannerModel
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from helpers import dependency, time_utils
from shared_utils import nextTick
from skeletons.gui.game_control import IComp7Controller

def isComp7EntryPointAvailable():
    comp7Ctrl = dependency.instance(IComp7Controller)
    return comp7Ctrl.isEnabled() and not comp7Ctrl.isFrozen() and comp7Ctrl.hasAnySeason()


class Comp7EntryPoint(ResizableEntryPointMeta):

    def isSingle(self, value):
        if self.__view:
            self.__view.setIsSingle(value)

    def _makeInjectView(self):
        self.__view = Comp7EntryPointView(flags=ViewFlags.VIEW)
        return self.__view


class Comp7EntryPointView(ViewImpl, Notifiable):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.comp7.Banner())
        settings.flags = flags
        settings.model = BannerModel()
        super(Comp7EntryPointView, self).__init__(settings)
        self.__isSingle = True

    @property
    def viewModel(self):
        return super(Comp7EntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BannerTooltip() if contentID == R.views.lobby.comp7.tooltips.BannerTooltip() else super(Comp7EntryPointView, self).createToolTipContent(event, contentID)

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateState()

    def _initialize(self, *args, **kwargs):
        super(Comp7EntryPointView, self)._initialize(*args, **kwargs)
        self.viewModel.onOpen += self.__onOpen
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onStatusTick += self.__onStatusTick
        self.__comp7Controller.onComp7ConfigChanged += self.__onConfigChanged
        self.addNotificator(PeriodicNotifier(lambda : time_utils.ONE_MINUTE, self.__updateState, periods=(time_utils.ONE_MINUTE,)))
        self.startNotification()

    def _finalize(self):
        self.viewModel.onOpen -= self.__onOpen
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onStatusTick -= self.__onStatusTick
        self.__comp7Controller.onComp7ConfigChanged -= self.__onConfigChanged
        self.clearNotification()
        super(Comp7EntryPointView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(Comp7EntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def __onStatusUpdated(self, _):
        self.__updateState()

    def __onStatusTick(self):
        self.__updateState()

    def __onConfigChanged(self):
        self.__updateState()

    def __updateState(self):
        if isComp7EntryPointAvailable():
            periodInfo = self.__comp7Controller.getPeriodInfo()
            with self.viewModel.transaction() as tx:
                tx.setIsSingle(self.__isSingle)
                tx.setTimeLeftUntilPrimeTime(periodInfo.primeDelta)
                season = self.__comp7Controller.getCurrentSeason() or self.__comp7Controller.getNextSeason() or self.__comp7Controller.getPreviousSeason()
                comp7_model_helpers.setSeasonInfo(model=tx.season, season=season)
                tx.season.setState(getBannerSeasonState())
        else:
            nextTick(self.destroy)()

    def __onOpen(self):
        self.destroy()
        comp7_prb_helpers.selectComp7()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.COMP7)
