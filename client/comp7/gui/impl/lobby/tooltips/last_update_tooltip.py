# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/last_update_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.last_update_tooltip_model import LastUpdateTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class LastUpdateTooltip(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.comp7.lobby.tooltips.LastUpdateTooltip())
        settings.model = LastUpdateTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(LastUpdateTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LastUpdateTooltip, self).getViewModel()

    def _onLoading(self, description, updateTime=None, *args, **kwargs):
        super(LastUpdateTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setDescription(description)
        self.viewModel.setLeaderboardUpdateTimestamp(updateTime or 0)
