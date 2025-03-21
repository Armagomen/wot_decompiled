# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/general_rank_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Rank
from frameworks.wulf import ViewModel

class GeneralRankTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(GeneralRankTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return Rank(self._getNumber(0))

    def setRank(self, value):
        self._setNumber(0, value.value)

    def getDivisions(self):
        return self._getString(1)

    def setDivisions(self, value):
        self._setString(1, value)

    def getFrom(self):
        return self._getNumber(2)

    def setFrom(self, value):
        self._setNumber(2, value)

    def getTo(self):
        return self._getNumber(3)

    def setTo(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(GeneralRankTooltipModel, self)._initialize()
        self._addNumberProperty('rank')
        self._addStringProperty('divisions', 'E, D, C, B, A')
        self._addNumberProperty('from', 1000)
        self._addNumberProperty('to', 2000)
