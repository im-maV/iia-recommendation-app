import { GamesRated } from './user-type.model';

export interface RegisterUserPayload {
  name: string;
}

export interface RecommendationsPayload {
  games: GamesRated[];
}
