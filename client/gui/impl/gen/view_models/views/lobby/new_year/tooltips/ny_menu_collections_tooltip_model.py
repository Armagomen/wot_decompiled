# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_menu_collections_tooltip_model.py
from frameworks.wulf import ViewModel

class NyMenuCollectionsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyMenuCollectionsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentToysCount(self):
        return self._getNumber(0)

    def setCurrentToysCount(self, value):
        self._setNumber(0, value)

    def getAllToysCount(self):
        return self._getNumber(1)

    def setAllToysCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyMenuCollectionsTooltipModel, self)._initialize()
        self._addNumberProperty('currentToysCount', 0)
        self._addNumberProperty('allToysCount', 0)
