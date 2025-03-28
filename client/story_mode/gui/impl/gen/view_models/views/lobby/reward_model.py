# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/reward_model.py
from frameworks.wulf import ViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.icon_model import IconModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def icon(self):
        return self._getViewModel(0)

    @staticmethod
    def getIconType():
        return IconModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getString(2)

    def setValue(self, value):
        self._setString(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def getTooltipContentId(self):
        return self._getString(4)

    def setTooltipContentId(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addViewModelProperty('icon', IconModel())
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
