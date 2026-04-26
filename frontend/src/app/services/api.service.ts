import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { RecommendationsPayload, RegisterUserPayload } from '@models/response.model';
import { GamesRated, gameType, userType } from '@models/user-type.model';

@Injectable({ providedIn: 'root' })
export class APIService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  sendRegisterUser(data: RegisterUserPayload): Observable<HttpResponse<userType>> {
    return this.http.post<userType>(`${this.apiUrl}/users/register`, data, { observe: 'response' });
  }

  sendUserProfile(data: Partial<userType>): Observable<userType> {
    return this.http.post<userType>(`${this.apiUrl}/users/profile`, data);
  }

  getGames(): Observable<HttpResponse<gameType[]>> {
    return this.http.get<gameType[]>(`${this.apiUrl}/games`, { observe: 'response' });
  }

  getRecommendations(data: RecommendationsPayload): Observable<HttpResponse<GamesRated[]>> {
    return this.http.post<GamesRated[]>(`${this.apiUrl}/recommendations`, data, {
      observe: 'response',
    });
  }
}
