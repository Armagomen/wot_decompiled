# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/__init__.py
from constants import PREBATTLE_TYPE as _P_TYPE
from constants import PREBATTLE_TYPE_NAMES as _P_NAMES
from constants import QUEUE_TYPE as _Q_TYPE
from constants import QUEUE_TYPE_NAMES as _Q_NAMES
from gui.prb_control.settings import CTRL_ENTITY_TYPE as _C_TYPE
from gui.prb_control.settings import CTRL_ENTITY_TYPE_NAMES as _C_NAMES
from gui.prb_control.storages.epic_storage import EpicStorage
from gui.prb_control.storages.event_battles_storage import EventBattlesStorage
from gui.prb_control.storages.local_storage import LocalStorage, RecentArenaStorage
from gui.prb_control.storages.mapbox_storage import MapboxStorage
from gui.prb_control.storages.maps_training_storage import MapsTrainingStorage
from gui.prb_control.storages.prb_storage import TrainingStorage
from gui.prb_control.storages.ranked_storage import RankedStorage
from gui.prb_control.storages.sandbox_storage import SandboxStorage
from gui.prb_control.storages.stronghold_storage import StrongholdStorage
from gui.prb_control.storages.tournament_storage import TournamentStorage
from gui.shared.system_factory import registerPrbStorage, collectPrbStorage, collectAllStorages
from soft_exception import SoftException

__all__ = ('RECENT_ARENA_STORAGE', 'storage_getter', 'legacy_storage_getter', 'prequeue_storage_getter', 'PrbStorageDecorator', '_makeQueueName')

def _makeUniqueName(ctrlName, entityName):
    return '{}_{}'.format(ctrlName, entityName)


def _makeQueueName(queueType):
    if queueType not in _Q_NAMES:
        raise SoftException('Queue type is invalid {}'.format(queueType))
    return _makeUniqueName(_C_NAMES[_C_TYPE.PREQUEUE], _Q_NAMES[queueType])


def _makeLegacyName(legacyType):
    if legacyType not in _P_TYPE.LEGACY_PREBATTLES:
        raise SoftException('Legacy type is invalid {}'.format(legacyType))
    return _makeUniqueName(_C_NAMES[_C_TYPE.LEGACY], _P_NAMES[legacyType])


RECENT_ARENA_STORAGE = 'recentArenaStorage'
_PRB_STORAGE = {}
registerPrbStorage(RECENT_ARENA_STORAGE, RecentArenaStorage())
registerPrbStorage(_makeLegacyName(_P_TYPE.TRAINING), TrainingStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.SANDBOX), SandboxStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.RANKED), RankedStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.EPIC), EpicStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.EVENT_BATTLES), EventBattlesStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.STRONGHOLD_UNITS), StrongholdStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.TOURNAMENT_UNITS), TournamentStorage())
registerPrbStorage(_makeLegacyName(_P_TYPE.EPIC_TRAINING), TrainingStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.MAPBOX), MapboxStorage())
registerPrbStorage(_makeQueueName(_Q_TYPE.MAPS_TRAINING), MapsTrainingStorage())

class storage_getter(object):

    def __init__(self, name):
        super(storage_getter, self).__init__()
        self.__name = name

    def __call__(self, *args):
        return collectPrbStorage(self.__name)


class legacy_storage_getter(storage_getter):

    def __init__(self, legacyType):
        super(legacy_storage_getter, self).__init__(_makeLegacyName(legacyType))


class prequeue_storage_getter(storage_getter):

    def __init__(self, queueType):
        super(prequeue_storage_getter, self).__init__(_makeQueueName(queueType))


class PrbStorageDecorator(LocalStorage):

    def __init__(self):
        self.__storages = collectAllStorages()

    def init(self):
        for storage in self.__storages:
            storage.init()

    def fini(self):
        for storage in self.__storages:
            storage.fini()

    def swap(self):
        for storage in self.__storages:
            storage.swap()

    def clear(self):
        for storage in self.__storages:
            storage.clear()

    def onAvatarBecomePlayer(self):
        for storage in self.__storages:
            storage.onAvatarBecomePlayer()
