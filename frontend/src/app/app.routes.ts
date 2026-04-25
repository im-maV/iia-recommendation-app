import { Routes } from '@angular/router';
import { Register } from './components/register/register';
import { Profile } from './components/profile/profile';
import { RecommendedGames } from './components/recommended-games/recommended-games';

export const routes: Routes = [{
    path: "",
    redirectTo: "users/register",
    pathMatch: "full"
  },
  {
    path: "users",
    children: [
      {
        path: "register",
        component: Register
      },
      {
        path: "profile",
        component: Profile
      }
    ]
  },
  {
    path: "recommendations",
    component: RecommendedGames
  },
  {
    path: "**",
    redirectTo: "users/register"
  },
];
