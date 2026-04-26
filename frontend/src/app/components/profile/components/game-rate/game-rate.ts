import { Component, computed, input, output, signal } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faStar, faArrowRight, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
import { gameType } from '@models/user-type.model';

@Component({
  selector: 'app-game-rate',
  imports: [FontAwesomeModule],
  templateUrl: './game-rate.html',
  styleUrl: './game-rate.scss',
})
export class GameRate {
  readonly icons = { faStar, faArrowRight, faTriangleExclamation };
  readonly STARS = [1, 2, 3, 4, 5] as const;

  readonly selectedGames = input.required<gameType[]>();
  readonly ratingsSubmitted = output<gameType[]>();

  readonly ratings = signal<Record<number, number>>({});

  readonly allRated = computed(() => {
    const currentRatings = this.ratings();
    return this.selectedGames().every((game) => (currentRatings[game.id] ?? 0) > 0);
  });

  getRating(gameId: number): number {
    return this.ratings()[gameId] ?? 0;
  }

  rate(gameId: number, rating: number): void {
    this.ratings.update((current) => ({ ...current, [gameId]: rating }));
  }

  submit(): void {
    if (!this.allRated()) return;
    const ratedGames: gameType[] = this.selectedGames().map((game) => ({
      ...game,
      rating: this.getRating(game.id),
    }));

    this.ratingsSubmitted.emit(ratedGames);
  }
}
