# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/markers2d/manager.py
from comp7.gui.Scaleform.daapi.view.battle.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.points_of_interest import markers2d as poi_plugins

class Comp7MarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(Comp7MarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = plugins.Comp7VehicleMarkerPlugin
        setup['settings'] = plugins.Comp7SettingsPlugin
        setup['pointsOfInterest'] = poi_plugins.PointsOfInterestPlugin
        return setup
