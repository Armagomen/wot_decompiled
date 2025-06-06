# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/game_control/voiceover_manager.py
from functools import partial
import typing
from account_helpers.settings_core.settings_constants import SOUND
import BigWorld
import SoundGroups
import WWISE
from Event import Event
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from constants import IS_DEVELOPMENT
from helpers import i18n, dependency
from story_mode.skeletons.voiceover_controller import IVoiceoverManager
_UPDATE_PERIOD = 0.1

class VoiceoverManager(IVoiceoverManager):
    __slots__ = ('onSubtitleShow', 'onSubtitleHide', '_currentSound', '_currentSubtitle', '_callbackId', '_currentCtx', '_delay', '_onEndCallbackId', 'onStarted', 'onStopped')

    def __init__(self):
        super(VoiceoverManager, self).__init__()
        self.onSubtitleShow = Event()
        self.onSubtitleHide = Event()
        self.onStarted = Event()
        self.onStopped = Event()
        self._currentSound = None
        self._currentSubtitle = ''
        self._callbackId = None
        self._currentCtx = None
        self._delay = None
        self._onEndCallbackId = None
        return

    def init(self):
        g_playerEvents.onAvatarBecomeNonPlayer += self._onAvatarBecomeNonPlayer

    def fini(self):
        g_playerEvents.onAvatarBecomeNonPlayer -= self._onAvatarBecomeNonPlayer

    @property
    def currentSubtitle(self):
        return self._currentSubtitle

    @property
    def currentCtx(self):
        return self._currentCtx

    @property
    def isPlaying(self):
        return self._currentSound is not None

    def stopVoiceover(self):
        WWISE.WW_removeMarkerListener(self._soundMarkerHandler)
        if self._currentSound is not None:
            self._currentSound.stop()
            self._currentSound = None
            self.onStopped()
        if self._currentSubtitle:
            self._currentSubtitle = ''
            self.onSubtitleHide()
        self._currentCtx = None
        if self._callbackId is not None:
            BigWorld.cancelCallback(self._callbackId)
            self._callbackId = None
        if self._onEndCallbackId is not None:
            BigWorld.cancelCallback(self._onEndCallbackId)
            self._onEndCallbackId = None
        return

    def playVoiceover(self, voiceoverId, ctx=None, delay=None):
        self._delay = delay
        if self._onEndCallbackId is not None:
            BigWorld.cancelCallback(self._onEndCallbackId)
            self._onEndCallbackId = None
        if self.isPlaying:
            self.stopVoiceover()
        self._currentSound = SoundGroups.g_instance.getSound2D(voiceoverId) if voiceoverId else None
        if self._currentSound is not None:
            WWISE.WW_addMarkerListener(self._soundMarkerHandler)
            self._currentCtx = ctx
            self._currentSound.play()
            self.onStarted()
            self._callbackId = BigWorld.callback(_UPDATE_PERIOD, self._update)
        return

    def onDisconnected(self):
        super(VoiceoverManager, self).onDisconnected()
        self.stopVoiceover()

    def onAvatarBecomePlayer(self):
        super(VoiceoverManager, self).onAvatarBecomePlayer()
        self.stopVoiceover()

    def onAccountBecomePlayer(self):
        super(VoiceoverManager, self).onAccountBecomePlayer()
        self.stopVoiceover()

    def _onAvatarBecomeNonPlayer(self):
        self.stopVoiceover()

    def _update(self):
        if self._currentSound is not None and self._currentSound.isPlaying:
            self._callbackId = BigWorld.callback(_UPDATE_PERIOD, self._update)
            return
        else:
            self._callbackId = None
            onEnd = self._currentCtx.get('onEnd') if self._currentCtx else None
            self.stopVoiceover()
            if self._delay is not None:
                self._onEndCallbackId = BigWorld.callback(self._delay, partial(self._onEndEvent, onEnd))
            else:
                self._onEndEvent(onEnd)
            return

    def _onEndEvent(self, onEnd):
        self._delay = None
        self._onEndCallbackId = None
        if callable(onEnd):
            onEnd()
        return

    def _soundMarkerHandler(self, marker):
        if not AccountSettings.getSettings(SOUND.SUBTITLES):
            return
        marker = marker.strip()
        if marker == '#end':
            if self._currentSubtitle:
                self._currentSubtitle = ''
                self.onSubtitleHide()
        elif marker.startswith('#'):
            self._currentSubtitle = i18n.makeString(marker)
            self.onSubtitleShow()


if IS_DEVELOPMENT:

    def debugSubtitle(text=''):
        voiceoverManager = dependency.instance(IVoiceoverManager)
        if text:
            voiceoverManager._currentSubtitle = text
            voiceoverManager.onSubtitleShow()
        else:
            voiceoverManager._currentSubtitle = ''
            voiceoverManager.onSubtitleHide()
