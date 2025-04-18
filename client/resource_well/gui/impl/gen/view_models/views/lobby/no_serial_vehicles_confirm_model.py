# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/no_serial_vehicles_confirm_model.py
from frameworks.wulf import ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.vehicle_counter_model import VehicleCounterModel

class NoSerialVehiclesConfirmModel(ViewModel):
    __slots__ = ('confirm', 'cancel', 'close')

    def __init__(self, properties=2, commands=3):
        super(NoSerialVehiclesConfirmModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleCounter(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleCounterType():
        return VehicleCounterModel

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NoSerialVehiclesConfirmModel, self)._initialize()
        self._addViewModelProperty('vehicleCounter', VehicleCounterModel())
        self._addStringProperty('vehicleName', '')
        self.confirm = self._addCommand('confirm')
        self.cancel = self._addCommand('cancel')
        self.close = self._addCommand('close')
