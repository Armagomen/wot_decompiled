# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ShotsReceiver.py
import BigWorld
import CGF
import GenericComponents
import Math
import logging
from Event import Event
from cgf_components_common.material_component import MaterialComponent
from cgf_components_common.shots_receiver import ShotsReceiver as Receiver
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_IDS, EFFECT_MATERIAL_INDEXES_BY_NAMES
from cgf_components.on_shot_components import EffectOnShotComponent, SoundOnShotComponent
_logger = logging.getLogger(__name__)
_DIR_UP = Math.Vector3(0.0, 1.0, 0.0)

class ShotsReceiver(BigWorld.DynamicScriptComponent, Receiver):

    def __init__(self):
        super(ShotsReceiver, self).__init__()
        self.onShot = Event()

    def receiveShot(self, hitPoint, hitDir, normal, shotID, effectIndex, matKind, damagedDestructibles):
        if self.entity.gameObject.isValid():
            self.onShot(hitPoint, hitDir, normal, shotID, effectIndex, matKind, damagedDestructibles, self.entity.gameObject.id)


@autoregister(presentInAllWorlds=True)
class ShotReceiverManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, ShotsReceiver)
    def onShotsReceiverAdded(self, gameObject, shotsReceiver):
        shotsReceiver.onShot += self.__onShot

    @onRemovedQuery(CGF.GameObject, ShotsReceiver)
    def onShotsReceiverRemoved(self, gameObject, shotsReceiver):
        shotsReceiver.onShot -= self.__onShot

    def __onShot(self, hitPoint, hitDir, normal, shotID, effectIndex, matKind, damagedDestructibles, gameObjectID):
        effectQuery = CGF.Query(self.spaceID, (CGF.GameObject,
         ShotsReceiver,
         EffectOnShotComponent,
         GenericComponents.TransformComponent))
        soundQuery = CGF.Query(self.spaceID, (CGF.GameObject,
         ShotsReceiver,
         SoundOnShotComponent,
         GenericComponents.TransformComponent))
        explosionQuery = CGF.Query(self.spaceID, (CGF.GameObject, ShotsReceiver, CGF.No(EffectOnShotComponent)))
        normal.normalise()
        shot = {'hitPoint': hitPoint,
         'hitDir': hitDir,
         'normal': normal,
         'shotID': int(shotID),
         'effectIndex': int(effectIndex),
         'matKind': int(matKind),
         'damagedDestructibles': damagedDestructibles}
        for gameObject, _, effectComponent, transform in effectQuery:
            if gameObject.id == gameObjectID:
                self.__processEffect(gameObject, shot, effectComponent.effectPath, transform)

        for gameObject, _, soundComponent, transform in soundQuery:
            if gameObject.id == gameObjectID:
                self.__processSound(gameObject, shot, soundComponent.soundPath, transform)

        for gameObject, _ in explosionQuery:
            if gameObject.id == gameObjectID:
                self.__processExplosion(gameObject, shot)

    def __processExplosion(self, gameObject, shot):
        materialIdx = 0
        if EFFECT_MATERIAL_INDEXES_BY_IDS.has_key(shot['matKind']):
            materialIdx = EFFECT_MATERIAL_INDEXES_BY_IDS[shot['matKind']]
        else:
            material = gameObject.findComponentByType(MaterialComponent)
            if material:
                materialIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES[material.kind]
        BigWorld.player().explodeProjectile(shot['shotID'], shot['effectIndex'], materialIdx, shot['hitPoint'], shot['hitDir'], shot['damagedDestructibles'])

    def __processEffect(self, gameObject, shot, effectPath, transform):
        position, normal = shot['hitPoint'], shot['normal']
        localTransform = transform.worldTransform
        localTransform.invert()
        localPosition = localTransform.applyPoint(position)
        localNormal = localTransform.applyVector(normal)
        localNormal.normalise()
        shotEffectTransform = Math.createVectorRotationMatrix(_DIR_UP, localNormal)
        shotEffectTransform.translation = localPosition
        CGF.loadGameObjectIntoHierarchy(effectPath, gameObject, shotEffectTransform)

    def __processSound(self, gameObject, shot, soundPath, transform):
        position = shot['hitPoint']
        localTransform = transform.worldTransform
        localTransform.invert()
        localPosition = localTransform.applyPoint(position)
        CGF.loadGameObjectIntoHierarchy(soundPath, gameObject, localPosition)
