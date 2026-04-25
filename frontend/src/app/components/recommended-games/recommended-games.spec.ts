import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecommendedGames } from './recommended-games';

describe('RecommendedGames', () => {
  let component: RecommendedGames;
  let fixture: ComponentFixture<RecommendedGames>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecommendedGames],
    }).compileComponents();

    fixture = TestBed.createComponent(RecommendedGames);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
