# Reporting App — All Routes

> Generated from `app.py` — 51 routes total (27 page/redirect routes + 24 API/data routes)

---

## Page Routes

| # | Route | Function | Methods | Auth | Description |
|---|-------|----------|---------|------|-------------|
| 1 | `/` | `index()` | GET | No | **Homepage** — Renders the landing page with active slideshow images. |
| 2 | `/login` | `login()` | GET, POST | No | **Login page** — Authenticates users (admin, parent, teacher). Rate-limited to 5/min. Redirects based on user role on success. |
| 3 | `/register` | `register()` | GET, POST | No | **Parent registration** — Step 1: enter phone number to start OTP-based registration. |
| 4 | `/register/verify` | `register_verify()` | GET, POST | No | **Registration OTP verification** — Step 2: enter the OTP sent via WhatsApp/SMS. |
| 5 | `/register/set-password` | `register_set_password()` | GET, POST | No | **Set password** — Step 3: choose a password after OTP verification. |
| 6 | `/forgot-password` | `forgot_password()` | GET, POST | No | **Forgot password** — Step 1: enter phone to receive password reset OTP. |
| 7 | `/forgot-password/verify` | `forgot_password_verify()` | GET, POST | No | **Forgot password OTP** — Step 2: verify reset OTP. |
| 8 | `/forgot-password/set-password` | `forgot_password_set_password()` | GET, POST | No | **Reset password** — Step 3: set new password after OTP verification. |
| 9 | `/reset-password` | `reset_password()` | GET, POST | Login | **Force password reset** — First-login password change for new users. |
| 10 | `/dashboard` | `dashboard()` | GET | Login | **Parent dashboard** — Main learner dashboard showing academics, attendance, finance, and disciplinary summary for the active child. |
| 11 | `/dashboard/select-learner` | `select_learner()` | POST | Login | **Switch learner** — Changes the active child for multi-learner parent accounts. |
| 12 | `/logout` | `logout()` | GET | Login | **Logout** — Clears session and logs the user out. |
| 13 | `/portals` | `portal_select()` | GET | Login | **Portal selector** — Landing page for manager accounts to choose between Parent, Management, or Teacher portals. |
| 14 | `/portals/parent` | `choose_parent_portal()` | POST | Login | **Switch to Parent portal** — Sets session mode to parent view (for manager accounts). |
| 15 | `/portals/management` | `choose_management_portal()` | POST | Login | **Switch to Management portal** — Enables management reporting dashboard. |
| 16 | `/portals/teacher` | `choose_teacher_portal()` | POST | Login | **Switch to Teacher portal** — Activates teacher-specific interface. |
| 17 | `/teacher` | `teacher_dashboard()` | GET | Login | **Teacher dashboard** — Main page for educator accounts with attendance, discipline, assessments, and reports tools. |
| 18 | `/management` | `management_dashboard()` | GET | Login | **Management dashboard** — Management portal home with reporting KPIs and navigation to all management reports. |
| 19 | `/admin` | `admin_dashboard()` | GET | Login | **Admin dashboard** — System admin page (admin-only, 403 for others). |
| 20 | `/management/report/<report_key>` | `management_report(report_key)` | GET | Login | **Management report pages** — Renders individual management reports by key. Keys include: `finance-overview`, `educator-staff`, `non-educator-staff`, `general-overview`, `principal-overview`, `attendance`, `learner-chart-report`, `school-achievement-report`, `learner-promotion-rate`, `enrolment-by-year-trend`, `subject-achievement-insights`, `term-to-date-insights`, `mark-schedules`, `academics-previous-year-comparison`, `average-academics-previous-year-comaparison`, `analysis`, `distribution-results-per-grade-per-subject`, `averages-per-subject-per-grade`, `results-per-grade-subject`, `achievement-promotion-analysis`, `learner-movement`, `result-analysis`, `top3`. |
| 21 | `/parent/learner-profile` | `parent_learner_profile()` | GET | Login | **Learner profile page** — Shows the active child's personal details (name, grade, contact info, address). |
| 22 | `/parent/learner-profile/submit-change` | `parent_submit_learner_profile_change()` | POST | Login | **Submit profile change** — Allows parents to request updates to their child's profile info. |

