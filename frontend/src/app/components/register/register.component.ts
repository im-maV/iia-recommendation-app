import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { UserStoreService } from '@services/user-store.service';
import { APIService } from '@services/api.service';
import { finalize } from 'rxjs';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faGamepad,
  faArrowRight,
  faUser,
  faTriangleExclamation,
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-register',
  imports: [FormsModule, FontAwesomeModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class Register {
  private readonly userStoreService = inject(UserStoreService);
  private readonly apiService = inject(APIService);
  private readonly router = inject(Router);

  readonly icons = { faGamepad, faArrowRight, faUser, faTriangleExclamation };

  readonly inputName = signal('');
  readonly showAlert = signal(false);
  readonly isLoading = signal(false);

  onRegisterName(): void {
    const name = this.inputName().trim();

    if (!name) {
      this.showAlert.set(true);
      return;
    }

    this.showAlert.set(false);
    this.isLoading.set(true);

    this.apiService
      .sendRegisterUser({ name })
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: ({ body }) => {
          if (!body) {
            console.error('[Register] Resposta sem body');
            this.showAlert.set(true);
            return;
          }
          this.userStoreService.user.set(body);
          this.router.navigate(['users/profile']);
        },
        error: (err: unknown) => {
          console.error('[Register] Erro ao registrar usuário:', err);
          this.showAlert.set(true);
        },
      });
  }
}
