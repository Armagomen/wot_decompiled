# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/banner_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.banner_tooltip_model import BannerTooltipModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers
from comp7.gui.impl.lobby.comp7_helpers.comp7_shared import getBannerSeasonState
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class BannerTooltip(ViewImpl):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID=R.views.comp7.lobby.tooltips.BannerTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = BannerTooltipModel()
        super(BannerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BannerTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__comp7Controller.onStatusUpdated, self.__onStatusUpdated), (self.__comp7Controller.onStatusTick, self.__onStatusTick), (self.__comp7Controller.onComp7RanksConfigChanged, self.__onConfigChanged))

    def _onLoading(self, *args, **kwargs):
        super(BannerTooltip, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def __onStatusUpdated(self, _):
        self.__updateState()

    def __onStatusTick(self):
        self.__updateState()

    def __onConfigChanged(self):
        self.__updateState()

    def __updateState(self):
        periodInfo = self.__comp7Controller.getPeriodInfo()
        with self.viewModel.transaction() as tx:
            tx.setTimeLeftUntilPrimeTime(periodInfo.primeDelta)
            season = self.__comp7Controller.getCurrentSeason() or self.__comp7Controller.getNextSeason() or self.__comp7Controller.getPreviousSeason()
            comp7_model_helpers.setSeasonInfo(model=tx.season, season=season)
            tx.season.setState(getBannerSeasonState())
