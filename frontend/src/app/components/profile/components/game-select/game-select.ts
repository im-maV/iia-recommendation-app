import { Component, computed, input, output, signal } from '@angular/core';
import { faArrowRight, faCheck } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { gameType } from '@models/user-type.model';

@Component({
  selector: 'app-game-select',
  imports: [FontAwesomeModule],
  templateUrl: './game-select.html',
  styleUrl: './game-select.scss',
})
export class GameSelect {
  readonly icons = { faCheck, faArrowRight };
  readonly MAX_SELECTED = 5;

  readonly games = input.required<gameType[]>();
  readonly selectionFinished = output<gameType[]>();

  private readonly selectedMap = signal<Map<number, gameType>>(new Map());

  readonly selectedIds = computed(() => new Set(this.selectedMap().keys()));
  readonly selectedCount = computed(() => this.selectedMap().size);
  readonly canConfirm = computed(() => this.selectedCount() === this.MAX_SELECTED);

  isSelected(gameId: number): boolean {
    return this.selectedIds().has(gameId);
  }

  toggle(game: gameType): void {
    this.selectedMap.update((current) => {
      const next = new Map(current);

      if (next.has(game.id)) {
        next.delete(game.id);
      } else {
        if (next.size >= this.MAX_SELECTED) return current;
        next.set(game.id, game);
      }

      return next;
    });
  }

  confirm(): void {
    if (!this.canConfirm()) return;
    this.selectionFinished.emit([...this.selectedMap().values()]);
  }
}
