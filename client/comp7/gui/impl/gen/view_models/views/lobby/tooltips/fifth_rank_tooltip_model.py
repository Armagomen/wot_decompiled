# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/fifth_rank_tooltip_model.py
from frameworks.wulf import ViewModel

class FifthRankTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FifthRankTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFrom(self):
        return self._getNumber(0)

    def setFrom(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(FifthRankTooltipModel, self)._initialize()
        self._addNumberProperty('from', 2000)
