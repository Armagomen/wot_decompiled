# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/season_point_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.season_point_tooltip_model import SeasonPointTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class SeasonPointTooltip(ViewImpl):
    __slots__ = ('__params',)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID=R.views.comp7.lobby.tooltips.SeasonPointTooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = SeasonPointTooltipModel()
        super(SeasonPointTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(SeasonPointTooltip, self).getViewModel()

    def _onLoading(self):
        super(SeasonPointTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setState(self.__params['state'])
            vm.setIgnoreState(self.__params['ignoreState'])
            vm.setSeasonPointExchangeRate(self.__comp7Controller.getYearlyRewards().extra.get('crystal', 0))
