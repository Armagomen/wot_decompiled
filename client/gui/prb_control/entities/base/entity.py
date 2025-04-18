# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/entity.py
import typing
from adisp import adisp_process
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.entities.base.actions_validator import IActionsValidator
from gui.prb_control.entities.base.actions_validator import NotSupportedActionsValidator, BaseActionsValidator
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.prb_getters import getQueueTypeFromPrbEntity
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.shared.utils.listeners_collection import IListenersCollection
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.ctx import PrbAction, PrbCtrlRequestCtx
    from gui.prb_control.entities.base.cooldown import PrbCooldownManager
    from gui.Scaleform.daapi.view.dialogs import IDialogMeta

class PrbFunctionalFlags(object):
    __slots__ = ('_entityFlags', '_modeFlags')

    def __init__(self, entityFlags, modeFlags, **kwargs):
        super(PrbFunctionalFlags, self).__init__()
        self._entityFlags = entityFlags
        self._modeFlags = modeFlags

    def getModeFlags(self):
        return self._modeFlags

    def getEntityFlags(self):
        return self._entityFlags

    def getFunctionalFlags(self):
        return self._modeFlags | self._entityFlags


class BasePrbEntryPoint(PrbFunctionalFlags):

    def isVisualOnly(self):
        return False

    def makeDefCtx(self):
        return None

    def create(self, ctx, callback=None):
        pass

    def canCreate(self):
        return True

    def join(self, ctx, callback=None):
        pass

    def canJoin(self):
        return True

    def select(self, ctx, callback=None):
        pass

    def setExtData(self, extData):
        pass

    def setAccountsToInvite(self, accountsToInvite):
        pass

    def setKeepCurrentView(self, keepCurrentView):
        pass

    def configure(self, action):
        self.setAccountsToInvite(action.accountsToInvite)
        self.setExtData(action.extData)


class BasePrbEntity(IActionsValidator, PrbFunctionalFlags):

    def __init__(self, entityFlags, modeFlags):
        super(BasePrbEntity, self).__init__(entityFlags=entityFlags, modeFlags=modeFlags)
        self._actionsValidator = self._createActionsValidator()
        self._scheduler = self._createScheduler()
        self._isActive = False
        self._cooldown = self._createCooldownManager()
        self._previous = None
        return

    def init(self, **kwargs):
        self._scheduler.init()
        self._isActive = True
        self._goToHangar()
        return FUNCTIONAL_FLAG.UNDEFINED

    def fini(self, **kwargs):
        self._scheduler.fini()
        self._isActive = False
        self._previous = None
        return FUNCTIONAL_FLAG.UNDEFINED

    def invalidate(self):
        pass

    def restore(self):
        pass

    def rejoin(self):
        pass

    def canSwitch(self, ctx):
        flags = self.getModeFlags()
        return ctx is not None and flags & FUNCTIONAL_FLAG.MODES_BITMASK > 0 and ctx.hasFlags(flags)

    def isActive(self):
        return self._isActive

    def isPlayerJoined(self, ctx):
        return False

    def canInvite(self, prbType):
        return True

    def isInQueue(self):
        return False

    def canKeepMode(self):
        return True

    def resetPlayerState(self):
        pass

    def canPlayerDoAction(self):
        return self._actionsValidator.canPlayerDoAction() or ValidationResult()

    def doAction(self, action=None):
        return False

    def doSelectAction(self, action):
        return SelectResult()

    def showGUI(self, ctx=None):
        return False

    def getConfirmDialogMeta(self, ctx):
        return None

    def showDialog(self, meta, callback, parent=None):
        self.__showDefaultDialog(meta, callback, parent=parent)

    def getID(self):
        pass

    def getCtrlType(self):
        return CTRL_ENTITY_TYPE.UNKNOWN

    def getEntityType(self):
        pass

    def getIntroType(self):
        pass

    def getRequestCtx(self):
        return None

    def getQueueType(self):
        return QUEUE_TYPE.UNKNOWN

    def setPreviousEntity(self, entity):
        self._previous = entity

    def hasLockedState(self):
        return False

    def getPermissions(self, pID=None, **kwargs):
        return IPrbPermissions()

    def isCommander(self, dbID=None):
        return False

    def leave(self, ctx, callback=None):
        pass

    def request(self, ctx, callback=None):
        pass

    def isInCoolDown(self, requestType):
        return self._cooldown and self._cooldown.isInProcess(requestType)

    def setCoolDown(self, requestType, coolDown):
        if self._cooldown:
            self._cooldown.process(requestType, coolDown=coolDown)

    def resetCoolDown(self, requestType):
        if self._cooldown:
            self._cooldown.reset(requestType)

    def canDoActionWithoutVehicle(self):
        return False

    def _createActionsValidator(self):
        return BaseActionsValidator(self)

    def _createScheduler(self):
        return BaseScheduler(self)

    def _createCooldownManager(self):
        return None

    def _goToHangar(self):
        if getQueueTypeFromPrbEntity(self) == getQueueTypeFromPrbEntity(self._previous) or self.isInQueue():
            return
        g_eventDispatcher.loadHangar()

    @adisp_process
    def __showDefaultDialog(self, meta, callback, parent=None):
        from gui import DialogsInterface
        result = yield DialogsInterface.showDialog(meta, parent=parent)
        if callback is not None:
            callback(result)
        return


class NotSupportedEntryPoint(BasePrbEntryPoint):

    def __init__(self):
        super(NotSupportedEntryPoint, self).__init__(entityFlags=FUNCTIONAL_FLAG.UNDEFINED, modeFlags=FUNCTIONAL_FLAG.UNDEFINED)

    def create(self, ctx, callback=None):
        LOG_ERROR('NotSupportedEntry.create', ctx)

    def join(self, ctx, callback=None):
        LOG_ERROR('NotSupportedEntry.join', ctx)


class NotSupportedEntity(BasePrbEntity, IListenersCollection):

    def __init__(self):
        super(NotSupportedEntity, self).__init__(entityFlags=FUNCTIONAL_FLAG.UNDEFINED, modeFlags=FUNCTIONAL_FLAG.UNDEFINED)

    def _createActionsValidator(self):
        return NotSupportedActionsValidator()

    def _goToHangar(self):
        pass
