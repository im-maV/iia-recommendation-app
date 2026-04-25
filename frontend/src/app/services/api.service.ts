import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { environment } from "../../environments/environment";

@Injectable({ providedIn: "root" })
export class APIService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  sendRegisterUser(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/register`, data, {observe: "response"});
  }

  sendUserProfile(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/profile`, data);
  }

  getGames(): Observable<any> {
    return this.http.get(`${this.apiUrl}/games`, {observe: "response"});
  }

  getRecommendations(data: any):Observable<any> {
    console.log(data)
    return this.http.post(`${this.apiUrl}/recommendations`, data, {observe: "response"});
  }
}
