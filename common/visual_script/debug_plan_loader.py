# File: d (Python 2.7)

from constants import IS_DEVELOPMENT
if IS_DEVELOPMENT:
    import VSE
    from plan_holder import PlanHolder
    import weakref
    from debug_utils import LOG_DEBUG_DEV
    from plan_tags import getAllTags
    
    class DebugPlanHolder(PlanHolder):
        __slots__ = 'contextName'
        
        def __init__(self, plan, state, auto = False):
            super(DebugPlanHolder, self).__init__(plan, state, auto)
            self.contextName = ''


    
    class DebugPlanLoader(object):
        
        def __init__(self):
            self._DebugPlanLoader__contextAll = []
            self._DebugPlanLoader__plans = { }
            self._DebugPlanLoader__tags = getAllTags()

        
        def getContext(self, name):
            for ctx in self._DebugPlanLoader__contextAll:
                if type(ctx()).__name__ == name:
                    return ctx()
            

        
        def regContext(self, context):
            for ctx in self._DebugPlanLoader__contextAll:
                if ctx() == context:
                    break
                    continue
                self._DebugPlanLoader__contextAll.append(weakref.ref(context))
                LOG_DEBUG_DEV('VSContext %s was registered' % type(context).__name__)
                return None

        
        def unregContext(self, context):
            for ctx in self._DebugPlanLoader__contextAll[:]:
                if ctx() == context:
                    self._DebugPlanLoader__contextDestroyed(context)
                    self._DebugPlanLoader__contextAll.remove(ctx)
                    LOG_DEBUG_DEV('VSContext %s was unregistered' % type(context).__name__)
                    break
                    continue

        
        def startPlan(self, planName, contextName, aspect, params = { }):
            if planName in self._DebugPlanLoader__plans:
                self._DebugPlanLoader__plans[planName].start()
                return True
            holder = None(VSE.Plan(), PlanHolder.LOADING, False)
            holder.params = params
            if contextName != '':
                context = self.getContext(contextName)
                if context:
                    holder.plan.setContext(context)
                    holder.contextName = contextName
                else:
                    return False
            holder.load(planName, aspect, self._DebugPlanLoader__tags)
            if holder.isLoaded:
                holder.start()
                self._DebugPlanLoader__plans[planName] = holder
                return True

        
        def stopPlan(self, planName):
            if planName in self._DebugPlanLoader__plans:
                self._DebugPlanLoader__plans[planName].plan.stop()
                del self._DebugPlanLoader__plans[planName]
                return True

        
        def stopAllPlans(self):
            res = True
            for planName in list(self._DebugPlanLoader__plans.keys()):
                res &= self.stopPlan(planName)
            
            return res

        
        def _DebugPlanLoader__contextDestroyed(self, context):
            for planName in list(self._DebugPlanLoader__plans.keys()):
                holder = self._DebugPlanLoader__plans[planName]
                if holder.contextName == type(context).__name__:
                    holder.plan.stop()
                    del self._DebugPlanLoader__plans[planName]
                    continue


    debugPlanLoader = DebugPlanLoader()
