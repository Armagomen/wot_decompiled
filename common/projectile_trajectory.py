# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/projectile_trajectory.py
import BigWorld
import Math

def computeProjectileTrajectory(beginPoint, velocity, gravity, time, epsilon):
    endPoint = beginPoint + velocity.scale(time) + gravity.scale(time * time * 0.5)
    return computeProjectileTrajectoryWithEnd(beginPoint, endPoint, velocity, gravity, epsilon)


def computeProjectileTrajectoryWithEnd(beginPoint, endPoint, velocity, gravity, epsilon):
    checkPoints = []
    stack = [(velocity, beginPoint, endPoint)]
    while len(stack) > 0:
        lastIdx = len(stack) - 1
        v1, p1, p2 = stack[lastIdx]
        del stack[lastIdx]
        delta = p2 - p1
        xzNormal = Math.Vector3(-delta.z, 0.0, delta.x)
        normal = xzNormal * delta
        if abs(normal.y) < epsilon:
            checkPoints.append(p2)
            continue
        normal.normalise()
        extremeTime = normal.dot(v1) / (-gravity.y * normal.y)
        extremePoint = v1.scale(extremeTime) + gravity.scale(extremeTime * extremeTime * 0.5)
        dist = abs(normal.dot(extremePoint))
        if dist > epsilon:
            extremeVelocity = v1 + gravity.scale(extremeTime)
            stack.append((extremeVelocity, p1 + extremePoint, p2))
            stack.append((v1, p1, p1 + extremePoint))
        checkPoints.append(p2)

    return checkPoints


try:
    computeProjectileTrajectory = BigWorld.wg_computeProjectileTrajectory
    computeProjectileTrajectoryWithEnd = BigWorld.wg_computeProjectileTrajectoryWithEnd
except AttributeError:
    pass

def getShotAngles(vehTypeDescr, vehMatrix, point, overrideGunPosition=None, overrideShotIdx=None):
    shot = vehTypeDescr.getShot(overrideShotIdx)
    return BigWorld.getAimingAngles(point, vehMatrix, vehTypeDescr.chassis.hullPosition + vehTypeDescr.hull.turretPositions[0], vehTypeDescr.activeGunShotPosition if overrideGunPosition is None else overrideGunPosition, shot.speed, shot.gravity)
