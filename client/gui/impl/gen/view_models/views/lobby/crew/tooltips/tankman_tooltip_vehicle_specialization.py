# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/tankman_tooltip_vehicle_specialization.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class TankmanTooltipVehicleSpecialization(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(TankmanTooltipVehicleSpecialization, self).__init__(properties=properties, commands=commands)

    def getSpecializationLevel(self):
        return self._getNumber(7)

    def setSpecializationLevel(self, value):
        self._setNumber(7, value)

    def getHasPenalty(self):
        return self._getBool(8)

    def setHasPenalty(self, value):
        self._setBool(8, value)

    def getNation(self):
        return self._getString(9)

    def setNation(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(TankmanTooltipVehicleSpecialization, self)._initialize()
        self._addNumberProperty('specializationLevel', 0)
        self._addBoolProperty('hasPenalty', False)
        self._addStringProperty('nation', '')
