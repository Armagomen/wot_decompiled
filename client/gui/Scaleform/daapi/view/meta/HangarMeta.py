# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarMeta.py
from gui.Scaleform.framework.entities.View import View

class HangarMeta(View):

    def onEscape(self):
        self._printOverrideError('onEscape')

    def showHelpLayout(self):
        self._printOverrideError('showHelpLayout')

    def closeHelpLayout(self):
        self._printOverrideError('closeHelpLayout')

    def hideTeaser(self):
        self._printOverrideError('hideTeaser')

    def onTeaserClick(self):
        self._printOverrideError('onTeaserClick')

    def as_setCarouselEnabledS(self, value):
        return self.flashObject.as_setCarouselEnabled(value) if self._isDAAPIInited() else None

    def as_setupAmmunitionPanelS(self, data):
        return self.flashObject.as_setupAmmunitionPanel(data) if self._isDAAPIInited() else None

    def as_setControlsVisibleS(self, value):
        return self.flashObject.as_setControlsVisible(value) if self._isDAAPIInited() else None

    def as_setComp7ModifiersVisibleS(self, value):
        return self.flashObject.as_setComp7ModifiersVisible(value) if self._isDAAPIInited() else None

    def as_setEventTournamentBannerVisibleS(self, alias, isVisible):
        return self.flashObject.as_setEventTournamentBannerVisible(alias, isVisible) if self._isDAAPIInited() else None

    def as_setPrestigeWidgetVisibleS(self, value):
        return self.flashObject.as_setPrestigeWidgetVisible(value) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_showHelpLayoutS(self):
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None

    def as_show3DSceneTooltipS(self, id, args):
        return self.flashObject.as_show3DSceneTooltip(id, args) if self._isDAAPIInited() else None

    def as_hide3DSceneTooltipS(self):
        return self.flashObject.as_hide3DSceneTooltip() if self._isDAAPIInited() else None

    def as_setCarouselS(self, linkage, alias):
        return self.flashObject.as_setCarousel(linkage, alias) if self._isDAAPIInited() else None

    def as_showTeaserS(self, data):
        return self.flashObject.as_showTeaser(data) if self._isDAAPIInited() else None

    def as_setTeaserTimerS(self, timeLabel):
        return self.flashObject.as_setTeaserTimer(timeLabel) if self._isDAAPIInited() else None

    def as_hideTeaserTimerS(self):
        return self.flashObject.as_hideTeaserTimer() if self._isDAAPIInited() else None

    def as_animateHangarViewsS(self, isShow):
        return self.flashObject.as_animateHangarViews(isShow) if self._isDAAPIInited() else None

    def as_setDQWidgetLayoutS(self, layout):
        return self.flashObject.as_setDQWidgetLayout(layout) if self._isDAAPIInited() else None

    def as_updateCarouselEventEntryStateS(self, isVisible):
        return self.flashObject.as_updateCarouselEventEntryState(isVisible) if self._isDAAPIInited() else None

    def as_updateHangarComponentsS(self, showComponents=None, hideComponents=None):
        return self.flashObject.as_updateHangarComponents(showComponents, hideComponents) if self._isDAAPIInited() else None

    def as_setBattleRoyaleSpaceLoadedS(self, showAnimation):
        return self.flashObject.as_setBattleRoyaleSpaceLoaded(showAnimation) if self._isDAAPIInited() else None

    def as_setComp7SpaceLoadedS(self, isLoaded):
        return self.flashObject.as_setComp7SpaceLoaded(isLoaded) if self._isDAAPIInited() else None
