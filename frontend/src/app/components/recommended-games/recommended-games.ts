import { Component, inject } from '@angular/core';
import { FrontService } from '../../services/front.service';

@Component({
  selector: 'app-recommended-games',
  imports: [],
  templateUrl: './recommended-games.html',
  styleUrl: './recommended-games.scss',
})
export class RecommendedGames {
  private frontService = inject(FrontService);
  public user = this.frontService.user();
}
