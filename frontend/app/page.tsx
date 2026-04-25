"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Owner, Task, SystemStats, TaskFrequency } from "./types";
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

  const loadData = useCallback(async () => {
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
  }, [selectedOwnerId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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
      await api.completeTask(taskId);
    } else {
      await api.markTaskPending(taskId);
    }
    loadData();
  }

  async function handleDeletePet(petId: string) {
    if (!confirm("Delete this pet and all its tasks?")) return;
    await api.deletePet(petId);
    loadData();
  }

  async function handleDeleteTask(taskId: string) {
    if (!confirm("Delete this task?")) return;
    await api.deleteTask(taskId);
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
              {["Pets & Tasks", "Dashboard", "Chat", "Calendar"].map(
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
              {activeTab === 0 && <PetsTasksTab owner={selectedOwner} onToggle={handleToggleTask} onDeletePet={handleDeletePet} onDeleteTask={handleDeleteTask} />}
              {activeTab === 1 && <DashboardTab owner={selectedOwner} onToggle={handleToggleTask} onDeleteTask={handleDeleteTask} />}
              {activeTab === 2 && <ChatTab />}
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
  onDeletePet,
  onDeleteTask,
}: {
  owner: Owner;
  onToggle: (taskId: string, completed: boolean) => void;
  onDeletePet: (petId: string) => void;
  onDeleteTask: (taskId: string) => void;
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
          <div className="pet-card-header">
            <div className="flex items-center gap-3 mb-2">
              <span className="pet-icon">{SPECIES_ICONS[pet.animal] || "🐾"}</span>
              <div>
                <h3 className="pet-name">{pet.name}</h3>
                <p className="pet-details">
                  {SPECIES_LABELS[pet.animal]} {pet.breed && `• ${pet.breed}`}
                </p>
              </div>
            </div>
            <button
              onClick={() => onDeletePet(pet.id)}
              className="delete-btn"
              title="Delete pet"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
              </svg>
            </button>
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
                <TaskItem key={task.id} task={task} onToggle={onToggle} onDelete={onDeleteTask} />
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
  onDelete,
}: {
  task: Task;
  onToggle: (taskId: string, completed: boolean) => void;
  onDelete?: (taskId: string) => void;
}) {
  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const dateStr2 = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const timeStr = date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    return `${dateStr2} at ${timeStr}`;
  };

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
        {task.assigned_date && (
          <div className="task-datetime text-xs mt-0.5" style={{ color: 'var(--foreground-muted)' }}>
            {formatDateTime(task.assigned_date)}
          </div>
        )}
        <div className="flex items-center gap-2 mt-1">
          <span className={`badge badge-${task.priority === 1 ? 'low' : task.priority === 2 ? 'medium' : 'high'}`}>
            {task.priority === 1 ? 'Low' : task.priority === 2 ? 'Medium' : 'High'}
          </span>
          <span className={`badge badge-${task.status}`}>
            {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
          </span>
        </div>
      </div>
      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(task.id);
          }}
          className="delete-btn"
          title="Delete task"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
          </svg>
        </button>
      )}
    </div>
  );
}

