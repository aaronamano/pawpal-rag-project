export type TaskStatus = "pending" | "completed" | "overdue" | "cancelled";
export type TaskFrequency = "daily" | "weekly" | "monthly" | "one_time";

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: number;
  frequency: TaskFrequency;
  assigned_date: string | null;
  status: TaskStatus;
  pet_id: string;
}

export interface Pet {
  id: string;
  name: string;
  animal: string;
  breed: string;
  age: number;
  weight: number;
  tasks: Task[];
}

export interface Owner {
  id: string;
  name: string;
  email: string;
  pets: Pet[];
}

export interface SystemStats {
  total_owners: number;
  total_pets: number;
  total_tasks: number;
  pending_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
}