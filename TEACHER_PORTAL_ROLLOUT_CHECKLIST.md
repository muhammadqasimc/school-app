# Teacher Portal Rollout Checklist

## Pilot Preparation
- Enable teacher role for 3 pilot users in `Admin -> Users`.
- Assign at least one class per pilot teacher.
- Verify teacher permissions (attendance, discipline, assessments, reports).
- Set term locks to unlocked for pilot term/year.

## QA Verification
- First-time teacher login via EdID redirects to OTP bootstrap.
- OTP verify + set-password flow completes.
- Teacher dashboard and all teacher pages render.
- Save endpoints return success for attendance/discipline/assessments.
- Messaging endpoint blocked when permission is disabled.
- HOD/Principal role shows leadership scope in dashboard.

## Security and Audit
- Confirm write endpoints are CSRF-protected and rate-limited.
- Confirm audit records are created in `teacher_audit_log`.
- Confirm term locks return HTTP 423 on locked modules.

## Rollback Controls
- Revoke `is_teacher` for affected users.
- Disable messaging permission (`can_teacher_message_parents`) globally/user-level.
- Lock attendance/discipline/assessments by term via admin term-lock form.

## Production Rollout
- Run pilot for one week.
- Expand by grade or department.
- Monitor support tickets and audit logs daily for two weeks.
