import { APIService } from './../../services/api.service';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FrontService } from '../../services/front.service';
import { Router } from '@angular/router';
import { gameType } from '../../services/front.service';

@Component({
  selector: 'app-profile',
  imports: [],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})


export class Profile implements OnInit {
  private frontService = inject(FrontService);
  private apiService = inject(APIService);
  public user = this.frontService.user();
  public allGames = signal([]);
  public random_games = computed(() => this.getRandomGames(this.allGames()));
  public selectedGames = signal<gameType[]>([]);
  public loading = signal(false);
  private router = inject(Router)

  getRandomGames(arr: gameType[], count = 10): gameType[] {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled.slice(0, count);
  }

  ngOnInit() {
    this.getGames();
  }

  getGames() {
    this.apiService.getGames().subscribe({
      next: (res) => {
        this.allGames.set(res.body);
      },
      error: (err) => {
        console.log(err);
      },
    });
  }

  toggleGame(game: any) {
    const current = this.selectedGames();

    const alreadySelected = current.find((g) => g.id === game.id);

    if (alreadySelected) {
      // remove se já estiver selecionado
      this.selectedGames.set(current.filter((g) => g.id !== game.id));
      return;
    }

    if (current.length >= 5) {
      alert('Você só pode selecionar até 5 jogos');
      return;
    }

    this.selectedGames.set([...current, game]);
  }

  sendSelectedGames() {
  const games = this.selectedGames();

  if (games.length !== 5) {
    alert("Selecione exatamente 5 jogos");
    return;
  }

  this.loading.set(true);

  this.apiService.getRecommendations({
    games: games
  }).subscribe({
    next: (res) => {
      console.log("Resposta:", res);
      const new_user = {
        ...this.frontService.user(),
        "games": res.body.games
      }
      this.frontService.user.set(new_user);
      this.loading.set(false);
      this.router.navigate(["recommendations"]);

    },
    error: (err) => {
       console.log("Erro completo:", JSON.stringify(err.error))
      this.loading.set(false);
      this.router.navigate(["users/profile"]);
    }
  });
}
}
