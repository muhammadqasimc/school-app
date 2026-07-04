# MDB Core Join Map (Recommended)

This is a practical join guide for the highest-value data flows in this MDB so field selection stays consistent across features and reports.

- Source reference: `MDB_SCHEMA_DOCUMENTATION.md`
- Scope: Learner Profile, Report Card, Parent Contact, Teacher-Class-Subject, Fees/Accounts
- Note: Access FK constraints are not explicitly exposed; joins below are recommended from field naming + table shape.

## 1) Learner Profile (base identity record)

**Primary base table:** `Learner_Info`

**Preferred key**
- `Learner_Info.LearnerID` (stored as text in this DB snapshot)

**Recommended joins**
- `Learner_Info.Class` -> `Classes.ClassId` (current class metadata)
- `Learner_Info.Grade` -> `Classes.Grade` (only when class id is missing; not unique alone)

**Usage notes**
- Treat `Learner_Info.ID` as row identity, but use `LearnerID` for cross-table links.
- Normalize learner IDs before joins (trim and cast if needed) because some tables store learner IDs as integers.

## 2) Report Card / Marks Flow

**Main transactional table:** `ReportMarks`

**Recommended join chain**
1. `ReportMarks.LearnerID` -> `Learner_Info.LearnerID`
2. `ReportMarks.SubjectId` -> `Subjects.Id`
3. `Learner_Info.Class` -> `Classes.ClassId`
4. Optional split detail: `ReportMarksSplits` on:
   - `ReportMarksSplits.LearnerID` = `ReportMarks.LearnerID`
   - `ReportMarksSplits.SubjectID` = `ReportMarks.SubjectId`
   - `ReportMarksSplits.DataYear` = `ReportMarks.Datayear` (normalize naming/case)

**Most useful filters**
- Year: `ReportMarks.Datayear`
- Reporting cycle/term: `ReportMarks.ReportId` and/or `ReportMarks.CASSTerm`
- Cohort scoping: `Learner_Info.Grade`, `Learner_Info.Class`

## 3) Parent Contact Flow

**Relationship bridge:** `Parent_Child`

**Recommended join chain**
1. `Learner_Info.LearnerID` -> `Parent_Child.Learnerid`
2. `Parent_Child.ParentId` -> `Parent_Info.ParentID`

**Role fields to use**
- Contact and identity: `Parent_Info.FName`, `Parent_Info.SName`, `Parent_Info.Tel1`, `Parent_Info.Tel2`, `Parent_Info.EMail`
- Relationship semantics: `Parent_Child.Relation`, `Parent_Child.Resides`, `Parent_Child.AccPayer`

**Usage notes**
- `Parent_Child.ChildId` appears available, but `Learnerid` aligns better to core learner links.
- Parents can map to multiple learners; design queries with one-to-many in mind.

## 4) Teacher-Class-Subject Allocation Flow

**Main assignment table:** `Educatorgroups`

**Recommended join chain**
1. `Educatorgroups.EducatorId` -> `Educators.EdID`
2. `Educatorgroups.SubjectId` -> `Subjects.Id`
3. Class alignment:
   - Prefer `Educatorgroups.TimetableClass` to match class labels where used
   - Or derive structure via `Classes` using grade + class naming conventions

**Homeroom/register teacher pattern**
- `Educators.RegisterClass` can be used for register class ownership.
- For timetable-based teaching loads, prioritize `Educatorgroups`.

## 5) Fees / Accounts / Cashbook Flow

This schema appears to separate:
- **Family/parent responsibility** in `Parent_Child` / `Parent_Info`
- **Debtor transactions** in `DebtorsTrans`
- **Receipts/deposits** in `Receipt_Info` and `DepositInfo`

**Recommended operational links**
- Cashbook stitching: `DebtorsTrans.TransNum` <-> `Receipt_Info.TransNo` <-> `DepositInfo.TransNo` (when reconciling ledger events)
- Account key handling:
  - `DebtorsTrans.DebAcc` is likely the debtor account number key
  - `DepositInfo.AccNumber` and `BankReceipt.AccNumber` are likely bank/account references

**Important caution**
- No explicit debtor master table was confirmed in this pass, so link `DebAcc` to parent/family entities only after validating account mapping in live data samples.
- Use `Parent_Child.FamilyCode` and payer flags (`AccPayer`) as candidate business keys for family billing context.

## Cross-Cutting Join Safety Rules

- Prefer ID joins over names (`...ID`, `...Id`) wherever available.
- Standardize ID datatypes in queries:
  - `LearnerID` is mixed text/int across tables.
  - Cast both sides to text for safest Access joins when uncertain.
- Always include year/period predicates on transactional tables:
  - `DataYear`/`Datayear`, `Year`, `Month`, `ReportId`, `CASSTerm`.
- For person tables with status fields, filter active rows where required:
  - `Learner_Info.Status`, `Parent_Child.Status`, `Educators.Status`.

## Quick Starter Query Shapes

Use these as patterns (not exact production SQL):

1. **Learner + Parent contacts**
- `Learner_Info` -> `Parent_Child` -> `Parent_Info`

2. **Learner report view**
- `Learner_Info` -> `ReportMarks` -> `Subjects` (+ `Classes`)

3. **Teacher subject allocations**
- `Educators` -> `Educatorgroups` -> `Subjects`

4. **Finance reconciliation slice**
- `DebtorsTrans` -> `Receipt_Info` -> `DepositInfo` (by transaction number/date window)

