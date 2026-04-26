import { gameType } from './user-type.model';

// Request payloads
export interface RegisterUserPayload {
  name: string;
}

export interface RecommendationsPayload {
  games: gameType[];
}

// Response bodies
export interface RegisterUserResponse {
  id: number;
  name: string;
}

export interface GamesResponse {
  games: gameType[];
}

export interface RecommendationsResponse {
  games: gameType[];
}
