import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SignIn from '@/views/auth/SignIn.vue'
import SignUp from '@/views/auth/SignUp.vue'
import Activate from '@/views/auth/Activate.vue'
import TeamView from '@/views/TeamView.vue'
import FixturesView from '@/views/FixturesView.vue'
import StandingsView from '@/views/StandingsView.vue'
import LeaguesView from '@/views/LeaguesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/sign-in',
      name: 'sign-in',
      component: SignIn
    },
    {
      path: '/sign-up',
      name: 'sign-up',
      component: SignUp
    },
    {
      path: '/activate/:uid/:token',
      name: 'activation',
      component: Activate
    },
    {
      path: '/fkl_team',
      name: 'team',
      component: TeamView
    },
    {
      path: '/standings',
      name: 'standings',
      component: StandingsView
    },
    {
      path: '/fixtures',
      name: 'fixtures',
      component: FixturesView
    },
    {
      path: '/leagues',
      name: 'leagues',
      component: LeaguesView
    }
  ]
})

export default router
