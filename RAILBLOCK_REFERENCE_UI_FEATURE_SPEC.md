# RailBlock AI — Reference UI Feature & UX Specification

## Purpose

This document extracts the useful **UI/UX patterns, features, interactions, and information architecture** from the supplied reference RailBlock frontend so another coding agent can reproduce the *good ideas* without needing access to the original ZIP.

This is a **feature/UX specification**, not a copy of the reference application's data or architecture.

---

# 1. Overall Product Experience

The reference presents itself as a **Railway Operations Management / Operations Control Center** application.

The visual language should communicate:

- railway operations
- infrastructure monitoring
- maintenance readiness
- train movement
- resources
- alerts
- reports
- administrative control
- professional enterprise software

The layout uses a persistent left sidebar, a sticky top header, and a scrollable main workspace.

The interface is responsive and supports desktop/mobile navigation.

---

# 2. Main Navigation / Information Architecture

The reference navigation contains:

1. Dashboard
2. Trains
3. Schedules
4. Resources
5. Maintenance
6. Corridors
7. Reports
8. Alerts
9. Settings
10. Admin

For RailBlock AI, these should be adapted to the actual backend and SIH26027 requirements.

Recommended RailBlock AI navigation:

- Dashboard
- Trains
- Schedules
- Resources
- Maintenance
- Assets
- Corridors
- Generate Plan
- Block Schedule
- Reports
- Alerts
- Settings
- Admin / System (prototype controls only)

---

# 3. Global Layout

## Sidebar

The reference uses:

- dark navy sidebar
- product logo/icon
- product name and subtitle
- active navigation highlighting
- icons beside every navigation item
- hover states
- vertically scrollable navigation
- user/profile area near bottom

The footer/sidebar area also communicates the product identity.

For RailBlock AI, preserve the existing SIH/CP-SAT branding and add an obvious system status indicator where useful.

## Topbar

The reference topbar contains:

- current page title
- page subtitle
- current date
- current time
- notification icon
- notification unread badge
- notification dropdown
- responsive menu button on smaller screens

This should be adapted to RailBlock AI and use real backend status where possible.

## Main Content

Main content is:

- light slate/neutral background
- rounded cards/panels
- strong spacing rhythm
- clear headings
- responsive grids
- dense but readable tables
- subtle shadows/borders

---

# 4. Reusable UI Building Blocks

The reference uses reusable components/patterns that should be replicated in the existing React/TypeScript project.

## Stat Card

Each metric card supports:

- icon
- icon background
- label
- main value
- optional delta
- optional direction indicator
- optional contextual caption

Use for:

- Asset Availability
- Maintenance Completion
- Critical Tasks
- Active Blocks
- Total Trains
- Active Corridors
- Overdue Tasks
- Resources
- Alerts

Never hardcode operational values in RailBlock AI.

## Panel / Card

Reusable panels support:

- title
- optional action button
- content area
- consistent border/radius/shadow

Use for:

- charts
- summaries
- tables
- alerts
- resource availability
- plan results

## Status Pill

Reusable status badges distinguish states such as:

- Active
- Delayed
- Completed
- Pending
- In Progress
- Warning
- Critical
- Resolved

Use the RailBlock AI domain status values rather than copying incompatible reference values.

## Priority Label

Reusable priority badges for:

- Critical
- High
- Medium
- Low

These map well to RailBlock AI's AI priority system.

## Search Bar

Reusable search component with:

- icon
- placeholder
- controlled value
- clear styling
- focus state

## Primary Button

Reusable primary action button with:

- icon
- clear label
- consistent blue/primary treatment
- hover/focus states

## Ghost / Secondary Button

Reusable secondary action button with:

- icon
- muted surface
- optional active state

## Data Table

Reusable table pattern with:

- configurable columns
- consistent headers
- responsive horizontal scrolling
- empty-state text
- row hover states
- action buttons

---

# 5. Dashboard Features

The reference Dashboard is designed as an operations-center overview.

## Hero / Operations Center Banner

Large top panel with:

- product title
- operations-center messaging
- short description
- visual background treatment
- two compact summary metrics

Reference concept:

"RailBlock AI Operations Center"

Description concept:

"Real-time visibility across train movement, corridors, resources and maintenance readiness."

For RailBlock AI, use this wording as inspiration, but never claim real-time telemetry unless actually available.

## KPI Grid

The dashboard uses a responsive 4-column-style KPI arrangement on larger screens.

Useful KPI families:

- Network/Asset Health
- Active Trains
- Active Corridors
- Maintenance Tasks
- Resource Availability
- Alerts

RailBlock AI should prioritize its actual SIH KPIs:

- Asset Availability %
- Maintenance Completion %
- Critical Tasks
- Active Blocks
- Train Impact Score
- Overdue Tasks
- Total Trains
- Total Corridors
- Resource Availability

