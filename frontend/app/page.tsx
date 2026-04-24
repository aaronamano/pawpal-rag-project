"use client";

import { useState, useEffect } from "react";
import { Owner, Pet, Task, SystemStats, TaskFrequency } from "./types";
import * as api from "./api";

const SPECIES_EMOJI: Record<string, string> = {
  dog: "🐕",
  cat: "🐈",
  bird: "🐦",
  rabbit: "🐰",
  other: "🐾",
};

const PRIORITY_LABELS: Record<number, string> = {
  1: "📘 Low",
  2: "🟡 Medium",
  3: "🔴 High",
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
    
    const taskDatetime = taskDate ? `${taskDate}T${taskTime}:00` : null;
    await api.createTask(
      taskTitle,
      taskDesc,
      taskPriority,
      taskFrequency,
      taskDatetime,
      owner.pets[0].id
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
      <div className="min-h-screen flex items-center justify-center bg-zinc-50">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 font-sans">
      <div className="max-w-7xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">🐾 PawPal+ Dashboard</h1>

        <div className="grid grid-cols-5 gap-4 mb-6">
          <StatCard title="👤 Owners" value={stats?.total_owners ?? 0} />
          <StatCard title="🐾 Pets" value={stats?.total_pets ?? 0} />
          <StatCard title="📋 Total Tasks" value={stats?.total_tasks ?? 0} />
          <StatCard title="⏳ Pending" value={stats?.pending_tasks ?? 0} />
          <StatCard
            title="⚠️ Overdue"
            value={stats?.overdue_tasks ?? 0}
            highlight={stats?.overdue_tasks ? "red" : undefined}
          />
        </div>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
            <h2 className="text-lg font-semibold mb-4">👤 Owner Setup</h2>
            {owners.length > 0 && (
              <select
                className="w-full p-2 border rounded mb-4"
                value={selectedOwnerId || ""}
                onChange={(e) => setSelectedOwnerId(e.target.value)}
              >
                {owners.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.name}
                  </option>
                ))}
              </select>
            )}
            <input
              type="text"
              placeholder="New Owner Name"
              className="w-full p-2 border rounded mb-2"
              value={newOwnerName}
              onChange={(e) => setNewOwnerName(e.target.value)}
            />
            <input
              type="email"
              placeholder="Email (optional)"
              className="w-full p-2 border rounded mb-3"
              value={newOwnerEmail}
              onChange={(e) => setNewOwnerEmail(e.target.value)}
            />
            <div className="flex gap-2">
              <button
                onClick={handleCreateOwner}
                className="flex-1 bg-emerald-600 text-white py-2 rounded hover:bg-emerald-700"
              >
                Create Owner
              </button>
              {selectedOwnerId && (
                <button
                  onClick={handleDeleteOwner}
                  className="px-4 border border-red-500 text-red-500 rounded hover:bg-red-50"
                >
                  Delete
                </button>
              )}
            </div>
            {selectedOwner && (
              <p className="text-sm mt-3 text-zinc-500">
                Current: {selectedOwner.name} | 🐾 {selectedOwner.pets.length} pets
              </p>
            )}
          </div>

          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
            <h2 className="text-lg font-semibold mb-4">➕ Add Pet</h2>
            <input
              type="text"
              placeholder="Pet Name"
              className="w-full p-2 border rounded mb-2"
              value={petName}
              onChange={(e) => setPetName(e.target.value)}
            />
            <select
              className="w-full p-2 border rounded mb-2"
              value={petSpecies}
              onChange={(e) => setPetSpecies(e.target.value)}
            >
              <option value="dog">Dog</option>
              <option value="cat">Cat</option>
              <option value="bird">Bird</option>
              <option value="rabbit">Rabbit</option>
              <option value="other">Other</option>
            </select>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <input
                type="number"
                placeholder="Age (yrs)"
                className="p-2 border rounded"
                value={petAge}
                onChange={(e) => setPetAge(Number(e.target.value))}
              />
              <input
                type="number"
                placeholder="Weight (lbs)"
                className="p-2 border rounded"
                value={petWeight}
                onChange={(e) => setPetWeight(Number(e.target.value))}
              />
            </div>
            <input
              type="text"
              placeholder="Breed (optional)"
              className="w-full p-2 border rounded mb-3"
              value={petBreed}
              onChange={(e) => setPetBreed(e.target.value)}
            />
            <button
              onClick={handleCreatePet}
              disabled={!selectedOwnerId}
              className="w-full bg-emerald-600 text-white py-2 rounded hover:bg-emerald-700 disabled:opacity-50"
            >
              Add Pet
            </button>
            {!selectedOwnerId && (
              <p className="text-sm mt-2 text-amber-600">⚠️ Create owner first</p>
            )}
          </div>

          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
            <h2 className="text-lg font-semibold mb-4">📋 Add Task</h2>
            {!selectedOwner || selectedOwner.pets.length === 0 ? (
              <p className="text-amber-600">⚠️ Add a pet first</p>
            ) : (
              <>
                <input
                  type="text"
                  placeholder="Task Title"
                  className="w-full p-2 border rounded mb-2"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                />
                <select
                  className="w-full p-2 border rounded mb-2"
                  value={taskPriority}
                  onChange={(e) => setTaskPriority(Number(e.target.value))}
                >
                  <option value={1}>📘 Low Priority</option>
                  <option value={2}>🟡 Medium Priority</option>
                  <option value={3}>🔴 High Priority</option>
                </select>
                <select
                  className="w-full p-2 border rounded mb-2"
                  value={taskFrequency}
                  onChange={(e) => setTaskFrequency(e.target.value as TaskFrequency)}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="one_time">One Time</option>
                </select>
                <textarea
                  placeholder="Description (optional)"
                  className="w-full p-2 border rounded mb-2 h-16"
                  value={taskDesc}
                  onChange={(e) => setTaskDesc(e.target.value)}
                />
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <input
                    type="date"
                    className="p-2 border rounded"
                    value={taskDate}
                    onChange={(e) => setTaskDate(e.target.value)}
                  />
                  <input
                    type="time"
                    className="p-2 border rounded"
                    value={taskTime}
                    onChange={(e) => setTaskTime(e.target.value)}
                  />
                </div>
                <button
                  onClick={handleCreateTask}
                  className="w-full bg-emerald-600 text-white py-2 rounded hover:bg-emerald-700"
                >
                  Add Task
                </button>
              </>
            )}
          </div>
        </div>

        {!selectedOwner ? (
          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-8 text-center">
            <p className="text-xl text-zinc-500">👆 Create an owner first!</p>
          </div>
        ) : (
          <div className="bg-white dark:bg-zinc-900 rounded-lg border">
            <div className="flex border-b">
              {["🐾 Pets & Tasks", "📊 Dashboard", "📅 Schedule", "📆 Calendar"].map(
                (tab, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveTab(i)}
                    className={`flex-1 py-3 font-medium ${
                      activeTab === i
                        ? "border-b-2 border-emerald-600 text-emerald-600"
                        : "text-zinc-500 hover:text-zinc-700"
                    }`}
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
  highlight,
}: {
  title: string;
  value: number;
  highlight?: "red";
}) {
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
      <h3 className="text-sm text-zinc-500">{title}</h3>
      <p className={`text-2xl font-bold ${highlight === "red" ? "text-red-600" : ""}`}>
        {value}
      </p>
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
    return <p className="text-zinc-500">No pets yet. Add a pet using the form above!</p>;
  }

  return (
    <div className="grid grid-cols-4 gap-4">
      {owner.pets.slice(0, 4).map((pet) => (
        <div key={pet.id} className="border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{SPECIES_EMOJI[pet.animal] || "🐾"}</span>
            <h3 className="text-lg font-semibold">{pet.name}</h3>
          </div>
          <p className="text-sm text-zinc-500 mb-3">
            {pet.animal} | {pet.breed || "N/A"} | {pet.age} yrs | {pet.weight} lbs
          </p>
          <div className="grid grid-cols-4 gap-2 mb-3 text-sm">
            <div className="text-center">
              <div className="font-bold">{pet.tasks.length}</div>
              <div className="text-zinc-500">Total</div>
            </div>
            <div className="text-center">
              <div className="font-bold">{pet.tasks.filter((t) => t.status === "completed").length}</div>
              <div className="text-zinc-500">Done</div>
            </div>
            <div className="text-center">
              <div className="font-bold">{pet.tasks.filter((t) => t.status === "pending").length}</div>
              <div className="text-zinc-500">Pending</div>
            </div>
            <div className="text-center">
              <div className="font-bold">{pet.tasks.filter((t) => t.status === "overdue").length}</div>
              <div className="text-zinc-500">Overdue</div>
            </div>
          </div>
          <details className="text-sm">
            <summary className="cursor-pointer text-zinc-500">
              View Tasks ({pet.tasks.length})
            </summary>
            <div className="mt-2 space-y-2">
              {pet.tasks.map((task) => (
                <div key={task.id} className="flex items-center gap-2 p-2 bg-zinc-50 rounded">
                  <input
                    type="checkbox"
                    checked={task.status === "completed"}
                    onChange={(e) => onToggle(task.id, e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span
                    className={
                      task.status === "completed"
                        ? "line-through text-zinc-400"
                        : task.status === "overdue"
                        ? "text-red-600"
                        : ""
                    }
                  >
                    {task.title}
                  </span>
                </div>
              ))}
            </div>
          </details>
        </div>
      ))}
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
  const [filter, setFilter] = useState("All Tasks");
  const [sortBy, setSortBy] = useState("Priority");

  if (allTasks.length === 0) {
    return <p className="text-zinc-500">No tasks yet. Create tasks to see the dashboard!</p>;
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
      <div className="grid grid-cols-5 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold">{allTasks.length}</div>
          <div className="text-sm text-zinc-500">Total</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold">{pending.length}</div>
          <div className="text-sm text-zinc-500">Pending</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold">{completed.length}</div>
          <div className="text-sm text-zinc-500">Completed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{overdue.length}</div>
          <div className="text-sm text-zinc-500">Overdue</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold">{owner.pets.length}</div>
          <div className="text-sm text-zinc-500">Pets</div>
        </div>
      </div>

      <div className="flex gap-4 mb-4">
        <select
          className="p-2 border rounded"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option>All Tasks</option>
          <option>Pending</option>
          <option>Completed</option>
          <option>Overdue</option>
        </select>
        <select
          className="p-2 border rounded"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option>Priority</option>
          <option>Date</option>
          <option>Pet Name</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Done</th>
              <th className="text-left py-2">Pet</th>
              <th className="text-left py-2">Task</th>
              <th className="text-left py-2">Priority</th>
              <th className="text-left py-2">Status</th>
              <th className="text-left py-2">Freq</th>
            </tr>
          </thead>
          <tbody>
            {displayTasks.map((task) => {
              const pet = owner.pets.find((p) => p.id === task.pet_id);
              return (
                <tr key={task.id} className="border-b">
                  <td className="py-2">
                    <input
                      type="checkbox"
                      checked={task.status === "completed"}
                      onChange={(e) => onToggle(task.id, e.target.checked)}
                    />
                  </td>
                  <td className="py-2">🐾 {pet?.name || "?"}</td>
                  <td className="py-2">{task.title}</td>
                  <td className="py-2">{PRIORITY_LABELS[task.priority]}</td>
                  <td className="py-2">
                    {task.status === "completed"
                      ? "✅ Done"
                      : task.status === "overdue"
                      ? "⚠️ Overdue"
                      : "⏳ Pending"}
                  </td>
                  <td className="py-2">{task.frequency}</td>
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
      <div className="flex gap-4 mb-4">
        <select
          className="p-2 border rounded"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option>Priority</option>
          <option>Date</option>
          <option>Pet Name</option>
        </select>
      </div>

      {schedule.length === 0 ? (
        <p className="text-zinc-500">No tasks to schedule</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">#</th>
                <th className="text-left py-2">Done</th>
                <th className="text-left py-2">Task</th>
                <th className="text-left py-2">Pet</th>
                <th className="text-left py-2">P</th>
                <th className="text-left py-2">Status</th>
                <th className="text-left py-2">Freq</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((task, i) => (
                <tr key={task.id} className="border-b">
                  <td className="py-2">{i + 1}</td>
                  <td className="py-2">{task.status === "completed" ? "✅" : ""}</td>
                  <td className="py-2">{task.title}</td>
                  <td className="py-2">{task.pet_name}</td>
                  <td className="py-2">
                    {task.priority === 1 ? "📘" : task.priority === 2 ? "🟡" : "🔴"}
                  </td>
                  <td className="py-2">
                    {task.status === "completed"
                      ? "✅"
                      : task.status === "overdue"
                      ? "⚠️"
                      : "⏳"}
                  </td>
                  <td className="py-2">{task.frequency}</td>
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
      <p className="text-zinc-500">
        ⚠️ Add tasks with due dates to see them on the calendar!
      </p>
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

  const getTasksForDay = (day: number) => {
    return tasksWithDates.filter((task) => {
      const taskDate = new Date(task.assigned_date!);
      return (
        taskDate.getDate() === day &&
        taskDate.getMonth() === month - 1 &&
        taskDate.getFullYear() === year
      );
    });
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
      <div className="flex items-center gap-4 mb-4">
        <input
          type="month"
          className="p-2 border rounded"
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(e.target.value)}
        />
        <h3 className="text-xl font-semibold">📆 {monthName}</h3>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekdays.map((day) => (
          <div key={day} className="text-center font-semibold text-sm">
            {day}
          </div>
        ))}
      </div>

      {weeks.map((week, wi) => (
        <div key={wi} className="grid grid-cols-7 gap-1 mb-1">
          {week.map((day, di) => (
            <div
              key={di}
              className={`min-h-[80px] border rounded p-1 text-center ${
                day === null
                  ? "border-transparent"
                  : isToday(day)
                  ? "bg-green-50 border-green-500"
                  : "bg-zinc-50"
              }`}
            >
              {day && (
                <>
                  <div className="font-semibold text-sm">{day}</div>
                  <div className="text-xs">
                    {getTasksForDay(day).length > 0 && (
                      <span className="text-zinc-500">
                        {getTasksForDay(day).filter((t) => t.status === "completed")
                          .length >
                          0 && "✅"}
                        {getTasksForDay(day).filter((t) => t.status === "pending")
                          .length >
                          0 &&
                          `⏳${getTasksForDay(day).filter((t) => t.status === "pending").length}`}
                        {getTasksForDay(day).filter((t) => t.status === "overdue")
                          .length >
                          0 &&
                          `⚠️${getTasksForDay(day).filter((t) => t.status === "overdue").length}`}
                      </span>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}