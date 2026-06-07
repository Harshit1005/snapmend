import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Assessment from '@/views/Assessment.vue'
import Repairs from '@/views/Repairs.vue'
import AssessmentDetail from '@/views/AssessmentDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard,
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
