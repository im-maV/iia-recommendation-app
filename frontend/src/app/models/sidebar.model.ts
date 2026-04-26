export enum BadgeType {
  Select = 'select',
  Rate = 'rate',
  Done = 'done',
}

export enum StepIndex {
  Select = 1,
  Rate = 2,
  Results = 3,
}

export type SidebarBadge = {
  label: string;
  icon: any;
  type: BadgeType;
};

export type SidebarStep = {
  index: StepIndex;
  label: string;
  isActive?: boolean;
  isDone?: boolean;
};
