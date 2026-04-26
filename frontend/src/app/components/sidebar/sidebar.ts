import { Component, computed, input } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faCheck, faGamepad } from '@fortawesome/free-solid-svg-icons';
import { BadgeType, SidebarBadge, SidebarStep, StepIndex } from '@models/sidebar.model';

const SIDEBAR_STEPS: SidebarStep[] = [
  { index: StepIndex.Select, label: '01 — Selecionar jogos' },
  { index: StepIndex.Rate, label: '02 — Avaliar' },
  { index: StepIndex.Results, label: '03 — Ver recomendações' },
];

@Component({
  selector: 'app-sidebar',
  imports: [FontAwesomeModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
  name = input<string>();
  sub = input<string>();
  badge = input<SidebarBadge>();
  currentStep = input.required<StepIndex>();

  protected readonly BadgeType = BadgeType;
  protected readonly icons = { faGamepad, faCheck };

  protected readonly steps = computed<SidebarStep[]>(() => {
    const current = this.currentStep();

    return SIDEBAR_STEPS.map((step) => ({
      ...step,
      isActive: current !== undefined ? step.index === current : false,
      isDone: current !== undefined ? step.index < current : false,
    }));
  });
}