## Train Status Distribution

Reference has a donut-style chart with:

- total count in center
- status legend
- multiple status categories

RailBlock AI can use this for actual train status data.

Do not use a hardcoded total.

## Upcoming Departures

Reference has a compact searchable departures panel.

Features:

- search by train or route
- displays first few matching departures
- train identifier
- departure/arrival route
- departure time

RailBlock AI should source this from real database-backed train/schedule information.

## Maintenance Overview

Reference has a compact table showing:

- task ID
- task name
- asset/location
- priority
- status

Rows are interactive in the reference and can advance status.

For RailBlock AI, only enable status updates if backed by a real API endpoint.

## Alerts Preview

Dashboard shows a few recent alerts.

Each alert includes:

- text
- timestamp
- unread indicator
- click-to-mark-read behavior

For RailBlock AI, alerts should be derived from real operational conditions when possible.

## Resource Availability

Reference shows resource category utilization as progress bars.

Resource categories include:

- locomotives
- coaches
- crew members
- maintenance units

For RailBlock AI, adapt this to the actual Resource model:

- Engineering resources
- Traction resources
- S&T resources
- maintenance crews/equipment

Only display utilization if it is actually calculable.

---

# 6. Trains Module

## Features

The reference Trains page supports:

- train count
- search by train name or number
- status filter
- filter dropdown
- add train button
- add train modal
- train list/table
- remove train action
- summary cards by status

## Add Train Form

The reference form concept collects railway identity and schedule information.

RailBlock AI should use fields actually supported by the backend, such as:

- Train number
- Train name, if available
- Train type
- Origin
- Destination
- Corridor
- Departure time
- Arrival time
- Priority
- Occupancy

Creation must go through:

React → FastAPI → SQLAlchemy → SQLite

Never write directly to SQLite from React.

## Search/Filtering

Recommended filters:

- All
- On Time
- Delayed
- Cancelled
- Other actual backend-supported statuses

Do not fabricate statuses.

---

# 7. Schedules Module

## Features

The reference Schedules page provides:

- schedule listing
- search by train/route
- week picker
- current-week highlighting
- date navigation
- add schedule button
- new schedule modal/form
- train autocomplete
- station autocomplete
- departure time
- arrival time
- weekly load visualization

## Weekly Planning UX

The reference allows selecting among week windows.

For RailBlock AI this can be adapted to:

- weekly maintenance planning horizon
- date-aware schedule visibility
- corridor/trains timeline

Do not build a separate fake scheduling system if the backend already provides the planning/block domain.

---

# 8. Resources Module

## Resource Categories

Reference categories:

- Locomotives
- Coaches
- Crew Members
- Maintenance Units

Each category has a resource card/list and an add-resource workflow.

## Resource Card

Useful presentation:

- resource title/type
- count
- status
- utilization
- action to add resource

## Add Resource

Reference uses reusable forms.

For RailBlock AI adapt this around the actual Resource model:

- resource ID
- name
- department
- capability
- availability
- quantity

Do not invent backend-supported fields.

---

# 9. Maintenance Module

## Maintenance Page Features

Reference provides:

- maintenance heading
- searchable task table
- task priority
- due date
- asset/location
- responsible person
- status
- task creation modal
- status progression

## Add Maintenance Work

Reference form concept includes:

- responsible person
- task name
- asset / location
- priority
- due date
- initial status

RailBlock AI should expand this with its actual domain fields:

- Asset
- Department
- Task Type
- Description
- Criticality
- Due Date
- Estimated Duration
- Required Block Duration
- Safety Impact
- Asset Impact
- Corridor
- Required Resources
- Dependency

Creation must use the backend API and persist in SQLite.

## Status Workflow

Reference concept:

Pending → In Progress → Completed → Pending

For RailBlock AI use backend-supported states such as:

PENDING
IN_PROGRESS
COMPLETED
OVERDUE

Only permit valid transitions.

---

# 10. Corridors Module

## Features

Reference corridor cards show:

- corridor ID
- corridor name
- route
- length
- daily trains
- operational status
- signal status

RailBlock AI should use its actual Corridor model and display:

- corridor ID
- name
- start station
- end station
- distance
- capacity
- availability windows
- train count
- block count

Do not invent "signal status" unless a real backend field exists.

---

# 11. Reports Module

The reference includes a report catalog.

## Report Metadata

Each report has:

- report name
- format
- data source

Formats shown include concepts such as:

- PDF
- XLSX
- CSV

## Useful RailBlock AI Reports

Adapt the idea to real analytics:

- Asset Availability
- Maintenance Completion
- Critical Task Summary
- Train Impact
- Corridor Utilization
- Resource Utilization
- Baseline vs Optimized Plan
- Overdue Maintenance
- Generated Block Plan

