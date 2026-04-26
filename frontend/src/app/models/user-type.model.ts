export interface userType {
  id: number;
  name: string;
  games: gameType[];
  ratings: {};
}

export interface gameType {
  name: string;
  id: number;
  genre: string;
  perspective: string;
  category: string;
}
