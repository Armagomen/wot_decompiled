# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/hw_single_price_view_model.py
from frameworks.wulf import ViewModel

class HwSinglePriceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HwSinglePriceViewModel, self).__init__(properties=properties, commands=commands)

    def getText(self):
        return self._getString(0)

    def setText(self, value):
        self._setString(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(HwSinglePriceViewModel, self)._initialize()
        self._addStringProperty('text', '')
        self._addNumberProperty('price', 0)