function DashboardTab({
  owner,
  onToggle,
  onDeleteTask,
}: {
  owner: Owner;
  onToggle: (taskId: string, completed: boolean) => void;
  onDeleteTask?: (taskId: string) => void;
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
              <th style={{ width: '7rem' }}>Date & Time</th>
              <th style={{ width: '6rem' }}>Priority</th>
              <th style={{ width: '6rem' }}>Status</th>
              <th style={{ width: '3rem' }}></th>
            </tr>
          </thead>
          <tbody>
            {displayTasks.map((task) => {
              const pet = owner.pets.find((p) => p.id === task.pet_id);
              const formatDateTime = (dateStr: string | null) => {
                if (!dateStr) return "—";
                const date = new Date(dateStr);
                const dateStr2 = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
                const timeStr = date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
                return `${dateStr2}, ${timeStr}`;
              };
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
                  <td className="task-datetime" style={{ color: 'var(--foreground-muted)', fontSize: '0.8125rem' }}>
                    {formatDateTime(task.assigned_date)}
                  </td>
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
                  <td>
                    {onDeleteTask && (
                      <button
                        onClick={() => onDeleteTask(task.id)}
                        className="delete-btn"
                        title="Delete task"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                        </svg>
                      </button>
                    )}
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

function ChatTab() {
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [chatMode, setChatMode] = useState<"assistant" | "resources">("assistant");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const chatModes = [
    {
      id: "assistant" as const,
      label: "Ask About Pets & Tasks",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 8V4H8"/>
          <rect x="8" y="8" width="8" height="12" rx="2"/>
          <path d="M12 8h4"/>
          <circle cx="12" cy="12" r="1"/>
        </svg>
      ),
      description: "FAQ, task queries, and pet info"
    },
    {
      id: "resources" as const,
      label: "Pet Resource Finder",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
          <path d="M11 8v6"/>
          <path d="M8 11h6"/>
        </svg>
      ),
      description: "Products, shelters, vets via Gemini"
    }
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const currentMode = chatModes.find(m => m.id === chatMode)!;

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsTyping(true);

    try {
      let response: string;

      if (chatMode === "resources") {
        const searchResult = await api.searchPetResourceProducts(userMessage);
        response = searchResult.result;
      } else {
        const result = await api.chatbotQuery(userMessage);
        response = result.result;
      }
      setMessages((prev) => [...prev, { role: "assistant", content: response }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "I couldn't process your request at the moment. Make sure the backend is running and GOOGLE_API_KEY is configured." }]);
    }
    setIsTyping(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-mode-selector">
        <div className="chat-mode-dropdown" ref={dropdownRef}>
          <button 
            className="chat-mode-trigger"
            onClick={() => setDropdownOpen(!dropdownOpen)}
            aria-expanded={dropdownOpen}
            aria-haspopup="listbox"
          >
            <span className="chat-mode-trigger-icon">{currentMode.icon}</span>
            <span className="chat-mode-trigger-content">
              <span className="chat-mode-trigger-label">{currentMode.label}</span>
              <span className="chat-mode-trigger-desc">{currentMode.description}</span>
            </span>
            <svg 
              className={`chat-mode-chevron ${dropdownOpen ? 'open' : ''}`} 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
            >
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </button>
          {dropdownOpen && (
            <div className="chat-mode-menu" role="listbox">
              {chatModes.map((mode) => (
                <button
                  key={mode.id}
                  className={`chat-mode-option ${chatMode === mode.id ? 'selected' : ''}`}
                  onClick={() => {
                    setChatMode(mode.id);
                    setDropdownOpen(false);
                  }}
                  role="option"
                  aria-selected={chatMode === mode.id}
                >
                  <span className="chat-mode-option-icon">{mode.icon}</span>
                  <span className="chat-mode-option-content">
                    <span className="chat-mode-option-label">{mode.label}</span>
                    <span className="chat-mode-option-desc">{mode.description}</span>
                  </span>
                  {chatMode === mode.id && (
                    <svg className="chat-mode-check" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M20 6L9 17l-5-5"/>
                    </svg>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="chat-welcome-icon">
              {chatMode === "assistant" ? (
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 8V4H8"/>
                  <rect x="8" y="8" width="8" height="12" rx="2"/>
                  <path d="M12 8h4"/>
                  <circle cx="12" cy="12" r="1" fill="currentColor"/>
                </svg>
              ) : (
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                  <path d="M11 8v6"/>
                  <path d="M8 11h6"/>
                </svg>
              )}
            </div>
            <div className="chat-welcome-title">
              {chatMode === "assistant" ? "PawPal Assistant" : "Pet Resource Finder"}
            </div>
            <div className="chat-welcome-text">
              {chatMode === "assistant" 
                ? "Ask me anything about your pets and tasks. I can help with FAQs, task queries, and more."
                : "Find pet products, shelters, vets, and more. Powered by Gemini AI to search trusted pet retailers."}
            </div>
            <div className="chatSuggestions">
              {chatMode === "assistant" ? (
                <>
                  <button className="chat-suggestion-btn" onClick={() => setInput("How do I add a new pet?")}>Adding pets</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("How do I schedule a task?")}>Scheduling tasks</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("What do priority levels mean?")}>Priority levels</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("How does the calendar work?")}>Calendar help</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("tasks due today")}>Tasks due today</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("overdue tasks")}>Overdue tasks</button>
                </>
              ) : (
                <>
                  <button className="chat-suggestion-btn" onClick={() => setInput("best dog food for puppies")}>Best dog food</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("cat toys at Chewy")}>Cat toys</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("pet shelters near me")}>Find shelters</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("veterinarian near me")}>Find vets</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("organic pet food brands")}>Organic food</button>
                  <button className="chat-suggestion-btn" onClick={() => setInput("pet grooming near me")}>Grooming</button>
                </>
              )}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                <div className="chat-message-avatar">
                  {msg.role === "assistant" 
                    ? chatMode === "assistant"
                      ? <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8V4H8"/><rect x="8" y="8" width="8" height="12" rx="2"/><path d="M12 8h4"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>
                      : <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/><path d="M11 8v6"/><path d="M8 11h6"/></svg>
                    : <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  }
                </div>
                <div className="chat-message-content">
                  <div className="chat-message-text">{msg.content}</div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="chat-message assistant">
                <div className="chat-message-avatar">
                  {chatMode === "assistant"
                    ? <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8V4H8"/><rect x="8" y="8" width="8" height="12" rx="2"/><path d="M12 8h4"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>
                    : <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/><path d="M11 8v6"/><path d="M8 11h6"/></svg>
                  }
                </div>
                <div className="chat-message-content">
                  <div className="chat-typing">
                    <span className="chat-typing-dot"></span>
                    <span className="chat-typing-dot"></span>
                    <span className="chat-typing-dot"></span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder={chatMode === "assistant" ? "Ask about pets and tasks..." : "Search for pet products, shelters, vets..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={isTyping}
        />
        <button className="chat-send-btn" onClick={handleSend} disabled={isTyping || !input.trim()}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </div>
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
  const tasksWithDates = allTasks.filter((t) => t.assigned_date && t.status !== "completed");
  const [selectedMonth, setSelectedMonth] = useState(
    new Date().toISOString().slice(0, 7)
  );
  const [showTitles, setShowTitles] = useState(true);
  const [expandedDay, setExpandedDay] = useState<number | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

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

  const truncateTitle = (title: string, maxLength: number) => {
    if (title.length <= maxLength) return title;
    return title.slice(0, maxLength - 1) + "…";
  };

  return (
    <div className="calendar-container">
      <div className="calendar-controls">
        <div className="calendar-nav">
          <button
            className="calendar-nav-btn"
            onClick={() => {
              const prev = new Date(year, month - 2, 1);
              setSelectedMonth(`${prev.getFullYear()}-${String(prev.getMonth() + 1).padStart(2, "0")}`);
            }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M10 12l-4-4 4-4" stroke="currentColor" strokeWidth="2" fill="none" />
            </svg>
          </button>
          <h3 className="calendar-month-title">{monthName}</h3>
          <button
            className="calendar-nav-btn"
            onClick={() => {
              const next = new Date(year, month, 1);
              setSelectedMonth(`${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, "0")}`);
            }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M6 12l4-4-4-4" stroke="currentColor" strokeWidth="2" fill="none" />
            </svg>
          </button>
        </div>
        
        <div className="calendar-toggle-group">
          <button
            className={`calendar-toggle-btn ${showTitles ? 'active' : ''}`}
            onClick={() => setShowTitles(!showTitles)}
          >
            <span className="calendar-toggle-icon">{showTitles ? '◉' : '○'}</span>
            <span>Show Titles</span>
          </button>
          <button
            className="calendar-toggle-btn today-btn"
            onClick={() => {
              const today = new Date();
              setSelectedMonth(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`);
            }}
          >
            Today
          </button>
        </div>
      </div>

      <div className="calendar-grid">
        {weekdays.map((day) => (
          <div key={day} className="calendar-day-header">
            {day}
          </div>
        ))}
        
        {weeks.flat().map((day, idx) => {
          const dayTasks = day ? getTasksForDay(day) : [];
          const isExpanded = expandedDay === day;
          
          return (
            <div
              key={idx}
              className={`calendar-day ${day === null ? 'other-month' : ''} ${day && isToday(day) ? 'today' : ''} ${dayTasks.length > 0 ? 'has-tasks' : ''}`}
              onClick={() => {
                if (day && dayTasks.length > 0) {
                  setExpandedDay(isExpanded ? null : day);
                }
              }}
            >
              {day && (
                <>
                  <div className="calendar-day-header-row">
                    <span className={`calendar-day-number ${isToday(day) ? 'today-number' : ''}`}>{day}</span>
                    {dayTasks.length > 0 && (
                      <span className="calendar-task-count-badge">{dayTasks.length}</span>
                    )}
                  </div>
                  
                  {showTitles && dayTasks.length > 0 && (
                    <div className="calendar-task-list">
                      {dayTasks.slice(0, isExpanded ? undefined : 2).map((task) => {
                        const formatTime = (dateStr: string | null) => {
                          if (!dateStr) return '';
                          const date = new Date(dateStr);
                          return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
                        };
                        const pet = owner.pets.find((p) => p.id === task.pet_id);
                        return (
                          <button
                            key={task.id}
                            className={`calendar-task-item task-${task.status}`}
                            onClick={() => setSelectedTask(task)}
                          >
                            <span className="calendar-task-pet">
                              {pet?.name || 'Unknown'}
                            </span>
                            <span className={`calendar-task-title ${task.status === 'completed' ? 'completed' : ''}`}>
                              {truncateTitle(task.title, 14)}
                            </span>
                            {task.assigned_date && (
                              <span className="calendar-task-time">
                                {formatTime(task.assigned_date)}
                              </span>
                            )}
                            {task.priority === 3 && task.status !== 'completed' && (
                              <span className="calendar-priority-dot" title="High Priority" />
                            )}
                          </button>
                        );
                      })}
                      
                      {dayTasks.length > 2 && !isExpanded && (
                        <button 
                          className="calendar-expand-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedDay(day);
                          }}
                        >
                          +{dayTasks.length - 2} more
                        </button>
                      )}
                      
                      {isExpanded && dayTasks.length > 2 && (
                        <button 
                          className="calendar-expand-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedDay(null);
                          }}
                        >
                          Show less
                        </button>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>

      {selectedTask && (
        <div className="calendar-modal-overlay" onClick={() => setSelectedTask(null)}>
          <div className="calendar-modal" onClick={(e) => e.stopPropagation()}>
            <button className="calendar-modal-close" onClick={() => setSelectedTask(null)}>×</button>
            <div className="calendar-modal-content">
              <div className="calendar-modal-header">
                <span className={`calendar-modal-priority badge-${selectedTask.priority === 1 ? 'low' : selectedTask.priority === 2 ? 'medium' : 'high'}`}>
                  {selectedTask.priority === 1 ? 'Low' : selectedTask.priority === 2 ? 'Medium' : 'High'} Priority
                </span>
                <span className={`calendar-modal-status badge-${selectedTask.status}`}>
                  {selectedTask.status.charAt(0).toUpperCase() + selectedTask.status.slice(1)}
                </span>
              </div>
              <h3 className="calendar-modal-title">{selectedTask.title}</h3>
              {selectedTask.description && (
                <p className="calendar-modal-description">{selectedTask.description}</p>
              )}
              <div className="calendar-modal-details">
                <div className="calendar-modal-detail">
                  <span className="calendar-modal-label">Pet</span>
                  <span className="calendar-modal-value">
                    {owner.pets.find((p) => p.id === selectedTask.pet_id)?.name || 'Unknown'}
                  </span>
                </div>
                <div className="calendar-modal-detail">
                  <span className="calendar-modal-label">Frequency</span>
                  <span className="calendar-modal-value">{FREQUENCY_LABELS[selectedTask.frequency] || selectedTask.frequency}</span>
                </div>
                {selectedTask.assigned_date && (
                  <div className="calendar-modal-detail">
                    <span className="calendar-modal-label">Due Date</span>
                    <span className="calendar-modal-value">
                      {new Date(selectedTask.assigned_date).toLocaleDateString("en-US", { 
                        weekday: "long", 
                        month: "long", 
                        day: "numeric", 
                        year: "numeric" 
                      })}
                    </span>
                  </div>
                )}
                {selectedTask.assigned_date && (
                  <div className="calendar-modal-detail">
                    <span className="calendar-modal-label">Time</span>
                    <span className="calendar-modal-value">
                      {new Date(selectedTask.assigned_date).toLocaleTimeString("en-US", { 
                        hour: "numeric", 
                        minute: "2-digit" 
                      })}
                    </span>
                  </div>
                )}
              </div>
              <div className="calendar-modal-actions">
                <button 
                  className="btn-primary flex-1"
                  onClick={() => {
                    onToggle(selectedTask.id, selectedTask.status !== "completed");
                    setSelectedTask(null);
                  }}
                >
                  {selectedTask.status === 'completed' ? 'Mark Incomplete' : 'Mark Complete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}