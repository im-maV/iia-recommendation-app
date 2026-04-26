import { Component, computed, inject, signal } from '@angular/core';
import { UserStoreService } from '@services/user-store.service';
import { Router } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faCheck,
  faGamepad,
  faListCheck,
  faRotateLeft,
  faStarHalfStroke,
  faWandMagicSparkles,
} from '@fortawesome/free-solid-svg-icons';
import { BadgeType, SidebarBadge, StepIndex } from '@models/sidebar.model';
import { Sidebar } from '@components/sidebar/sidebar';

@Component({
  selector: 'app-recommended-games',
  imports: [Sidebar, FontAwesomeModule],
  templateUrl: './recommended-games.component.html',
  styleUrl: './recommended-games.component.scss',
})
export class RecommendedGames {
  private userStoreService = inject(UserStoreService);
  private router = inject(Router);

  readonly icons = {
    faGamepad,
    faRotateLeft,
    faCheck,
    faWandMagicSparkles,
    faListCheck,
    faStarHalfStroke,
  };

  readonly user = this.userStoreService.user;

  readonly currentStep = StepIndex.Results;
  readonly sidebarBadge: SidebarBadge = {
    label: 'Recomendações',
    icon: faWandMagicSparkles,
    type: BadgeType.Done,
  };

  restart() {
    this.userStoreService.reset();
    this.router.navigate(['/']);
  }
}
