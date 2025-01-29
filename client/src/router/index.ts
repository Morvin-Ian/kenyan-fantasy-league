import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/HomeView.vue"),
    },
    {
      path: "/sign-in",
      name: "sign-in",
      component: () => import("@/views/auth/SignIn.vue"),
    },
    {
      path: "/sign-up",
      name: "sign-up",
      component: () => import("@/views/auth/SignUp.vue"),
    },
    {
      path: "/activate/:uid/:token",
      name: "activation",
      component: () => import("@/views/auth/Activate.vue"),
    },
    {
      path: "/fkl_team",
      name: "team",
      component: () => import("@/views/TeamView.vue"),
    },
    {
      path: "/standings",
      name: "standings",
      component: () => import("@/views/StandingsView.vue"),
    },
    {
      path: "/fixtures",
      name: "fixtures",
      component: () => import("@/views/FixturesView.vue"),
    },
    {
      path: "/leagues",
      name: "leagues",
      component: () => import("@/views/LeaguesView.vue"),
    },
    {
      path: "/profile",
      name: "profile",
      component: () => import("@/views/ProfileView.vue"),
    },
    {
      path: "/password/reset/confirm/:uid/:token",
      name: "reset-password",
      component: () => import("@/views/auth/PasswordResetConfirm.vue"),
    },
    {
      path: "/password/reset/request",
      name: "reset-password-request",
      component: () => import("@/views/auth/PasswordResetRequest.vue"),
    },
  ],
});

export default router;
