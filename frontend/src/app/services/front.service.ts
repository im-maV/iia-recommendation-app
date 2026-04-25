import { Injectable, signal } from "@angular/core";
import { HttpClient } from "@angular/common/http";


export type userType = {
  id: number,
  name: string,
  games: gameType[],
  ratings: {}
}


export type gameType = {
  name: string,
  id: number,
  genre: string,
  perspective: string,
  category: string,
}

@Injectable({ providedIn: "root" })
export class FrontService {

  constructor(private http: HttpClient) {}

  public user = signal<userType>({} as userType);
  public selectedGames = signal([] as any)
  public recommendedGames = signal([] as any)

  reset () {
    this.user.set({} as userType)
    this.selectedGames.set([])
    this.recommendedGames.set([])
  }

}
