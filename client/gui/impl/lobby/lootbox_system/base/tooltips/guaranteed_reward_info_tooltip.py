# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/tooltips/guaranteed_reward_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.guaranteed_reward_info_tooltip_view_model import GuaranteedRewardInfoTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController

class GuaranteedRewardInfoTooltip(ViewImpl):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, category, eventName):
        settings = ViewSettings(R.views.lobby.lootbox_system.tooltips.GuaranteedRewardInfoTooltip())
        settings.model = GuaranteedRewardInfoTooltipViewModel()
        super(GuaranteedRewardInfoTooltip, self).__init__(settings)
        self.__category = category
        self.__eventName = eventName

    @property
    def viewModel(self):
        return super(GuaranteedRewardInfoTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(GuaranteedRewardInfoTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            vmTx.setGuaranteedFrequency(self.__lootBoxes.getBoxInfoByCategory(self.__category).get('limit', 0))
            vmTx.setEventName(self.__eventName)
