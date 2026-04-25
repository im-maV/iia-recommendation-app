import { Injectable, signal } from '@angular/core';
import { gameType, userType } from '@models/user-type.model';

const EMPTY_USER: userType = {} as userType;

@Injectable({ providedIn: 'root' })
export class UserStoreService {
  readonly user = signal<userType>(EMPTY_USER);
  readonly selectedGames = signal<gameType[]>([]);
  readonly recommendedGames = signal<gameType[]>([]);

  reset(): void {
    this.user.set(EMPTY_USER);
    this.selectedGames.set([]);
    this.recommendedGames.set([]);
  }
}
