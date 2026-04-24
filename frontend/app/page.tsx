"use client";

import { useState, useEffect } from "react";
import { Owner, Pet, Task, SystemStats, TaskFrequency } from "./types";
import * as api from "./api";

const SPECIES_ICONS: Record<string, string> = {
  dog: "🐕",
  cat: "🐈",
  bird: "🐦",
  rabbit: "🐰",
  other: "🐾",
};

const SPECIES_LABELS: Record<string, string> = {
  dog: "Dog",
  cat: "Cat",
  bird: "Bird",
  rabbit: "Rabbit",
  other: "Other",
};

const FREQUENCY_LABELS: Record<string, string> = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
  one_time: "One-time",
};

export default function Home() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [owners, setOwners] = useState<Owner[]>([]);
  const [selectedOwnerId, setSelectedOwnerId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);

  const [newOwnerName, setNewOwnerName] = useState("");
  const [newOwnerEmail, setNewOwnerEmail] = useState("");

  const [petName, setPetName] = useState("");
  const [petSpecies, setPetSpecies] = useState("dog");
  const [petBreed, setPetBreed] = useState("");
  const [petAge, setPetAge] = useState(1);
  const [petWeight, setPetWeight] = useState(10);

  const [taskTitle, setTaskTitle] = useState("");
  const [taskPriority, setTaskPriority] = useState(1);
  const [taskFrequency, setTaskFrequency] = useState<TaskFrequency>("one_time");
  const [taskDesc, setTaskDesc] = useState("");
  const [taskDate, setTaskDate] = useState("");
  const [taskTime, setTaskTime] = useState("09:00");
  const [taskPetId, setTaskPetId] = useState("");

  const selectedOwner = owners.find((o) => o.id === selectedOwnerId) || null;

  async function loadData() {
    setLoading(true);
    try {
      const [statsData, ownersData] = await Promise.all([
        api.getStats(),
        api.getOwners(),
      ]);
      setStats(statsData);
      setOwners(ownersData);
      if (ownersData.length > 0 && !selectedOwnerId) {
        setSelectedOwnerId(ownersData[0].id);
      }
    } catch (e) {
      console.error("Failed to load data:", e);
    }
    setLoading(false);
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleCreateOwner() {
    if (!newOwnerName.trim()) return;
    await api.createOwner(newOwnerName, newOwnerEmail);
    setNewOwnerName("");
    setNewOwnerEmail("");
    loadData();
  }

  async function handleDeleteOwner() {
    if (!selectedOwnerId) return;
    if (!confirm("Delete this owner and all their pets?")) return;
    await api.deleteOwner(selectedOwnerId);
    setSelectedOwnerId(null);
    loadData();
  }

  async function handleCreatePet() {
    if (!selectedOwnerId || !petName.trim()) return;
    await api.createPet(
      petName,
      petSpecies,
      petBreed,
      petAge,
      petWeight,
      selectedOwnerId
    );
    setPetName("");
    setPetBreed("");
    loadData();
  }

  async function handleCreateTask() {
    if (!selectedOwnerId || !taskTitle.trim()) return;
    const owner = owners.find((o) => o.id === selectedOwnerId);
    if (!owner || owner.pets.length === 0) return;
    
    const petId = taskPetId || owner.pets[0].id;
    const taskDatetime = taskDate ? `${taskDate}T${taskTime}:00` : null;
    await api.createTask(
      taskTitle,
      taskDesc,
      taskPriority,
      taskFrequency,
      taskDatetime,
      petId,
      selectedOwnerId
    );
    setTaskTitle("");
    setTaskDesc("");
    loadData();
  }

  async function handleToggleTask(taskId: string, completed: boolean) {
    if (completed) {
      await api.markTaskPending(taskId);
    } else {
      await api.completeTask(taskId);
    }
    loadData();
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto p-6">
        <header className="mb-8">
          <h1 className="text-2xl font-bold" style={{ fontFamily: 'var(--font-outfit)' }}>
            PawPal+ Dashboard
          </h1>
        </header>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <StatCard title="Owners" value={stats?.total_owners ?? 0} icon="👤" />
          <StatCard title="Pets" value={stats?.total_pets ?? 0} icon="🐾" />
          <StatCard title="Total Tasks" value={stats?.total_tasks ?? 0} icon="📋" />
          <StatCard title="Pending" value={stats?.pending_tasks ?? 0} icon="⏳" />
          <StatCard 
            title="Overdue" 
            value={stats?.overdue_tasks ?? 0} 
            icon="⚠️" 
            variant={stats?.overdue_tasks ? "danger" : "default"} 
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="card-header">
              <span className="text-xl">👤</span>
              <h2 className="card-title">Owner Setup</h2>
            </div>
            
            {owners.length > 0 && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                  Select Owner
                </label>
                <select
                  className="form-input"
                  value={selectedOwnerId || ""}
                  onChange={(e) => setSelectedOwnerId(e.target.value)}
                >
                  {owners.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <div className="space-y-3 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                  Name
                </label>
                <input
                  type="text"
                  placeholder="Enter owner name"
                  className="form-input"
                  value={newOwnerName}
                  onChange={(e) => setNewOwnerName(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                  Email (optional)
                </label>
                <input
                  type="email"
                  placeholder="email@example.com"
                  className="form-input"
                  value={newOwnerEmail}
                  onChange={(e) => setNewOwnerEmail(e.target.value)}
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={handleCreateOwner}
                className="btn-primary flex-1"
              >
                Create Owner
              </button>
              {selectedOwnerId && (
                <button
                  onClick={handleDeleteOwner}
                  className="btn-danger"
                >
                  Delete
                </button>
              )}
            </div>
            
            {selectedOwner && (
              <p className="text-sm mt-4" style={{ color: 'var(--foreground-muted)' }}>
                Current: <strong>{selectedOwner.name}</strong> &bull; {selectedOwner.pets.length} pets
              </p>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <span className="text-xl">🐾</span>
              <h2 className="card-title">Add Pet</h2>
            </div>
            
            <div className="space-y-3 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                  Pet Name
                </label>
                <input
                  type="text"
                  placeholder="Enter pet name"
                  className="form-input"
                  value={petName}
                  onChange={(e) => setPetName(e.target.value)}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                  Species
                </label>
                <select
                  className="form-input"
                  value={petSpecies}
                  onChange={(e) => setPetSpecies(e.target.value)}
                >
                  <option value="dog">Dog</option>
                  <option value="cat">Cat</option>
                  <option value="bird">Bird</option>
                  <option value="rabbit">Rabbit</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                    Age (years)
                  </label>
                  <input
                    type="number"
                    min="0"
                    className="form-input"
                    value={petAge}
                    onChange={(e) => setPetAge(Number(e.target.value))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                    Weight (lbs)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    className="form-input"
                    value={petWeight}
                    onChange={(e) => setPetWeight(Number(e.target.value))}
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                  Breed (optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g., Golden Retriever"
                  className="form-input"
                  value={petBreed}
                  onChange={(e) => setPetBreed(e.target.value)}
                />
              </div>
            </div>
            
            <button
              onClick={handleCreatePet}
              disabled={!selectedOwnerId}
              className="btn-primary w-full"
            >
              Add Pet
            </button>
            
            {!selectedOwnerId && (
              <div className="warning-message mt-3">
                <span>⚠️</span>
                <span>Create an owner first</span>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <span className="text-xl">📋</span>
              <h2 className="card-title">Add Task</h2>
            </div>
            
            {!selectedOwner || selectedOwner.pets.length === 0 ? (
              <div className="warning-message">
                <span>⚠️</span>
                <span>Add a pet first</span>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                    Task Title
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Vet appointment"
                    className="form-input"
                    value={taskTitle}
                    onChange={(e) => setTaskTitle(e.target.value)}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                      Priority
                    </label>
                    <select
                      className="form-input"
                      value={taskPriority}
                      onChange={(e) => setTaskPriority(Number(e.target.value))}
                    >
                      <option value={1}>Low</option>
                      <option value={2}>Medium</option>
                      <option value={3}>High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                      Frequency
                    </label>
                    <select
                      className="form-input"
                      value={taskFrequency}
                      onChange={(e) => setTaskFrequency(e.target.value as TaskFrequency)}
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="one_time">One-time</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                    Pet
                  </label>
                  <select
                    className="form-input"
                    value={taskPetId}
                    onChange={(e) => setTaskPetId(e.target.value)}
                  >
                    <option value="">Select a pet</option>
                    {selectedOwner.pets.map((pet) => (
                      <option key={pet.id} value={pet.id}>
                        {pet.name} ({SPECIES_LABELS[pet.animal]})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                    Description (optional)
                  </label>
                  <textarea
                    placeholder="Add details..."
                    className="form-input h-20 resize-none"
                    value={taskDesc}
                    onChange={(e) => setTaskDesc(e.target.value)}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                      Due Date
                    </label>
                    <input
                      type="date"
                      className="form-input"
                      value={taskDate}
                      onChange={(e) => setTaskDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--foreground-muted)' }}>
                      Time
                    </label>
                    <input
                      type="time"
                      className="form-input"
                      value={taskTime}
                      onChange={(e) => setTaskTime(e.target.value)}
                    />
                  </div>
                </div>
                
                <button
                  onClick={handleCreateTask}
                  className="btn-primary w-full"
                >
                  Add Task
                </button>
              </div>
            )}
          </div>
        </div>

        {!selectedOwner ? (
          <div className="card empty-state">
            <div className="empty-state-icon">👆</div>
            <div className="empty-state-title">Get Started</div>
            <div className="empty-state-text">Create an owner to begin managing your pets and tasks.</div>
          </div>
        ) : (
          <div className="card p-0">
            <div className="tab-list">
              {["Pets & Tasks", "Dashboard", "Schedule", "Calendar"].map(
                (tab, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveTab(i)}
                    className={`tab-button ${activeTab === i ? 'active' : ''}`}
                  >
                    {tab}
                  </button>
                )
              )}
            </div>

            <div className="p-6">
              {activeTab === 0 && <PetsTasksTab owner={selectedOwner} onToggle={handleToggleTask} />}
              {activeTab === 1 && <DashboardTab owner={selectedOwner} onToggle={handleToggleTask} />}
              {activeTab === 2 && <ScheduleTab ownerId={selectedOwner.id} />}
              {activeTab === 3 && <CalendarTab owner={selectedOwner} onToggle={handleToggleTask} />}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  variant = "default",
}: {
  title: string;
  value: number;
  icon: string;
  variant?: "default" | "danger";
}) {
  return (
    <div className="card">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <p className="stat-value" style={variant === "danger" ? { color: 'var(--danger)' } : {}}>
            {value}
          </p>
          <p className="stat-label">{title}</p>
        </div>
      </div>
    </div>
  );
}

function PetsTasksTab({
  owner,
  onToggle,
}: {
  owner: Owner;
  onToggle: (taskId: string, completed: boolean) => void;
}) {
  if (owner.pets.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🐾</div>
        <div className="empty-state-title">No Pets Yet</div>
        <div className="empty-state-text">Add a pet using the form above to get started!</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {owner.pets.map((pet) => (
        <div key={pet.id} className="pet-card">
          <div className="flex items-center gap-3 mb-2">
            <span className="pet-icon">{SPECIES_ICONS[pet.animal] || "🐾"}</span>
            <div>
              <h3 className="pet-name">{pet.name}</h3>
              <p className="pet-details">
                {SPECIES_LABELS[pet.animal]} {pet.breed && `• ${pet.breed}`}
              </p>
            </div>
          </div>
          <p className="pet-details mb-4">
            {pet.age} {pet.age === 1 ? 'year' : 'years'} old • {pet.weight} lbs
          </p>
          
          <div className="pet-stats">
            <div className="pet-stat">
              <div className="pet-stat-value">{pet.tasks.length}</div>
              <div className="pet-stat-label">Total</div>
            </div>
            <div className="pet-stat">
              <div className="pet-stat-value" style={{ color: 'var(--accent)' }}>
                {pet.tasks.filter((t) => t.status === "completed").length}
              </div>
              <div className="pet-stat-label">Done</div>
            </div>
            <div className="pet-stat">
              <div className="pet-stat-value">
                {pet.tasks.filter((t) => t.status === "pending").length}
              </div>
              <div className="pet-stat-label">Pending</div>
            </div>
            <div className="pet-stat">
              <div className="pet-stat-value" style={{ color: 'var(--danger)' }}>
                {pet.tasks.filter((t) => t.status === "overdue").length}
              </div>
              <div className="pet-stat-label">Overdue</div>
            </div>
          </div>
          
          <details className="mt-4">
            <summary className="cursor-pointer text-sm font-medium" style={{ color: 'var(--foreground-muted)' }}>
              View {pet.tasks.length} Tasks
            </summary>
            <div className="mt-3 space-y-2">
              {pet.tasks.map((task) => (
                <TaskItem key={task.id} task={task} onToggle={onToggle} />
              ))}
            </div>
          </details>
        </div>
      ))}
    </div>
  );
}

function TaskItem({
  task,
  onToggle,
}: {
  task: Task;
  onToggle: (taskId: string, completed: boolean) => void;
}) {
  return (
    <div 
      className={`flex items-center gap-3 p-2 rounded ${task.status === 'completed' ? 'task-row-completed' : ''} ${task.status === 'overdue' ? 'task-row-overdue' : ''}`}
      style={{ background: 'var(--background-muted)' }}
    >
      <div className="checkbox-wrapper">
        <input
          type="checkbox"
          checked={task.status === "completed"}
          onChange={(e) => onToggle(task.id, e.target.checked)}
          className="checkbox"
        />
      </div>
      <div className="flex-1 min-w-0">
        <div className="task-title text-sm font-medium truncate">{task.title}</div>
        <div className="flex items-center gap-2 mt-1">
          <span className={`badge badge-${task.priority === 1 ? 'low' : task.priority === 2 ? 'medium' : 'high'}`}>
            {task.priority === 1 ? 'Low' : task.priority === 2 ? 'Medium' : 'High'}
          </span>
          <span className={`badge badge-${task.status}`}>
            {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
          </span>
        </div>
      </div>
    </div>
  );
}

function DashboardTab({
  owner,
  onToggle,
}: {
  owner: Owner;
  onToggle: (taskId: string, completed: boolean) => void;
}) {
  const allTasks = owner.pets.flatMap((p) => p.tasks);
  const [filter, setFilter] = useState("All");
  const [sortBy, setSortBy] = useState("Priority");

  if (allTasks.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <div className="empty-state-title">No Tasks Yet</div>
        <div className="empty-state-text">Create tasks to see them on the dashboard!</div>
      </div>
    );
  }

  const pending = allTasks.filter((t) => t.status === "pending");
  const completed = allTasks.filter((t) => t.status === "completed");
  const overdue = allTasks.filter((t) => t.status === "overdue");

  const displayTasks = (() => {
    let tasks = allTasks;
    if (filter === "Pending") tasks = pending;
    else if (filter === "Completed") tasks = completed;
    else if (filter === "Overdue") tasks = overdue;

    if (sortBy === "Priority") {
      tasks = [...tasks].sort((a, b) => b.priority - a.priority);
    } else if (sortBy === "Date") {
      tasks = [...tasks].sort(
        (a, b) =>
          new Date(a.assigned_date || 0).getTime() -
          new Date(b.assigned_date || 0).getTime()
      );
    }
    return tasks;
  })();

  return (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="text-center p-3 rounded" style={{ background: 'var(--background-muted)' }}>
          <div className="stat-value">{allTasks.length}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="text-center p-3 rounded" style={{ background: 'var(--background-muted)' }}>
          <div className="stat-value">{pending.length}</div>
          <div className="stat-label">Pending</div>
        </div>
        <div className="text-center p-3 rounded" style={{ background: 'var(--background-muted)' }}>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{completed.length}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="text-center p-3 rounded" style={{ background: 'var(--background-muted)' }}>
          <div className="stat-value" style={{ color: 'var(--danger)' }}>{overdue.length}</div>
          <div className="stat-label">Overdue</div>
        </div>
        <div className="text-center p-3 rounded" style={{ background: 'var(--background-muted)' }}>
          <div className="stat-value">{owner.pets.length}</div>
          <div className="stat-label">Pets</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 mb-4">
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--foreground-subtle)' }}>
            Filter
          </label>
          <select
            className="form-input w-40"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="All">All Tasks</option>
            <option value="Pending">Pending</option>
            <option value="Completed">Completed</option>
            <option value="Overdue">Overdue</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--foreground-subtle)' }}>
            Sort By
          </label>
          <select
            className="form-input w-32"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="Priority">Priority</option>
            <option value="Date">Date</option>
          </select>
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '3rem' }}>Done</th>
              <th>Pet</th>
              <th>Task</th>
              <th style={{ width: '6rem' }}>Priority</th>
              <th style={{ width: '6rem' }}>Status</th>
              <th style={{ width: '6rem' }}>Frequency</th>
            </tr>
          </thead>
          <tbody>
            {displayTasks.map((task) => {
              const pet = owner.pets.find((p) => p.id === task.pet_id);
              return (
                <tr 
                  key={task.id} 
                  className={task.status === 'completed' ? 'task-row-completed' : task.status === 'overdue' ? 'task-row-overdue' : ''}
                >
                  <td className="checkbox-wrapper">
                    <input
                      type="checkbox"
                      checked={task.status === "completed"}
                      onChange={(e) => onToggle(task.id, e.target.checked)}
                      className="checkbox"
                    />
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <span>{SPECIES_ICONS[pet?.animal || 'other']}</span>
                      <span className="font-medium">{pet?.name || "Unknown"}</span>
                    </div>
                  </td>
                  <td className="task-title font-medium">{task.title}</td>
                  <td>
                    <span className={`badge badge-${task.priority === 1 ? 'low' : task.priority === 2 ? 'medium' : 'high'}`}>
                      {task.priority === 1 ? 'Low' : task.priority === 2 ? 'Medium' : 'High'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${task.status}`}>
                      {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                    </span>
                  </td>
                  <td style={{ color: 'var(--foreground-muted)' }}>
                    {FREQUENCY_LABELS[task.frequency] || task.frequency}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ScheduleTab({ ownerId }: { ownerId: string }) {
  const [schedule, setSchedule] = useState<any[]>([]);
  const [sortBy, setSortBy] = useState("Priority");

  useEffect(() => {
    api.getSchedule(ownerId).then(setSchedule);
  }, [ownerId]);

  return (
    <div>
      <div className="mb-4">
        <label className="block text-xs font-medium mb-1" style={{ color: 'var(--foreground-subtle)' }}>
          Sort By
        </label>
        <select
          className="form-input w-32"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="Priority">Priority</option>
          <option value="Date">Date</option>
        </select>
      </div>

      {schedule.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📅</div>
          <div className="empty-state-title">No Tasks to Schedule</div>
          <div className="empty-state-text">Add tasks with due dates to see them here.</div>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '3rem' }}>#</th>
                <th style={{ width: '3rem' }}>Done</th>
                <th>Task</th>
                <th>Pet</th>
                <th style={{ width: '5rem' }}>Priority</th>
                <th style={{ width: '5rem' }}>Status</th>
                <th style={{ width: '5rem' }}>Freq</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((task, i) => (
                <tr 
                  key={task.id}
                  className={task.status === 'overdue' ? 'task-row-overdue' : ''}
                >
                  <td style={{ color: 'var(--foreground-subtle)' }}>{i + 1}</td>
                  <td className="checkbox-wrapper">
                    {task.status === "completed" ? (
                      <span style={{ color: 'var(--accent)' }}>✓</span>
                    ) : null}
                  </td>
                  <td className="font-medium">{task.title}</td>
                  <td>{task.pet_name}</td>
                  <td>
                    <span className={`badge badge-${task.priority === 1 ? 'low' : task.priority === 2 ? 'medium' : 'high'}`}>
                      {task.priority === 1 ? 'Low' : task.priority === 2 ? 'Med' : 'High'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${task.status}`}>
                      {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                    </span>
                  </td>
                  <td style={{ color: 'var(--foreground-muted)' }}>
                    {FREQUENCY_LABELS[task.frequency] || task.frequency}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function CalendarTab({
  owner,
  onToggle,
}: {
  owner: Owner;
  onToggle: (taskId: string, completed: boolean) => void;
}) {
  const allTasks = owner.pets.flatMap((p) => p.tasks);
  const tasksWithDates = allTasks.filter((t) => t.assigned_date);
  const [selectedMonth, setSelectedMonth] = useState(
    new Date().toISOString().slice(0, 7)
  );

  if (tasksWithDates.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📆</div>
        <div className="empty-state-title">No Calendar Tasks</div>
        <div className="empty-state-text">Add tasks with due dates to see them on the calendar.</div>
      </div>
    );
  }

  const [year, month] = selectedMonth.split("-").map(Number);
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const startWeekday = firstDay.getDay();
  const daysInMonth = lastDay.getDate();

  const monthName = firstDay.toLocaleString("default", {
    month: "long",
    year: "numeric",
  });

  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const days: (number | null)[] = [];
  for (let i = 0; i < startWeekday; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);

  const weeks = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }

  const isTaskOnDay = (task: Task, day: number): boolean => {
    if (!task.assigned_date) return false;
    const taskDate = new Date(task.assigned_date);
    const taskYear = taskDate.getFullYear();
    const taskMonth = taskDate.getMonth() + 1;
    const taskDay = taskDate.getDate();

    if (task.frequency === "one_time") {
      return taskDay === day && taskMonth === month && taskYear === year;
    }

    const monthStart = new Date(year, month - 1, 1);
    const monthEnd = new Date(year, month, 0);

    if (task.frequency === "daily") {
      return taskDate <= monthEnd;
    }

    if (task.frequency === "weekly") {
      const taskWeekday = taskDate.getDay();
      const targetWeekday = new Date(year, month - 1, day).getDay();
      if (taskWeekday !== targetWeekday) return false;
      const taskStartOfWeek = new Date(taskDate);
      taskStartOfWeek.setDate(taskDate.getDate() - taskDate.getDay());
      const monthStartOfWeek = new Date(monthStart);
      monthStartOfWeek.setDate(1 - monthStart.getDay());
      return taskStartOfWeek <= monthEnd && monthStart <= new Date(year, month - 1, day);
    }

    if (task.frequency === "monthly") {
      if (taskDay !== day) return false;
      if (year < taskYear) return false;
      if (year === taskYear && month < taskMonth) return false;
      return true;
    }

    return taskDay === day && taskMonth === month && taskYear === year;
  };

  const getTasksForDay = (day: number) => {
    return tasksWithDates.filter((task) => isTaskOnDay(task, day));
  };

  const isToday = (day: number) => {
    const today = new Date();
    return (
      day === today.getDate() &&
      month === today.getMonth() + 1 &&
      year === today.getFullYear()
    );
  };

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--foreground-subtle)' }}>
            Month
          </label>
          <input
            type="month"
            className="form-input w-44"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
          />
        </div>
        <h3 className="text-xl font-semibold" style={{ fontFamily: 'var(--font-outfit)' }}>
          {monthName}
        </h3>
      </div>

      <div className="calendar-grid">
        {weekdays.map((day) => (
          <div key={day} className="calendar-day-header">
            {day}
          </div>
        ))}
        
        {weeks.flat().map((day, idx) => (
          <div
            key={idx}
            className={`calendar-day ${day === null ? 'other-month' : ''} ${day && isToday(day) ? 'today' : ''}`}
          >
            {day && (
              <>
                <div className="calendar-day-number">{day}</div>
                <div className="calendar-task-count">
                  {getTasksForDay(day).slice(0, 3).map((task) => (
                    <span 
                      key={task.id}
                      className={`calendar-task-badge badge-${task.status}`}
                      style={{
                        background: task.status === 'completed' ? 'var(--accent-light)' : 
                                   task.status === 'overdue' ? 'var(--danger-light)' : 
                                   'var(--warning-light)',
                        color: task.status === 'completed' ? 'var(--accent)' : 
                               task.status === 'overdue' ? 'var(--danger)' : 
                               'var(--warning)',
                      }}
                      title={`${task.title} (${FREQUENCY_LABELS[task.frequency] || task.frequency})`}
                    >
                      {task.status === 'completed' ? '✓' : task.status === 'overdue' ? '!' : '•'}
                      <span className="ml-1 text-xs">{task.frequency === 'daily' ? 'D' : task.frequency === 'weekly' ? 'W' : task.frequency === 'monthly' ? 'M' : ''}</span>
                    </span>
                  ))}
                  {getTasksForDay(day).length > 3 && (
                    <span className="calendar-task-badge" style={{ background: 'var(--background-muted)' }}>
                      +{getTasksForDay(day).length - 3}
                    </span>
                  )}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}