---

## API Routes (Parent Portal)

| # | Route | Function | Description |
|---|-------|----------|-------------|
| 23 | `/api/learner-profile` | `api_learner_profile()` | **GET learner profile data** — Returns JSON with the active learner's name, surname, ID, grade, and other personal info. |
| 24 | `/api/academics-filters` | `api_academics_filters()` | **GET academics filter options** — Returns available years, terms, grades, and subjects for filtering academic results. |
| 25 | `/api/academics` | `api_academics()` | **GET academic results** — Returns marks/grades for the active learner, filterable by year, term, grade, and subject. |
| 26 | `/api/subject-details` | `api_subject_details()` | **GET subject breakdown** — Detailed per-subject performance data (scores, percentages, assessments) for a specific subject/year/term. |
| 27 | `/api/attendance-filters` | `api_attendance_filters()` | **GET attendance filter options** — Returns available years and grades for filtering attendance records. |
| 28 | `/api/attendance` | `api_attendance()` | **GET attendance records** — Returns attendance stats (days present/absent, late arrivals) filterable by year and grade. |
| 29 | `/api/finance` | `api_finance()` | **GET financial info** — Returns fee statements: annual fee, total paid, outstanding balance, and payment history for the learner. |
| 30 | `/api/disciplinary` | `api_disciplinary()` | **GET disciplinary records** — Returns disciplinary incidents and summary stats for the learner, filterable by year. |
| 31 | `/api/disciplinary/documents` | `api_disciplinary_documents()` | **GET disciplinary documents** — Returns associated disciplinary document files (PDFs/evidence). |

---

## API Routes (Management Portal)

| # | Route | Function | Description |
|---|-------|----------|-------------|
| 32 | `/api/management-report` | `api_management_report()` | **GET generic report data** — Returns JSON payload for any management report type identified by `report_key` query param. |
| 33 | `/api/management-report-filters` | `api_management_report_filters()` | **GET report filter options** — Returns available years, terms, phases, grades, subjects, and schools for management report filtering. |
| 34 | `/api/management-distribution-results` | `api_management_distribution_results()` | **GET distribution results** — Grade/subject mark distribution data showing how learners are spread across achievement bands. |
| 35 | `/api/management-averages-per-subject-per-grade` | `api_management_averages_per_subject_per_grade()` | **GET averages by subject & grade** — Average marks per subject broken down by grade level. |
| 36 | `/api/management-results-per-grade-subject` | `api_management_results_per_grade_subject()` | **GET results per grade/subject** — Individual learner results grouped by grade and subject. |
| 37 | `/api/management-analysis` | `api_management_analysis()` | **GET analysis blocks** — Analytical breakdowns (pass rates, performance bands, subject comparisons) per grade. |
| 38 | `/api/management-learner-movement` | `api_management_learner_movement()` | **GET learner movement data** — Information on learners who dropped out or are repeating a grade. |
| 39 | `/api/management-top3` | `api_management_top3()` | **GET top learners** — Returns the top N learners (default 3, configurable 1-20) by average mark for the selected year/term. |
| 40 | `/api/management-academics-previous-year-comparison/filters` | `api_management_academics_previous_year_comparison_filters()` | **GET previous-year comparison filters** — Filter options for comparing academic performance with the prior year. |
| 41 | `/api/management-academics-previous-year-comparison/preview` | `api_management_academics_previous_year_comparison_preview()` | **GET previous-year comparison data** — Year-over-year academic performance comparison preview. |
| 42 | `/api/management-average-academics-previous-year-comaparison/filters` | `api_management_average_academics_previous_year_comparision_filters()` | **GET average comparison filters** — Filter options for average academics year-over-year comparison. |
| 43 | `/api/management-average-academics-previous-year-comaparison/preview` | `api_management_average_academics_previous_year_comparision_preview()` | **GET average comparison data** — Year-over-year average academics comparison preview. |
| 44 | `/api/management-result-analysis` | `api_management_result_analysis()` | **GET result analysis data** — CAPS-style result analysis with pass/fail counts per subject per phase (Foundation, Intermediate, Senior, FET). |
| 45 | `/api/management-achievement-promotion-analysis` | `api_management_achievement_promotion_analysis()` | **GET achievement/promotion analysis** — Promotion rate data showing how many learners meet promotion requirements per grade. |
| 46 | `/api/management-result-analysis/pdf` | `api_management_result_analysis_pdf()` | **GET result analysis PDF** — Generates and downloads a formatted PDF report of the result analysis. |
| 47 | `/api/management-result-analysis/xlsx` | `api_management_result_analysis_xlsx()` | **GET result analysis XLSX** — Generates and downloads an Excel spreadsheet of the result analysis data. |
| 48 | `/api/management-mark-schedules/filters` | `api_management_mark_schedules_filters()` | **GET mark schedule filter options** — Available filters (year, term, grade, subject) for generating mark schedules. |
| 49 | `/api/management-mark-schedules/preview` | `api_management_mark_schedules_preview()` | **GET mark schedule preview** — Previews mark schedule data (subject scores, averages, pass/fail counts) before PDF export. |
| 50 | `/api/management-mark-schedules/pdf` | `api_management_mark_schedules_pdf()` | **GET mark schedule PDF** — Generates and downloads a formatted PDF mark schedule with learner scores per subject and summary stats. |

