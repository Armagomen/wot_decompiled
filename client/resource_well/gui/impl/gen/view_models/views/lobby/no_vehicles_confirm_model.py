# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/no_vehicles_confirm_model.py
from frameworks.wulf import ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.vehicle_counter_model import VehicleCounterModel

class NoVehiclesConfirmModel(ViewModel):
    __slots__ = ('showHangar',)

    def __init__(self, properties=1, commands=1):
        super(NoVehiclesConfirmModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleCounter(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleCounterType():
        return VehicleCounterModel

    def _initialize(self):
        super(NoVehiclesConfirmModel, self)._initialize()
        self._addViewModelProperty('vehicleCounter', VehicleCounterModel())
        self.showHangar = self._addCommand('showHangar')
