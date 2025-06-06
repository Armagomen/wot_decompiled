# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/sixth_rank_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.sixth_rank_tooltip_model import SixthRankTooltipModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class SixthRankTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.comp7.lobby.tooltips.SixthRankTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = SixthRankTooltipModel()
        super(SixthRankTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SixthRankTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SixthRankTooltip, self)._initialize(*args, **kwargs)
        comp7_model_helpers.setElitePercentage(self.viewModel)
