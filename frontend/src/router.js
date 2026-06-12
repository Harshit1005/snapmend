import { createRouter, createWebHistory } from 'vue-router'
import RoleSelection from '@/views/RoleSelection.vue'
import Dashboard from '@/views/Dashboard.vue'
import Assessment from '@/views/Assessment.vue'
import Repairs from '@/views/Repairs.vue'
import AssessmentDetail from '@/views/AssessmentDetail.vue'
import SupervisorDashboard from '@/views/SupervisorDashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'RoleSelection',
      component: RoleSelection,
    },
    {
      path: '/inspector',
      name: 'InspectorDashboard',
      component: Dashboard,
    },
    {
      path: '/supervisor',
      name: 'SupervisorDashboard',
      component: SupervisorDashboard,
    },
    {
      path: '/assessment',
      name: 'Assessment',
      component: Assessment,
    },
    {
      path: '/assessment/:id',
      name: 'AssessmentDetail',
      component: AssessmentDetail,
    },
    {
      path: '/repairs',
      name: 'Repairs',
      component: Repairs,
    },
  ],
})

export default router
