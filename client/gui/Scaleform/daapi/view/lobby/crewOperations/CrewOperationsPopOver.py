# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/CrewOperationsPopOver.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.CrewOperationsPopOverMeta import CrewOperationsPopOverMeta
from gui.Scaleform.locale.CREW_OPERATIONS import CREW_OPERATIONS
from gui.impl.dialogs.dialogs import showRetrainDialog
from gui.prb_control import prb_getters
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.tankman import TankmanReturn, TankmanUnload
from gui.shared.utils import decorators
from helpers import dependency
from helpers import i18n
from items import tankmen
from skeletons.gui.shared import IItemsCache
OPERATION_RETRAIN = 'retrain'
OPERATION_RETURN = 'return'
OPERATION_DROP_IN_BARRACK = 'dropInBarrack'

class CrewOperationsPopOver(CrewOperationsPopOverMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_ctxData',)

    def __init__(self, ctx):
        super(CrewOperationsPopOver, self).__init__()
        self._ctxData = ctx.get('data')

    def _populate(self):
        super(CrewOperationsPopOver, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitLeft += self.__unitMgrOnUnitLeft
        self.__update()

    def onWindowClose(self):
        self.destroy()

    def _destroy(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitLeft -= self.__unitMgrOnUnitLeft
        super(CrewOperationsPopOver, self)._destroy()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(CrewOperationsPopOver, self)._dispose()

    def invokeOperation(self, operationName):
        if operationName == OPERATION_RETRAIN:
            if self._ctxData:
                tankmenIds = self._ctxData.get('tankmenIds', [])
                vehicleCD = self._ctxData.get('vehicleCD', None)
                showRetrainDialog(tankmenIds, vehicleCD)
        elif operationName == OPERATION_RETURN:
            self.__processReturnCrew()
        else:
            self.__unloadCrew()
        return

    def onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            self.__update()

    def __update(self):
        vehicle = g_currentVehicle.item
        dataForUpdate = {'operationsArray': [self.__getRetrainOperationData(vehicle), self.__getReturnOperationData(vehicle), self.__getDropInBarrackOperationData(vehicle)]}
        self.as_updateS(dataForUpdate)

    def __getRetrainOperationData(self, vehicle):
        crew = vehicle.crew
        if vehicle.isDisabled:
            return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'locked')
        if self.__isNoCrew(crew):
            return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'noCrew')
        return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'alreadyRetrained') if self.__isTopCrewForCurrentVehicle(crew, vehicle) else self.__getInitCrewOperationObject(OPERATION_RETRAIN)

    def __getReturnOperationData(self, vehicle):
        if vehicle.isInBattle:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'vehicleInBattle')
        crew = vehicle.crew
        lastCrewIDs = vehicle.lastCrew
        freeBerths = self.itemsCache.items.freeTankmenBerthsCount()
        tankmenToBarracksCount = 0
        for tankman in crew:
            if tankman[1] is not None:
                tankmenToBarracksCount += 1

        demobilizedMembersCounter = 0
        isCrewAlreadyInCurrentVehicle = True
        if lastCrewIDs is not None:
            for lastTankmenInvID in lastCrewIDs:
                actualLastTankman = self.itemsCache.items.getTankman(lastTankmenInvID)
                if actualLastTankman is not None:
                    if actualLastTankman.isInTank:
                        lastTankmanVehicle = self.itemsCache.items.getVehicle(actualLastTankman.vehicleInvID)
                        if lastTankmanVehicle:
                            if lastTankmanVehicle.isLocked:
                                return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_MEMBERSINBATTLE_TOOLTIP)
                            if lastTankmanVehicle.invID != vehicle.invID:
                                isCrewAlreadyInCurrentVehicle = False
                            elif lastTankmanVehicle.invID == vehicle.invID:
                                tankmenToBarracksCount -= 1
                    else:
                        isCrewAlreadyInCurrentVehicle = False
                        freeBerths += 1
                demobilizedMembersCounter += 1

            if tankmenToBarracksCount > 0 and tankmenToBarracksCount > freeBerths:
                return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_NOSPACE_TOOLTIP)
        else:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'noPrevious')
        if demobilizedMembersCounter > 0 and demobilizedMembersCounter == len(lastCrewIDs):
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'allDemobilized')
        elif isCrewAlreadyInCurrentVehicle:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'alreadyOnPlaces')
        else:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_MEMBERDEMOBILIZED_TOOLTIP, True) if 0 < demobilizedMembersCounter < len(lastCrewIDs) else self.__getInitCrewOperationObject(OPERATION_RETURN)

    def __getDropInBarrackOperationData(self, vehicle):
        crew = vehicle.crew
        if self.__isNoCrew(crew):
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, 'noCrew')
        elif vehicle.isInBattle:
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, None, CREW_OPERATIONS.DROPINBARRACK_WARNING_INBATTLE_TOOLTIP)
        elif self.__isNotEnoughSpaceInBarrack(crew):
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, None, CREW_OPERATIONS.DROPINBARRACK_WARNING_NOSPACE_TOOLTIP)
        else:
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, None, CREW_OPERATIONS.DROPINBARRACK_WARNING_CREWISLOCKED_TOOLTIP) if vehicle.isCrewLocked else self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK)

    def __isTopCrewForCurrentVehicle(self, crew, vehicle):
        for _, tman in crew:
            if tman is not None:
                if tman.efficiencyRoleLevel < tankmen.MAX_SKILL_LEVEL or tman.vehicleNativeDescr.type.compactDescr != vehicle.intCD:
                    return False

        return True

    def __isNoCrew(self, crew):
        for _, tman in crew:
            if tman is not None:
                return False

        return True

    def __isNotEnoughSpaceInBarrack(self, crew):
        berthsNeeded = len([ (role, t) for role, t in crew if t is not None ])
        return 0 < berthsNeeded > self.itemsCache.items.freeTankmenBerthsCount()

    @decorators.adisp_process('crewReturning')
    def __processReturnCrew(self):
        result = yield TankmanReturn(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __getInitCrewOperationObject(self, operationId, errorId=None, warningId='', operationAvailable=False):
        context = '#crew_operations:%s'
        cOpId = context % operationId
        iconPathContext = '../maps/icons/tankmen/crew/%s%s'
        errorText = ''
        btnLabelText = ''
        if errorId:
            errorText = i18n.makeString(cOpId + '/error/' + errorId)
        else:
            btnLabelText = i18n.makeString(cOpId + '/button/label')
        warningInfo = None
        if warningId != '':
            warningInfo = {'operationAvailable': operationAvailable,
             'tooltipId': warningId}
        return {'id': operationId,
         'iconPath': iconPathContext % (operationId, '.png'),
         'title': i18n.makeString(cOpId + '/title'),
         'description': i18n.makeString(cOpId + '/description'),
         'error': errorText,
         'warning': warningInfo,
         'btnLabel': btnLabelText,
         'btnNotificationEnabled': False}

    def __unitMgrOnUnitLeft(self, _, __):
        self._destroy()

    @staticmethod
    @decorators.adisp_process('unloading')
    def __unloadCrew():
        result = yield TankmanUnload(g_currentVehicle.item.invID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
