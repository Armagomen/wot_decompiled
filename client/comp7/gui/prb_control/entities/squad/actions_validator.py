# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/prb_control/entities/squad/actions_validator.py
import typing
from comp7_common.comp7_constants import BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitSlotsValidator, CommanderValidator, UnitPlayerValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller, IPlatoonController
from gui.periodic_battles.models import PrimeTimeStatus
from constants import IS_DEVELOPMENT
if typing.TYPE_CHECKING:
    from gui.prb_control.items import PlayerUnitInfo

class _Comp7VehiclesValidator(SquadVehiclesValidator):
    _BATTLE_MODE_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7


class _UnitSlotsValidator(UnitSlotsValidator):

    def _validate(self):
        stats = self._entity.getStats()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_NOT_FULL) if stats.freeSlotsCount > 0 else super(_UnitSlotsValidator, self)._validate()


class _PrimeTimeValidator(CommanderValidator):

    def _validate(self):
        status, _, _ = dependency.instance(IComp7Controller).getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(_PrimeTimeValidator, self)._validate()


class _Comp7PlayerValidator(UnitPlayerValidator):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def _validate(self):
        if self.__comp7Ctrl.isBanned:
            return ValidationResult(False, UNIT_RESTRICTION.BAN_IS_SET, None)
        else:
            ranks = self.__getPlayersRanks()
            return ValidationResult(False, UNIT_RESTRICTION.RANK_RESTRICTION, None) if ranks and max(ranks) - min(ranks) > self.__comp7Ctrl.getPlatoonRankRestriction() else super(_Comp7PlayerValidator, self)._validate()

    def __getPlayersRanks(self):
        playersRanks = []
        for slotData in self.__platoonCtrl.getPlatoonSlotsData():
            playerData = slotData.get('player')
            if playerData is None:
                continue
            comp7EnqueueData = playerData.get('extraData', {}).get('comp7EnqueueData', {})
            playersRanks.append(comp7EnqueueData.get('rank', 0))

        return playersRanks


class _Comp7ModeStatusValidator(BaseActionsValidator):

    def _validate(self):
        if self._entity.isCommander():
            for pInfo in self._entity.getMembers().itervalues():
                if self.__isModeOfflineForPlayer(pInfo):
                    return ValidationResult(False, UNIT_RESTRICTION.MODE_OFFLINE)

        else:
            pInfo = self._entity.getPlayerInfo()
            if self.__isModeOfflineForPlayer(pInfo):
                return ValidationResult(False, UNIT_RESTRICTION.MODE_OFFLINE)
        return super(_Comp7ModeStatusValidator, self)._validate()

    @staticmethod
    def __isModeOfflineForPlayer(pInfo):
        comp7EnqueueData = pInfo.extraData.get('comp7EnqueueData', {})
        isOnline = bool(comp7EnqueueData.get('isOnline', 0))
        return not isOnline


class _Comp7SlotValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class Comp7SquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        validators = [_Comp7VehiclesValidator(entity), _PrimeTimeValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)

    def _createSlotsValidator(self, entity):
        baseValidator = super(Comp7SquadActionsValidator, self)._createSlotsValidator(entity)
        validators = [baseValidator, _Comp7SlotValidator(entity)]
        if not IS_DEVELOPMENT:
            validators.append(_UnitSlotsValidator(entity))
        return ActionsValidatorComposite(entity, validators=validators)

    def _createPlayerValidator(self, entity):
        validators = [_Comp7PlayerValidator(entity), _Comp7ModeStatusValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)
