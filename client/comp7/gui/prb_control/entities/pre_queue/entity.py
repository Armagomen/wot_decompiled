# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
import typing
from CurrentVehicle import g_currentVehicle
from comp7.gui.comp7_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from comp7.gui.prb_control.entities.comp7_prb_helpers import Comp7ViewPresenter
from comp7.gui.prb_control.entities.pre_queue.actions_validator import Comp7ActionsValidator
from comp7.gui.prb_control.entities.pre_queue.ctx import Comp7QueueCtx
from comp7.gui.prb_control.entities.pre_queue.permissions import Comp7Permissions
from comp7.gui.prb_control.entities.pre_queue.vehicles_watcher import Comp7VehiclesWatcher
from comp7.gui.prb_control.entities.scheduler import Comp7Scheduler
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from comp7.gui.prb_control.storages.comp7_storage import Comp7Storage

class Comp7EntryPoint(PreQueueEntryPoint):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(Comp7EntryPoint, self).__init__(FUNCTIONAL_FLAG.COMP7, QUEUE_TYPE.COMP7)

    def select(self, ctx, callback=None):
        status, _, _ = self.__comp7Controller.getPrimeTimeStatus()
        if not self.__comp7Controller.isEnabled():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif status in self._getUnavailableStates():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
            return
        else:
            super(Comp7EntryPoint, self).select(ctx, callback)
            return

    @staticmethod
    def _getUnavailableStates():
        return (PrimeTimeStatus.FROZEN,)


class Comp7Entity(PreQueueEntity):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(Comp7Entity, self).__init__(FUNCTIONAL_FLAG.COMP7, QUEUE_TYPE.COMP7, PreQueueSubscriber())
        self.__watcher = None
        self.__introPresenter = Comp7ViewPresenter()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.COMP7)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = Comp7VehiclesWatcher()
        self.__watcher.start()
        self.__introPresenter.init()
        result = super(Comp7Entity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        self.__introPresenter.fini()
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(Comp7Entity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(Comp7Entity, self).leave(ctx, callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name in (PREBATTLE_ACTION_NAME.COMP7,) else super(Comp7Entity, self).doSelectAction(action)

    def getPermissions(self, *_):
        return Comp7Permissions(self.isInQueue())

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(Comp7Entity, self).queue(ctx, callback=callback)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return Comp7QueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return Comp7ActionsValidator(self)

    def _createScheduler(self):
        return Comp7Scheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().AccountComp7Component.enqueueComp7(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the Competitive7x7', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountComp7Component.dequeueComp7()
        LOG_DEBUG('Sends request on dequeuing from the Competitive7x7')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