---

## Other Registered Reports (rendered via `/management/report/<report_key>`)

These 23 report templates are rendered through the dynamic `management_report()` handler:

| Report Key | Title | Description |
|------------|-------|-------------|
| `finance-overview` | Finance Overview | School financial overview with fees, payments, and outstanding balances |
| `educator-staff` | Educator Staff Profile | Staff profile data for teaching personnel |
| `non-educator-staff` | Non-Educator Staff Profile | Staff profile data for non-teaching personnel |
| `general-overview` | General Overview | High-level school performance overview |
| `principal-overview` | Principal Overview | Principal's dashboard with key metrics |
| `attendance` | Attendance | School-wide attendance statistics |
| `learner-chart-report` | Learner Chart Report | Visual chart report on learner data |
| `school-achievement-report` | School Achievement Report | Overall school academic achievement report |
| `learner-promotion-rate` | Learner Promotion Rate | Percentage of learners promoted to next grade |
| `enrolment-by-year-trend` | Enrolment by Year Trend | Historical enrolment trend data |
| `subject-achievement-insights` | Subject Achievement Insights | Deep-dive into subject-level performance |
| `term-to-date-insights` | Term-to-Date Insights | Current term performance snapshot |
| `mark-schedules` | Mark Schedules | Full mark schedule export (PDF/XLSX via API) |
| `academics-previous-year-comparison` | Academics Previous Year Comparison | Year-over-year academic comparison |
| `average-academics-previous-year-comaparison` | Average Academics Previous Year Comaparison | Year-over-year average comparison |
| `analysis` | Analysis | General analysis dashboard |
| `distribution-results-per-grade-per-subject` | Distribution Results per Grade per Subject | Mark distribution across grades and subjects |
| `averages-per-subject-per-grade` | Averages per Subject per Grade | Subject averages by grade level |
| `results-per-grade-subject` | Results per Grade/Subject | Individual learner results by grade and subject |
| `achievement-promotion-analysis` | Achievement/Promotion Analysis | Promotion eligibility analysis |
| `learner-movement` | Learners who dropped Out or are Repeating a Grade | Learner attrition and grade repetition tracking |
| `result-analysis` | Result Analysis | CAPS-style phase-based result analysis with PDF/XLSX export |
| `top3` | Top 3 | Top-performing learners ranking |

---

## Summary

- **Page routes (HTML rendered):** 22 routes
- **API routes (JSON responses):** 28 routes (8 parent-portal + 20 management-portal)
- **Total registered Flask routes:** 50
- **Management report templates served:** 23 dynamic report types
- **Auth patterns:** Most routes require `@login_required`. Management API routes additionally check `_management_user_can_access_reports()`. Parent portal routes check feature-level permissions via `_parent_portal_feature_allowed()`.