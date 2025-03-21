# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/recruit_window/recruit_content.py
import logging
import Event
import constants
from gui import GUI_NATIONS
from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog_utils import getSortedItems
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.drop_down_item_view_model import DropDownItemViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.recruit_content_view_model import RecruitContentViewModel, DropDownState
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.vehicle_item_view_model import VehicleItemViewModel
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.utils.functions import replaceHyphenToUnderscore, capitalizeText
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import vehicles
from items.components.skills_constants import ORDERED_ROLES
from nations import INDICES
from skeletons.gui.shared import IItemsCache
NO_DATA_VALUE = '-1'
FIRST_ELEMENT = 0
_logger = logging.getLogger(__name__)

class RecruitContent(object):
    __slots__ = ('__viewModel', '__selectedNationID', '__selectedNation', '__selectedVehType', '__selectedVehicle', '__selectedSpecialization', 'onRecruitContentChanged', '__isFemale', '__predefinedNations', '__predefinedRoles', '__vehIntCD', '__slotSpecialization', '__isSlotChanged')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, predefinedData, model=None):
        super(RecruitContent, self).__init__()
        self.__viewModel = model
        self.__selectedNation = NO_DATA_VALUE
        self.__selectedNationID = None
        self.__selectedVehType = NO_DATA_VALUE
        self.__selectedVehicle = NO_DATA_VALUE
        self.__selectedSpecialization = NO_DATA_VALUE
        self.onRecruitContentChanged = Event.Event()
        self.__isFemale = None
        self.__predefinedNations = None
        self.__predefinedRoles = None
        self.__vehIntCD = None
        self.__slotSpecialization = None
        self.__isSlotChanged = False
        self.__processPredefinedData(predefinedData)
        return

    @property
    def viewModel(self):
        return self.__viewModel

    def subscribe(self):
        self.viewModel.onNationChange += self.__onNationChange
        self.viewModel.onVehTypeChange += self.__onVehTypeChange
        self.viewModel.onVehicleChange += self.__onVehicleChange
        self.viewModel.onSpecializationChange += self.__onSpecializationChange

    def unsubscribe(self):
        self.viewModel.onSpecializationChange -= self.__onSpecializationChange
        self.viewModel.onVehicleChange -= self.__onVehicleChange
        self.viewModel.onVehTypeChange -= self.__onVehTypeChange
        self.viewModel.onNationChange -= self.__onNationChange

    def onLoading(self):
        self.__updateModelAndFireCahangedEvent()

    def __fillModel(self):
        if self.__vehIntCD is not None:
            self.__isSlotChanged = int(self.__selectedVehicle) != self.__vehIntCD or self.__slotSpecialization != self.__selectedSpecialization
        with self.viewModel.transaction() as tx:
            tx.setIsSlotChanged(self.__isSlotChanged)
            self.__fillNations()
            self.__fillVehTypes()
            self.__fillVehicles()
            self.__fillRoles()
            self.__updateSelectedValues()
            self.__updateDropDownsStates()
        return

    def __processPredefinedData(self, predefinedData):
        self.__isFemale = predefinedData.get('isFemale', False)
        slotToUnpack = predefinedData.get('slotToUnpack')
        if slotToUnpack != -1:
            vehicle = predefinedData.get('predefinedVehicle')
            self.__vehIntCD = vehicle.intCD
            self.__selectedVehicle = vehicle.intCD
            self.__selectedVehType = vehicle.type
            self.__selectedNation = vehicle.nationName
            self.__selectedNationID = vehicle.nationID
            self.__selectedSpecialization = vehicle.descriptor.type.crewRoles[slotToUnpack][FIRST_ELEMENT]
            self.__slotSpecialization = self.__selectedSpecialization
        predefinedNations = predefinedData.get('predefinedNations')
        if predefinedNations:
            self.__predefinedNations = predefinedNations
            self.__selectedNation = self.__choosePredefined(self.__predefinedNations, self.__selectedNation)
            self.__selectedNationID = INDICES.get(self.__selectedNation) if self.__selectedNation else None
        predefinedRoles = predefinedData.get('predefinedRoles')
        if predefinedRoles:
            self.__predefinedRoles = predefinedRoles
            self.__selectedSpecialization = self.__choosePredefined(self.__predefinedRoles, self.__selectedSpecialization)
        return

    def __fillNations(self):
        nations = self.viewModel.getNations()
        nations.clear()
        nationsList = getSortedItems(self.__getNationsList(), GUI_NATIONS)
        for name in nationsList:
            model = DropDownItemViewModel()
            model.setId(name)
            model.setLabel(backport.text(R.strings.nations.dyn(name)()))
            nations.addViewModel(model)

    def __getNationsList(self):
        filteredNations = set(GUI_NATIONS)
        if self.__predefinedNations:
            filteredNations = filteredNations.intersection(set(self.__predefinedNations))
        return list(filteredNations)

    def __fillVehTypes(self):
        vehTypes = self.viewModel.getVehTypes()
        vehTypes.clear()
        vehTypeList = getSortedItems(self.__getVehTypeList(), VEHICLE_TYPES_ORDER)
        for name in vehTypeList:
            model = DropDownItemViewModel()
            model.setId(name)
            model.setLabel(capitalizeText(backport.text(R.strings.menu.classes.dyn(replaceHyphenToUnderscore(name))())))
            vehTypes.addViewModel(model)

    def __getVehTypeList(self):
        nationVehTypes = self._itemsCache.items.getVehicles(self.__getClassesCriteria(self.__selectedNationID)).values()
        filteredVehTypes = set((v.type for v in nationVehTypes))
        if self.__predefinedRoles:
            vehTypesByRole = set((v.type for v in nationVehTypes if set(self.__predefinedRoles).intersection(set((r[FIRST_ELEMENT] for r in v.descriptor.type.crewRoles)))))
            filteredVehTypes = filteredVehTypes.intersection(vehTypesByRole)
            if not filteredVehTypes and self.__selectedNation != NO_DATA_VALUE:
                _logger.warning("Couldn't get vehTypes intersections with predefinedRoles: %s Check Token settings", self.__predefinedRoles)
        return list(filteredVehTypes)

    def __fillVehicles(self):
        vehs = self.viewModel.getVehicles()
        vehs.clear()
        nationVehicleList = self.__getVehicleList()
        for intCD, vehicle in nationVehicleList:
            model = VehicleItemViewModel()
            model.setId(intCD)
            model.setName(vehicle.descriptor.type.shortUserString)
            model.setType(replaceHyphenToUnderscore(vehicle.type))
            model.setIsElite(vehicle.isPremium)
            model.setIsIGR(vehicle.isPremiumIGR)
            vehs.addViewModel(model)

    def __getVehicleList(self):
        vehiclesCriteria = self.__getVehicleTypeCriteria(self.__selectedNationID, self.__selectedVehType)
        vehiclesByNation = self._itemsCache.items.getVehicles(vehiclesCriteria).items()
        filteredVehicles = set(vehiclesByNation)
        if self.__predefinedRoles:
            vehiclesByRole = set((i for i in vehiclesByNation if set(self.__predefinedRoles).intersection(set((r[FIRST_ELEMENT] for r in i[1].descriptor.type.crewRoles)))))
            filteredVehicles = filteredVehicles.intersection(vehiclesByRole)
            if not filteredVehicles and self.__selectedVehType != NO_DATA_VALUE:
                _logger.warning("Couldn't get vehicles intersections with predefinedRoles: %s Check Token settings", self.__predefinedRoles)
        return sorted(filteredVehicles, key=lambda x: (x[1].level, x[1].shortUserName))

    def __fillRoles(self):
        specializations = self.viewModel.getSpecializations()
        specializations.clear()
        rolesList = getSortedItems(self.__getRolesList(), ORDERED_ROLES)
        for name in rolesList:
            model = DropDownItemViewModel()
            model.setId(name)
            if self.__isFemale:
                model.setLabel(backport.text(R.strings.item_types.tankman.roles.female.dyn(name)()))
            else:
                model.setLabel(backport.text(R.strings.item_types.tankman.roles.dyn(name)()))
            specializations.addViewModel(model)

    def __getRolesList(self):
        _, _, vehTypeID = vehicles.parseIntCompactDescr(int(self.__selectedVehicle))
        modulesAll = self._itemsCache.items.getVehicles(self.__getRoleCriteria(self.__selectedNationID, self.__selectedVehType, vehTypeID)).values()
        filteredRoles = set((r[FIRST_ELEMENT] for v in modulesAll for r in v.descriptor.type.crewRoles))
        if self.__predefinedRoles:
            filteredRoles = filteredRoles.intersection(set(self.__predefinedRoles))
            if not filteredRoles:
                return list(self.__predefinedRoles)
        return list(filteredRoles)

    def __updateModelAndFireCahangedEvent(self):
        self.__fillModel()
        self.onRecruitContentChanged(self.__selectedNationID, self.__selectedVehType, self.__selectedVehicle, self.__selectedSpecialization, self.__isSlotChanged)

    def __onNationChange(self, args):
        selectedId = self.__getIdFromArgs(args)
        if not self.__isSingleValue(self.__predefinedRoles):
            self.__selectedSpecialization = NO_DATA_VALUE
        if selectedId is not None and selectedId != NO_DATA_VALUE:
            if self.__isSingleValue(self.__predefinedNations):
                self.__selectedNation = self.__predefinedNations[FIRST_ELEMENT]
                self.__selectedNationID = INDICES.get(self.__predefinedNations[FIRST_ELEMENT])
            else:
                self.__selectedNation = selectedId
                self.__selectedNationID = INDICES.get(selectedId)
        else:
            self.__selectedNation = NO_DATA_VALUE
            self.__selectedNationID = None
        self.__selectedVehType = NO_DATA_VALUE
        self.__selectedVehicle = NO_DATA_VALUE
        self.__updateModelAndFireCahangedEvent()
        return

    def __onVehTypeChange(self, args):
        selectedId = self.__getIdFromArgs(args)
        if selectedId is not None and selectedId != NO_DATA_VALUE:
            self.__selectedVehType = selectedId
            self.__selectedVehicle = NO_DATA_VALUE
            if not self.__isSingleValue(self.__predefinedRoles):
                self.__selectedSpecialization = NO_DATA_VALUE
        else:
            self.__selectedVehType = NO_DATA_VALUE
            self.__selectedVehicle = NO_DATA_VALUE
            if not self.__isSingleValue(self.__predefinedRoles):
                self.__selectedSpecialization = NO_DATA_VALUE
        self.__updateModelAndFireCahangedEvent()
        return

    def __onVehicleChange(self, args):
        selectedId = self.__getIdFromArgs(args)
        if selectedId is not None and selectedId != NO_DATA_VALUE:
            self.__selectedVehicle = selectedId
            if not self.__isSingleValue(self.__predefinedRoles):
                self.__selectedSpecialization = NO_DATA_VALUE
        else:
            self.__selectedVehicle = NO_DATA_VALUE
            if not self.__isSingleValue(self.__predefinedRoles):
                self.__selectedSpecialization = NO_DATA_VALUE
        self.__updateModelAndFireCahangedEvent()
        return

    def __onSpecializationChange(self, args):
        selectedId = self.__getIdFromArgs(args)
        if selectedId is not None:
            self.__selectedSpecialization = selectedId
        self.__updateModelAndFireCahangedEvent()
        return

    def __getIdFromArgs(self, args=None):
        if args is None:
            return
        else:
            selectedId = args.get('id', None)
            return selectedId

    def __getDropDownState(self, isPredefined, isPrevSelected):
        if isPredefined:
            return DropDownState.LOCKED
        return DropDownState.NORMAL if isPrevSelected else DropDownState.DISABLED

    def __updateDropDownsStates(self):
        self.viewModel.setNationState(self.__getDropDownState(self.__isSingleValue(self.__predefinedNations), True))
        self.viewModel.setVehTypeState(self.__getDropDownState(False, self.__selectedNation != NO_DATA_VALUE))
        self.viewModel.setVehicleState(self.__getDropDownState(False, self.__selectedVehType != NO_DATA_VALUE))
        self.viewModel.setSpecializationState(self.__getDropDownState(self.__isSingleValue(self.__predefinedRoles), self.__selectedVehicle != NO_DATA_VALUE))

    def __updateSelectedValues(self):
        self.viewModel.setSelectedNation(str(self.__selectedNation))
        self.viewModel.setSelectedVehType(str(self.__selectedVehType))
        self.viewModel.setSelectedVehicle(str(self.__selectedVehicle))
        self.viewModel.setSelectedSpecialization(str(self.__selectedSpecialization))

    def __isSingleValue(self, lst):
        return lst is not None and len(lst) == 1

    def __choosePredefined(self, predefinedList, defaultValue):
        return predefinedList[0] if len(predefinedList) == 1 else defaultValue

    def __getNationsCriteria(self):
        rqc = REQ_CRITERIA
        criteria = ~(~rqc.UNLOCKED | ~rqc.COLLECTIBLE)
        criteria |= ~rqc.VEHICLE.OBSERVER
        criteria |= ~rqc.VEHICLE.BATTLE_ROYALE
        criteria |= ~rqc.VEHICLE.MAPS_TRAINING
        criteria |= ~rqc.VEHICLE.EVENT_BATTLE
        criteria |= ~rqc.VEHICLE.MODE_HIDDEN
        return criteria

    def __getClassesCriteria(self, nationID):
        maxResearchedLevel = self._itemsCache.items.stats.getMaxResearchedLevel(nationID)
        criteria = self.__getNationsCriteria() | REQ_CRITERIA.NATIONS([nationID])
        criteria |= ~(REQ_CRITERIA.COLLECTIBLE | ~REQ_CRITERIA.VEHICLE.LEVELS(range(1, maxResearchedLevel + 1)) | ~REQ_CRITERIA.INVENTORY)
        criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
        return criteria

    def __getVehicleTypeCriteria(self, nationID, vclass):
        criteria = self.__getClassesCriteria(nationID) | REQ_CRITERIA.VEHICLE.CLASSES([vclass])
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
        if not constants.IS_IGR_ENABLED:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if constants.IS_DEVELOPMENT:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_BOT
        return criteria

    def __getRoleCriteria(self, nationID, vclass, typeID):
        return self.__getVehicleTypeCriteria(nationID, vclass) | REQ_CRITERIA.INNATION_IDS([typeID])
