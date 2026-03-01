# 📅 EventsCalendar

EventsCalendar is a modern, dark-themed desktop productivity application built using Python and Tkinter.  
It combines an interactive month-view calendar with structured task management and real-time productivity tracking.

All data is stored locally using JSON. No backend. No external services. Fully offline.

---

## ✨ Overview

EventsCalendar allows users to:

- Navigate through months dynamically  
- Select any date from an interactive grid  
- Add categorized events with priority and status  
- Track completion progress  
- View monthly productivity insights  
- Filter events by category  

Over time, users build a structured, visual timeline of their productivity.

---

## 🗂 Structured Event System

Each event includes:

- Title  
- Date  
- Optional time  
- Category (Study, Work, Personal, Health, Meetings)  
- Priority (High, Medium, Low)  
- Status (Pending, In Progress, Done)  
- Optional notes  

Events are stored in a structured JSON format for efficient retrieval and filtering.

---

## 🎨 User Interface & Experience

EventsCalendar is designed with clarity and structure in mind:

- Dark theme with centralized color system  
- Hover interactions  
- Clickable calendar cells  
- Event preview chips inside calendar grid  
- Scrollable daily event sidebar  
- Read-only protection for past dates  
- Live character counter during event creation  
- Keyboard shortcuts (Enter to Save, Esc to Cancel)  
- Automatic data saving  

---

## 📊 Productivity Insights

EventsCalendar provides real-time analytics:

- Monthly total event count  
- Completed vs Pending breakdown  
- Category distribution visualization  
- “Today” badge indicator  
- Status bar summary  

All metrics update instantly after modifications.

---

## 🛠 Tech Stack

- Python 3  
- Tkinter  
- ttk  
- JSON  
- Datetime module  
- Object-Oriented Programming  

No third-party libraries required.

---

## 🧠 Architecture

The application follows a modular object-oriented structure:

- `EventsCalendarApp` – Main application controller  
- `EventDialog` – Dedicated event creation component  
- Centralized theming configuration  
- JSON-based data modeling  
- Dynamic calendar grid rendering  
- Sidebar-based event card rendering  

---

## 📱 Platform

- Desktop application  
- Offline-first design  
- Cross-platform (Windows / macOS / Linux with Python support)

---

## 👩‍💻 Developer

Built with a focus on structured productivity, clean UI architecture, and lightweight offline design.

---