Start with CSV export for reliability.

PDF/XLSX are optional.

Never generate fabricated values.

---

# 12. Alerts Module

The reference provides an Alerts page with filtering.

## Alert Categories

- Critical
- Warning
- Info
- Resolved

## Alert Information

Each alert can include:

- message
- severity
- timestamp
- read/unread state

## RailBlock AI Alert Sources

Prefer dynamically derived alerts from actual data:

- severe defect
- overdue critical task
- high-risk asset
- unscheduled critical maintenance
- train conflict warning
- corridor capacity issue
- validation violation
- optimizer failure/timeout
- backend unavailable

Do not maintain fake hardcoded alert arrays as operational truth.

---

# 13. Settings Module

Reference Settings has sections for:

- Profile
- Notifications
- Security
- System Preferences

## Profile

Useful profile fields:

- full name
- role
- organization/context

For a hackathon prototype, profile data can remain local if no auth backend exists.

## Notifications

Useful preferences:

- email notifications
- critical alerts
- report notifications
- weekly summaries

Only implement settings that are meaningful to the demo.

## Security

The reference discusses password/security concepts.

RailBlock AI should NOT fake authentication.

Instead show prototype/security status and clearly state when authentication is not implemented.

## System Preferences

RailBlock AI should include:

- Light mode
- Dark mode
- optional System mode
- API/backend status
- database status
- CP-SAT status
- ML model status
- app version
- SIH problem number

Persist theme preference locally unless a backend preference model exists.

---

# 14. Admin Module

Reference Admin provides:

- user management
- search users
- role filtering
- status filtering
- add user
- activate/suspend
- system policy controls
- backup interval
- audit retention
- audit log
- system status cards

Reference admin data is local/browser based.

For RailBlock AI:

Do NOT claim this is production role-based authentication unless a real auth backend exists.

A safer version is a System/Admin page containing:

- system health
- model status
- optimizer status
- demo database controls
- audit information
- configuration

---

# 15. Search / Filtering Patterns

Strong reusable patterns from the reference:

- global-style search inputs
- per-page search
- dropdown filters
- active filter buttons
- clear empty states
- search result counts
- responsive filter layout

Good RailBlock AI filters:

## Trains
- search
- status
- corridor

## Maintenance
- search
- department
- status
- criticality
- AI priority
- overdue

## Assets
- search
- asset type
- criticality
- condition/status

## Corridors
- search
- traffic level
- operational status

## Blocks
- corridor
- department
- horizon
- status

---

# 16. Modal / Form Patterns

Reference modals share:

- fixed overlay
- rounded dialog
- form fields
- validation message
- cancel action
- primary submit action
- local form state

RailBlock AI should use the same reusable pattern for:

- Add Train
- Add Maintenance Task
- Add Resource
- Add Schedule (when supported)
- Add Corridor (when supported)

All form submissions must use actual backend APIs.

---

# 17. Responsive / Mobile Behavior

The reference supports:

- collapsible sidebar
- overlay on mobile
- desktop fixed sidebar
- responsive cards
- scrollable tables
- responsive charts
- stacked layouts

Preserve these patterns.

---

# 18. Visual Design Direction

Reference visual characteristics:

- deep navy sidebar
- blue primary action color
- white cards
- light slate page background
- rounded corners
- subtle borders
- subtle shadows
- readable dark text
- muted secondary text
- colored status pills
- clear hierarchy

RailBlock AI should enhance this with a stronger railway/control-center identity.

Recommended visual vocabulary:

- Navy = control / infrastructure
- Blue = primary action / planning
- Emerald = healthy/success
- Amber = warning
- Red = critical
- Slate = neutral/context

Avoid:

- excessive gradients
- overly rounded childish UI
- excessive animations
- gaming aesthetics
- giant empty sections

---

# 19. Dashboard Interaction Details

Useful interactions worth adapting:

- click KPI to open relevant page
- click maintenance row to inspect task
- click notification to mark as read
- click "View All" to navigate to detailed page
- quick search for trains/routes
- status filters
- compact context labels

Only enable an interaction when the backend can support the result.

---

# 20. Loading / Empty / Error States

The reference consistently shows explicit empty states.

RailBlock AI should have reusable components for:

### Loading
- spinner or skeleton
- descriptive text

### Empty
- icon
- short message
- optional action

### Error
- clear message
- retry button

Example error:

BACKEND CONNECTION LOST

Unable to retrieve railway operations data.

Retry

Never show raw stack traces in the UI.

---

# 21. Notification System

Reference behavior:

- notification bell
- unread count badge
- dropdown
- mark one as read
- mark all as read
- recent notification list

