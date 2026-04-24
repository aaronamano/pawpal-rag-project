import { Owner, Pet, Task, SystemStats } from "./types";

const API_BASE = "http://localhost:8000";

export async function getStats(): Promise<SystemStats> {
  const res = await fetch(`${API_BASE}/api/stats`);
  return res.json();
}

export async function getOwners(): Promise<Owner[]> {
  const res = await fetch(`${API_BASE}/api/owners`);
  return res.json();
}

export async function createOwner(name: string, email: string = "") {
  const res = await fetch(`${API_BASE}/api/owners`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email }),
  });
  return res.json();
}

export async function deleteOwner(ownerId: string) {
  const res = await fetch(`${API_BASE}/api/owners/${ownerId}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function createPet(
  name: string,
  animal: string,
  breed: string,
  age: number,
  weight: number,
  ownerId: string
) {
  const res = await fetch(`${API_BASE}/api/pets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      animal,
      breed,
      age,
      weight,
      owner_id: ownerId,
    }),
  });
  return res.json();
}

export async function createTask(
  title: string,
  description: string,
  priority: number,
  frequency: string,
  assignedDate: string | null,
  petId: string
) {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title,
      description,
      priority,
      frequency,
      assigned_date: assignedDate,
      pet_id: petId,
    }),
  });
  return res.json();
}

export async function completeTask(taskId: string) {
  const res = await fetch(`${API_BASE}/api/tasks/${taskId}/complete`, {
    method: "POST",
  });
  return res.json();
}

export async function markTaskPending(taskId: string) {
  const res = await fetch(`${API_BASE}/api/tasks/${taskId}/pending`, {
    method: "POST",
  });
  return res.json();
}

export async function getSchedule(ownerId: string) {
  const res = await fetch(`${API_BASE}/api/schedule/${ownerId}`);
  return res.json();
}