import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { UserStoreService } from '@services/user-store.service';
import { APIService } from '@services/api.service';
import { GameSelect } from './components/game-select/game-select';
import { GameRate } from './components/game-rate/game-rate';
import { Sidebar } from '@components/sidebar/sidebar';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faGamepad,
  faListCheck,
  faStarHalfStroke,
  faCheck,
  faWandMagicSparkles,
} from '@fortawesome/free-solid-svg-icons';
import { BadgeType, SidebarBadge, StepIndex } from '@models/sidebar.model';
import { gameType } from '@models/user-type.model';

type ProfilePhase = 'select' | 'rate';

interface SidebarConfig {
  sub: string;
  badge: SidebarBadge;
  currentStep: StepIndex;
}

const SIDEBAR_CONFIG: Record<ProfilePhase, SidebarConfig> = {
  select: {
    sub: 'Escolha 5 jogos que você já jogou ou conhece.',
    badge: { label: 'Seleção', icon: faListCheck, type: BadgeType.Select },
    currentStep: StepIndex.Select,
  },
  rate: {
    sub: 'Avalie os jogos selecionados para calibrar suas recomendações.',
    badge: { label: 'Avaliação', icon: faStarHalfStroke, type: BadgeType.Rate },
    currentStep: StepIndex.Rate,
  },
};

@Component({
  selector: 'app-profile',
  imports: [GameSelect, GameRate, Sidebar, FontAwesomeModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss',
})
export class Profile implements OnInit {
  private readonly userStoreService = inject(UserStoreService);
  private readonly apiService = inject(APIService);
  private readonly router = inject(Router);

  readonly icons = { faGamepad, faListCheck, faStarHalfStroke, faCheck, faWandMagicSparkles };

  readonly user = this.userStoreService.user;

  readonly allGames = signal<gameType[]>([]);
  readonly randomGames = signal<gameType[]>([]);
  readonly finalSelectedGames = signal<gameType[]>([]);
  readonly currentPhase = signal<ProfilePhase>('select');
  readonly loading = signal(false);

  readonly sidebarConfig = computed<SidebarConfig>(() => SIDEBAR_CONFIG[this.currentPhase()]);

  ngOnInit(): void {
    this.getGames();
  }

  onSelectionFinished(games: gameType[]): void {
    this.finalSelectedGames.set(games);
    this.currentPhase.set('rate');
  }

  onRatingsSubmitted(ratedGames: gameType[]): void {
    this.loading.set(true);

    this.apiService.getRecommendations({ games: ratedGames }).subscribe({
      next: ({ body }) => {
        if (!body) {
          console.error('[Profile] Resposta sem body');
          return;
        }
        this.userStoreService.user.set({ ...this.user(), games: body.games });
        this.router.navigate(['recommendations']);
      },
      error: (err: unknown) => {
        console.error('[Profile] Erro ao gerar recomendações:', err);
        this.loading.set(false);
      },
      complete: () => this.loading.set(false),
    });
  }

  private getGames(): void {
    this.apiService.getGames().subscribe({
      next: ({ body }) => {
        if (!body) {
          console.error('[Profile] Resposta sem body');
          return;
        }
        this.allGames.set(body);
        this.randomGames.set(this.pickRandom(body, 10));
      },
      error: (err: unknown) => {
        console.error('[Profile] Erro ao carregar jogos:', err);
      },
    });
  }

  private pickRandom<T>(arr: T[], count: number): T[] {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled.slice(0, count);
  }
}
