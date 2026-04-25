import { Routes } from '@angular/router';

const loadRegister = () =>
  import('@components/register/register.component').then((m) => m.Register);

const loadProfile = () => import('@components/profile/profile.component').then((m) => m.Profile);

const loadRecommendations = () =>
  import('@components/recommended-games/recommended-games.component').then(
    (m) => m.RecommendedGames,
  );

export const routes: Routes = [
  { path: '', redirectTo: 'users/register', pathMatch: 'full' },
  {
    path: 'users',
    children: [
      { path: '', redirectTo: 'register', pathMatch: 'full' },
      { path: 'register', loadComponent: loadRegister },
      { path: 'profile', loadComponent: loadProfile },
    ],
  },
  { path: 'recommendations', loadComponent: loadRecommendations },
  { path: '**', redirectTo: 'users/register' },
];
