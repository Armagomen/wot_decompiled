# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/collection_price_model.py
from frameworks.wulf import ViewModel

class CollectionPriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(CollectionPriceModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(CollectionPriceModel, self)._initialize()
        self._addNumberProperty('price', 0)
