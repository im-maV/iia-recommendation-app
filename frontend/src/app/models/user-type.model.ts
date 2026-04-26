export interface userType {
  id: number;
  name: string;
  games: GamesRated[];
}

export interface gameType {
  name: string;
  id: number;
  genre: string;
  perspective: string;
  category: string;
}

export interface GamesRated extends gameType {
  rating: number;
  similarity_score?: number;
}