For RailBlock AI, use derived operational alerts and notifications when possible.

---

# 22. Time / Date Context

Reference topbar continuously displays:

- current date
- current time

This can be kept in RailBlock AI as a UI convenience.

Do not misrepresent it as railway operational timing.

---

# 23. Reports / CSV Export Pattern

Reference contains helper logic to build CSV and simple downloadable reports.

Useful RailBlock AI report exports:

- maintenance task CSV
- asset inventory CSV
- train list CSV
- corridor list CSV
- generated block plan CSV
- baseline-vs-optimized KPI CSV

All exports should use real API data.

---

# 24. Recommended RailBlock AI Feature Set Derived From Reference

## Must-have

- operations dashboard
- trains page
- maintenance management
- assets
- corridors
- resources
- schedules
- generate plan
- block schedule/Gantt
- alerts
- settings
- light/dark mode
- search/filtering
- loading/error/empty states
- real API integration
- database persistence

## Strongly recommended

- dashboard upcoming departures
- train status distribution
- corridor network summary
- resource availability bars
- plan comparison card
- operational alert center
- CSV reports
- quick actions
- notification dropdown

## Optional

- admin/system page
- PDF reports
- richer schedule editor
- advanced global search
- configurable notification preferences

---

# 25. Features That Must NOT Be Copied As-Is

The reference contains static/local data for demonstration, including concepts like:

- initialTrains
- schedules
- corridors
- initialMaintenanceTasks
- initialAdminUsers
- initialAuditLogs
- reportChartData
- allAlerts

It also uses local browser persistence for some admin/settings behavior.

RailBlock AI must NOT use these static arrays as operational truth.

Instead:

Reference UX
      ↓
RailBlock AI backend APIs
      ↓
SQLite / real persisted demo data
      ↓
React UI

---

# 26. RailBlock AI-Specific Data Authority Rules

The backend is the source of truth for:

- assets
- maintenance tasks
- defects
- trains
- schedules
- corridors
- resources
- plans
- blocks
- AI predictions
- validation
- analytics

The frontend must never be trusted for:

- AI scores
- optimizer results
- validation status
- plan approval
- critical railway safety state

---

# 27. Light/Dark Mode Requirements

Add application-wide theme support.

Required options:

- Light
- Dark
- System (preferred when practical)

Persist selection.

Theme must affect:

- sidebar
- topbar
- dashboard
- cards
- tables
- filters
- modals
- forms
- charts
- Gantt
- alerts
- settings

Dark theme must NOT simply invert colors.

Use a deliberate dark control-room palette.

---

# 28. Final RailBlock AI UX Goal

The final product should visually communicate:

RAILWAY OPERATIONS
        +
MAINTENANCE INTELLIGENCE
        +
AI PRIORITIZATION
        +
CONSTRAINT OPTIMIZATION
        +
BLOCK PLANNING
        +
HUMAN REVIEW

A judge should understand the product within 10 seconds of seeing the dashboard.

The visual style should feel like a **professional railway operations control center**, not a generic CRUD admin panel.

---

# 29. Implementation Guidance For Another Coding Agent

When adapting these features into the existing RailBlock AI project:

1. Inspect the current code first.
2. Preserve the existing FastAPI + SQLAlchemy + CP-SAT + React architecture.
3. Reuse existing API clients and components where possible.
4. Add missing pages only when they correspond to real backend capabilities.
5. Add backend endpoints only when required by a useful frontend feature.
6. Keep frontend types aligned with Pydantic/API schemas.
7. Never introduce static operational datasets merely to make the UI look populated.
8. Test data persistence after create/update operations.
9. Keep the optimizer and safety constraints deterministic.
10. Run backend tests and frontend build after changes.

---

# 30. Suggested Final Sidebar

```text
RAILBLOCK AI
AI-Powered Railway Operations

MAIN
  Dashboard

OPERATIONS
  Trains
  Schedules
  Corridors
  Resources

MAINTENANCE
  Maintenance
  Assets

PLANNING
  Generate Plan
  Block Schedule

INSIGHTS
  Reports
  Alerts

SYSTEM
  Settings
  Admin/System
```

---

# 31. Suggested Final Demo Journey

```text
Dashboard
   ↓
View network/asset/train/maintenance status
   ↓
Trains
   ↓
View train movements and corridor relationship
   ↓
Maintenance
   ↓
View overdue/high-priority work
   ↓
Generate Plan
   ↓
Weekly / Monthly
   ↓
AI Prioritization
   ↓
CP-SAT Optimization
   ↓
Validation
   ↓
Baseline vs Optimized
   ↓
Block Schedule / Gantt
   ↓
Reports / Alerts
   ↓
Human Review / Approval
```

This is the core UX story that should be implemented around RailBlock AI's existing backend.
