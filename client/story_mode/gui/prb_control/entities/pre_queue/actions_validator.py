# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/prb_control/entities/pre_queue/actions_validator.py
from gui.prb_control.entities.base.pre_queue.actions_validator import InQueueValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from helpers import dependency
from story_mode.skeletons.story_mode_controller import IStoryModeController

class StoryModeStateValidator(BaseActionsValidator):

    def _validate(self):
        ctrl = dependency.instance(IStoryModeController)
        return ValidationResult(False) if not ctrl.isEnabled() or ctrl.isSelectedMissionLocked() else super(StoryModeStateValidator, self)._validate()


class StoryModeActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        validators = [StoryModeStateValidator(entity), InQueueValidator(entity)]
        super(StoryModeActionsValidator, self).__init__(entity, validators)
