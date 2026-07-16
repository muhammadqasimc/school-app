# School SIS / Reporting App Feature Research

## Context from this codebase
This app already covers:
- Parent dashboard with academic and disciplinary records
- OTP registration via WhatsApp/SMS
- Multi-child support
- Admin tools for users, announcements, messaging, teacher provisioning, sync control, assets, detention notices, sick notes
- Management dashboards and report APIs with charts/filters
- Teacher portal with attendance, discipline, assessments, reports, and parent messaging permissions

## Comparable app patterns observed
Based on common SIS/management patterns seen in products like Gradelink, Infinite Campus, PowerSchool-style portals, and Schoology-style communication workflows, the strongest recurring capabilities are:
- Unified student profile view with attendance, grades, behavior, and communication history
- Fast filtering by year/term/grade/class/subject
- Parent/student mobile-first access and notifications
- Teacher workflows for attendance, messaging, assignments, and report generation
- Admin workflows for permissions, bulk imports, sync, audit, and data quality
- Analytics dashboards with trend charts, drilldowns, and exportable reports

## Concrete feature ideas for this app

### 1. Early-warning / at-risk dashboard
- Flag learners with attendance drops, repeated discipline incidents, or grade declines
- Provide reason tags like "attendance below 85%", "3+ missing assessments", "repeat offender"
- Add one-click drilldown into the learner’s history and contacts

### 2. Parent communication center with templates
- Prebuilt message templates for attendance warnings, fee reminders, missing work, and behavior notes
- Merge fields for learner name, grade, class, teacher, and dates
- Delivery tracking: sent, delivered, read, failed

### 3. Teacher intervention workflow
- Teachers can log interventions after contacting a parent
- Track follow-up date, outcome, and next action
- Show intervention history in learner profile and management reports

### 4. Attendance exception handling
- Mark late, excused, unexcused, medical, transport, and school activity absences
- Allow bulk reasons, notes, and attachments
- Auto-escalate chronic absenteeism to admin/manager views

### 5. Comment bank and term report builder
- Reusable comments for behavior, work habits, and subject performance
- Generate term report comments from selectable rubric tags
- Export-ready report cards or narrative summaries

### 6. Student profile 360 view
- Single page combining attendance, grades, discipline, notes, contacts, messages, and documents
- Timeline of events across terms/years
- Quick actions: message parent, add note, log intervention, print summary

### 7. Bulk import and data validation
- CSV import for learners, classes, teacher assignments, and contacts
- Validation preview with row-level errors before commit
- Duplicate detection and merge suggestions

### 8. Mobile-first notifications
- Optional WhatsApp/SMS push for absence alerts, announcements, and urgent notices
- Notification preferences by channel and priority
- Quiet hours / opt-out controls

### 9. Report scheduling and subscriptions
- Save report filters and schedule weekly/monthly delivery to staff
- Email or downloadable PDF exports
- Role-based visibility for principals, HODs, and admins

### 10. Audit log and change history
- Track who changed grades, attendance, permissions, announcements, and sync settings
- Searchable audit trail with before/after values
- Useful for compliance and troubleshooting

### 11. More actionable analytics
- Compare current term vs previous term and prior year automatically
- Class/subject heatmaps for weak performance areas
- Trend lines for attendance and discipline by grade

### 12. Workflow queues for admin staff
- Unified queue for approvals: profile changes, sick notes, disciplinary cases, message moderation
- Statuses: new, in review, approved, rejected, escalated
- Assignment to staff members with due dates

## Best-fit ideas for this repo specifically
Priority recommendations based on current architecture:
1. Early-warning dashboard
2. Parent communication templates + delivery tracking
3. Student profile 360 view
4. Attendance exception handling
5. Audit log
6. Bulk import + validation

## Suggested next implementation slices
- Add an at-risk learner API and dashboard card to management home
- Extend communication center with message templates and status history
- Expand learner profile page with a cross-module activity timeline
- Add attendance reason codes and exception workflow
- Introduce a simple audit table for key admin actions
