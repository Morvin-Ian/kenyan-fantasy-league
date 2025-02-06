import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import SignIn from "@/views/auth/SignIn.vue";
import SignUp from "@/views/auth/SignUp.vue";
import Activate from "@/views/auth/Activate.vue";
import TeamView from "@/views/TeamView.vue";
import StandingsView from "@/views/StandingsView.vue";
import FixturesView from "@/views/FixturesView.vue";
import LeaguesView from "@/views/LeaguesView.vue";
import ProfileView from "@/views/ProfileView.vue";
import PasswordResetConfirm from "@/views/auth/PasswordResetConfirm.vue";
import PasswordResetRequest from "@/views/auth/PasswordResetRequest.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/sign-in",
      name: "sign-in",
      component: SignIn,
    },
    {
      path: "/sign-up",
      name: "sign-up",
      component: SignUp,
    },
    {
      path: "/activate/:uid/:token",
      name: "activation",
      component: Activate,
    },
    {
      path: "/fkl_team",
      name: "team",
      component: TeamView,
    },
    {
      path: "/standings",
      name: "standings",
      component: StandingsView,
    },
    {
      path: "/fixtures",
      name: "fixtures",
      component: FixturesView,
    },
    {
      path: "/leagues",
      name: "leagues",
      component: LeaguesView,
    },
    {
      path: "/profile",
      name: "profile",
      component: ProfileView,
    },
    {
      path: "/password/reset/confirm/:uid/:token",
      name: "reset-password",
      component: PasswordResetConfirm,
    },
    {
      path: "/password/reset/request",
      name: "reset-password-request",
      component: PasswordResetRequest,
    },
  ],
});

export default router;
