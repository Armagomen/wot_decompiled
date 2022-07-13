# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/pre_queue/scheduler.py
from gui.impl.gen import R
from gui.periodic_battles.prb_control.scheduler import PeriodicScheduler
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomScheduler(PeriodicScheduler):
    _RES_ROOT = R.strings.system_messages.funRandom
    _controller = dependency.descriptor(IFunRandomController)
