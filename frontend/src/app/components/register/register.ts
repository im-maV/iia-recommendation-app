import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router'
import { FormsModule } from '@angular/forms';
import { FrontService } from '../../services/front.service';
import { APIService } from '../../services/api.service';

@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  private frontService = inject(FrontService)
  private apiService = inject(APIService)
  private router = inject(Router)
  public inputName = signal("")

  onRegisterName () {
    const name = this.inputName()
    if (!name) return;

    this.apiService.sendRegisterUser({ name }).subscribe({
      next: (res) => {
        console.log(res.body)
        this.frontService.user.set(res.body)
        this.router.navigate(["users/profile"]);
      },
      error: (err) => {
        console.log(err)
      }
    })};
}
