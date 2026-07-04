# MDB Schema & Relationship Documentation

- Source MDB: `C:\Users\User\Documents\Reporting_app\Reporting App\KISMET SECONDARY 2026  JAN (1).mdb`
- Generated: `2026-04-09 08:58:01`
- Total tables (excluding `MSys*`): `399`
- Inferred relationships: `455`
- Tables with metadata read issues: `109`

## How to Use This Document

- Use **Table Dictionary** to find fields and datatypes quickly.
- Use **Inferred Relationships** to choose join keys safely.
- Use **Domain Groupings** to understand which tables collaborate in each workflow.
- Relationship confidence is heuristic (Access metadata did not expose FK constraints directly).
- Some legacy tables had unreadable metadata; those are listed in **Metadata Read Issues**.

## Metadata Read Issues

- `Absentees`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `AbsenteeStatistics`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `AccCategories`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `AccountInfo`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `ActionCodeList`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `BankPay`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `BankReceipt`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `BankState`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `BarrierCodeList`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `CancelLog`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `CASubjects`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `CASubjectSections`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ChartAccountsTable`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `ChartofAccountDetails`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ChartofAccountsGE`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `ChartOfAccountsNC`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ChartofAccountsWC`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Cheque_Pay`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ChequeNum`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Classes`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `CriteriaActivities`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `CurrentPeriod`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `CycleInfo`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DAS`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `DASCategories`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `DASDevelopmentneedCategories`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `DebtorsTrans`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DeletedItems`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DeleteLog`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DepositBooks`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DepositInfo`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Disabilities`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Disciplinarycodelist`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DisciplinaryConsequences`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DisciplinaryLearnerMisconduct`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `DisciplinaryRecords`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Educators`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `EducatorSubjectsTaught`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `EducatorTeachingHours`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `EducatorTeachingLevel`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `FeederSchools`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `FeeExemptions`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `FormLock`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `General_Info`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `GLTrans`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Inventory`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `InventoryLocation`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `InventoryQuantities`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `InventoryWriteOff`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `Journals`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `Learner_Info`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `LearnerApplications`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `LearnerAttendance`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `LearnerCass`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `LearnerCTA`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `LearnerMovement`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `LearnerPerformance`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `LearnerSubjectLanguages`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `LearnerSupportMaterials`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `LearningBarriers`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ModeTransport`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Mortality`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `OBEEvaluations`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `Parent_Child`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `Parent_Info`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `PettyCashAccounts`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `PettyPay`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `PhysicalRooms`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `PromotionDescriptions`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `PromotionsExport`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 8-9: illegal UTF-16 surrogate
- `Receipt_Info`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ReportCycles`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `ReportMarks`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SchoolAdministration`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolBoarding`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 8-9: illegal UTF-16 surrogate
- `SchoolCommunityParents`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolCurriculum`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SchoolFees`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolFinance`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolGrades`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SchoolManagement`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolProvincialSupport`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolResources`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SchoolSubVenues`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolTerms`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SchoolUniform`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SchoolUniformParts`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SchoolVenues`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `ServiceProvider`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SGBPolicy`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SGBSalaries`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `SportFields`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `StaffAbsentees`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `StaffAbsenteeStatistics`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `StaffLeave`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `StaffMembers`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `SubjectCriteria`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SubjectOutcomes`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `Subjects`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `SubjectSpecialisation`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `TeachingLanguages`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `TieClasses`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 32-33: illegal encoding
- `TieEducators`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `TieGroups`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 32-33: illegal encoding
- `TieSubjects`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `TimetableInputs`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 16-17: illegal UTF-16 surrogate
- `TrainingAttended`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate
- `TransactionTypes`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 80-81: illegal UTF-16 surrogate
- `VenueTypes`: used SELECT fallback after metadata decode error: 'utf-16-le' codec can't decode bytes in position 48-49: illegal UTF-16 surrogate

## Domain Groupings

### Academic & Assessment Domain

- Tables: `54`
- `12_2_1_Old_ReportMarks`, `12_2_1_Old_Subjects`, `12_2_1_Old_SubjectSets`, `12_2_1_Old_SubjectSpecialisation`, `17_3_0_ReportMarks`, `17_3_0_ReportMarksSplits`, `Ana2012FinalMarks`, `Ana2012TotalMarksPerGrade`, `AnaGrade1To3Marks`, `AnaGrade4To9Marks`, `CASubjects`, `CASubjectSections`, `CriteriaAssessments`, `CriterionOutcomes`, `ELNA_Assessments`, `ELNA_AssessmentScore`, `GlobalSecMarks`, `GradeSubjectSets`, `GroupSubjects`, `LsmAreasSubjects`, `LsmItemsSubjects`, `ReportComments`, `ReportCommentsSkills`, `ReportCommentsVA`, `ReportCycles`, `ReportGeneralComments`, `ReportLanguages`, `ReportMarks`, `ReportMarksSplits`, `ReportOutcomeMarks`, `ReportsMortalityCategories`, `SIAS_Health_Professional_Report`, `SNE_Assessment_Supp_Req`, `SNE_Assessment_Supp_Req_Rating`, `SNE_Health_Professional_Report`, `SNE_lu_Assessment_Support_Area`, `SubjectAverages`, `SubjectCriteria`, `SubjectCriteriaActivities`, `SubjectCriteriaDeviations`, `SubjectCriteriaTypes`, `SubjectDept_Info`, `SubjectMainTopics`, `SubjectOutcomes`, `Subjects`, `SubjectSets`, `SubjectsMusicInstruments`, `SubjectsOfficial`, `SubjectsOfficial_OLD`, `SubjectsOfficialSettings`, `SubjectSpecialisation`, `SubjectsReportSplits`, `SubjectsSettings`, `TieSubjects`

### Class/Grade Structure Domain

- Tables: `6`
- `Classes`, `ClassTT`, `SchoolGrades`, `SNE_Factors_Classroom`, `SNE_Survey2008GradeByPregnant`, `TieClasses`

### Configuration/Lookup Domain

- Tables: `9`
- `ActionCodeList`, `BarrierCodeList`, `DemeritMeritSettings`, `DetentionNotificationSettings`, `Disciplinarycodelist`, `LetterHeadSettings`, `ReasonCodes`, `Settings`, `Weeksetup`

### Educator/Staff Domain

- Tables: `36`
- `12_2_1_Old_Educatorgroups`, `18_1_0_Old_Educator_Appraisal`, `18_1_0_Old_Educator_DSG`, `18_1_0_Old_Educator_Final_Score`, `18_1_0_Old_Educator_Final_Score_Comment`, `18_1_0_Old_Educator_Improvement_Plan`, `18_1_0_Old_Educator_Level`, `18_1_0_Old_Educator_PGP`, `Educator_CalendarTerms`, `Educator_CalendarWeekSetup`, `Educatorgroups`, `EducatorQualificationTypes`, `Educators`, `EducatorSubjectsTaught`, `EducatorTeachingHours`, `EducatorTeachingLevel`, `EducatorTT`, `IQMS_Educator_Appraisal`, `IQMS_Educator_DSG`, `IQMS_Educator_FinalScore`, `IQMS_Educator_FinalScoreComments`, `IQMS_Educator_ImprovementPlan`, `IQMS_Educator_PGP`, `IQMS_Educator_PGP_Subjects`, `RegisterEducators`, `SNE_Survey2008EducatorINSET`, `SNE_Survey2008EducatorOtherSpecialisation`, `SNE_Survey2008EducatorPhase`, `SNE_Survey2008EducatorSpecialisation`, `Staff_CalendarTerms`, `Staff_CalendarWeekSetup`, `StaffAbsentees`, `StaffAbsenteeStatistics`, `StaffLeave`, `StaffMembers`, `TieEducators`

### Finance Domain

- Tables: `6`
- `FeederSchools`, `FeeExemptions`, `Fees`, `SchoolFees`, `SchoolFinance`, `SNE_Survey2008SchoolFees`

### Learner Domain

- Tables: `51`
- `12_2_1_Old_LearnerPromotion`, `12_2_1_Old_LearnerSubjects`, `17_3_0_LearnerCass`, `17_3_0_LearnerPromotion`, `DisciplinaryLearnerMisconduct`, `ELNA_LearnerRegistration`, `ExtraMuralsCompEventsLearners`, `ExtraMuralsLearners`, `Learner_Info`, `LearnerApplications`, `LearnerAttendance`, `LearnerCass`, `LearnerCassActivities`, `LearnerClasses`, `LearnerCTA`, `LearnerDeworming`, `LearnerExamRegistration`, `LearnerExamRegistrationSubjects`, `LearnerExamRegistrationV2`, `LearnerMAttendance`, `LearnerMedConTypes`, `LearnerMedicals`, `LearnerMedications`, `LearnerMentors`, `LearnerMentorshipCats`, `LearnerMentorships`, `LearnerMentorTypes`, `LearnerMovement`, `LearnerPerformance`, `LearnerProgression`, `LearnerPromotion`, `LearnerPromotionDefaultComments`, `LearnerSubjectLanguages`, `LearnerSubjects`, `LearnerSupportMaterials`, `LearnerTranferCard`, `SIAS_Learner_Action_Plan`, `SIAS_Learner_Action_Plan_Signature`, `SIAS_Learner_Background_Info`, `SIAS_Learner_Profile`, `SIAS_Learner_Support_Needs`, `SIAS_LearnerDetails`, `SNE_Learner_Background_Info`, `SNE_Learner_Impairment_Area`, `SNE_Learner_Supp_Needs`, `SNE_Learner_Support_Needs`, `SNE_Survey2008LearnerAge`, `SNE_Survey2008LearnerDeceasedParent`, `SNE_Survey2008LearnerEnrollment`, `SNE_Survey2008LearnerLanguage`, `SNE_Survey2008LearnerTransfers`

### Other/Uncategorized Domain

- Tables: `225`
- `'mdb-import$'_ImportErrors`, `18_1_0_Old_lu_Perfomance_Criteria`, `18_1_0_Old_lu_PerformanceStandards`, `18_1_0_Old_PM_CheckList`, `18_1_0_SGBFunctions`, `Absentees`, `AbsenteesPeriods`, `AbsenteesReasons`, `AbsenteeStatistics`, `AccCategories`, `AccountInfo`, `Ana2012EvaluationLevels`, `BankPay`, `BankReceipt`, `BankRecon`, `BankState`, `BankStateDetails`, `BusRoutes`, `Bustickets`, `ChartAccountsTable`, `ChartofAccountDetails`, `ChartofAccountsEC`, `ChartofAccountsGE`, `ChartofAccountsKZN`, `ChartOfAccountsNC`, `ChartofAccountsWC`, `Cheque_Pay`, `ChequeNum`, `Comments`, `CostCentres`, `Countries`, `CriteriaActivities`, `CurrentPeriod`, `CycleInfo`, `DAS`, `DASCategories`, `DASDevelopmentneedCategories`, `DebtorsTrans`, `DeletedItems`, `DepositBooks`, `DepositInfo`, `Deworming`, `DewormingQue`, `Disabilities`, `DisciplinaryConsequences`, `DisciplinaryRecords`, `Districts`, `ELNA_Assessor`, `ELNA_AssessorInstructionV1`, `ELNA_FinalScore`, `ELNA_Intructions`, `ELNA_Items`, `Events`, `ExtraMurals`, `ExtraMuralsAccolades`, `ExtraMuralsCompetitions`, `ExtraMuralsCompEvents`, `ExtraMuralsCompEventsTeams`, `ExtraMuralsHouses`, `ExtraMuralsHousesLinks`, `ExtraMuralsTeams`, `ExtraMuralsTypes`, `FormLetters`, `FormLock`, `FormTemplates`, `General_Info`, `GlobalSec`, `GlobalSecMenus`, `GlobalSecProfiles`, `GlobalSecRights`, `GLTrans`, `GovMembers`, `GovMemberShips`, `GovPolicies`, `GovPoliciesRecords`, `GovTrainingCategories`, `GovTrainingCourses`, `GovTrainingReceived`, `GovTrainingRequired`, `HealthConsent`, `Hostels`, `ICTAsistiveDeviceRecords`, `ICTCourseData`, `ICTdata`, `ICTEConnectivityRecords`, `ICTElectronicContentRecords`, `ICTInfrastuctureRecords`, `ICTSecuritydata`, `Info`, `InstructionLanguages`, `Inventory`, `InventoryLocation`, `InventoryQuantities`, `InventoryVenueTypes`, `InventoryWriteOff`, `IQMS_PerformanceCriterias`, `IQMS_PerformanceLevels`, `IQMS_PerformanceStandards`, `IQMS_PM_CheckList`, `IQMS_PM_CheckListItems`, `Journals`, `LearningBarriers`, `Look_UpGE`, `Look_UpNC`, `Look_UpWC`, `LsmAreas`, `LsmAreasGroups`, `LsmAuthors`, `LsmCategories`, `LsmItems`, `LsmLanguages`, `LsmLoans`, `LsmManufacturers`, `LsmPublishers`, `LsmQuantities`, `LsmWriteOff`, `LuritsDatabaseDeployment`, `ModeTransport`, `MonthlyBudgets`, `Mortality`, `MultipleDisabilities`, `NonInstructionalAreas`, `OBEEvaluations`, `OtherPurposeAreas`, `PAMDisabilityCategory`, `Paste Errors`, `PastelCompanyPath`, `PastelCustomerCategory`, `PettyCashAccounts`, `PettyPay`, `PettyVoucherNumbers`, `PhysicalInfrastructure`, `PhysicalRooms`, `PromotionDescriptions`, `Promotions`, `PromotionsExport`, `Qualifications`, `QualificationsTypes`, `Receipt_Info`, `ReceiptBooks`, `Religion`, `Requisitions`, `SchoolAdministration`, `SchoolBoarding`, `SchoolCurriculum`, `SchoolGovBodies`, `SchoolInfo`, `SchoolManagement`, `SchoolProvincialSupport`, `SchoolResources`, `SchoolSafety`, `SchoolSubVenues`, `SchoolTerms`, `SchoolUniform`, `SchoolUniformParts`, `SchoolVenues`, `SeriousIncidents`, `SeriousIncidentsTypes`, `ServiceProvider`, `SGBFunctionAverage`, `SGBFunctions`, `SGBPolicy`, `SGBSalaries`, `SIAS_AreaofFunctionalLimmitation`, `SIAS_Areas_Needing_Ongoing_support`, `SIAS_Areas_Of_Concern`, `SIAS_Criteria_For_Selection`, `SIAS_Curriculum_Intervention`, `SIAS_Curriculum_Intervention_AdditionalSupport_And_Plan`, `SIAS_DBST_Checklist`, `SIAS_DBST_Review`, `SIAS_DBST_Support_Request`, `SIAS_Disabilities_Categories`, `SIAS_EarlyIntervention`, `SIAS_Factors_Community`, `SIAS_Frequency_Of_Provision`, `SIAS_IndividualSupportPlan`, `SIAS_SBST_Review`, `SIAS_School_Action_Plan`, `SIAS_Source`, `SIAS_Strength_and_Need`, `SIAS_Strength_Needs_Areas`, `SIAS_Suport_Needs`, `SIAS_Support_Areas`, `SNE_Action_Review`, `SNE_Criteria_For_Selection`, `SNE_Criteria_For_Selection_Other`, `SNE_DBST_Review_ILST_Request`, `SNE_DBST_Support_Strategy`, `SNE_Factors_Community`, `SNE_Factors_School`, `SNE_ILST_Intervention_Records`, `SNE_ISP`, `SNE_Learning_And_Development_Barriers`, `SNE_lu_Activity_Domain_Limit_Desc`, `SNE_lu_Activity_Domain_Sub_Section`, `SNE_lu_AreaID_of_Support`, `SNE_lu_Impairment_Area`, `SNE_lu_ISP_Actions`, `SNE_lu_Sub_Support_Area`, `SNE_lu_Support_Area`, `SNE_Survey2008AssistiveDevice`, `SNE_Survey2008ExtraMural`, `SNE_Survey2008HealthProfessional`, `SNE_Survey2008Mortality`, `SNE_Survey2008OtherAssistiveDevice`, `SNE_Survey2008PopulationGroup`, `SNE_Survey2008Promotions`, `SNE_Survey2008SocialGrant`, `SportFields`, `SSE_Functions`, `SSE_Responsibility`, `SubjMultiGetFrom`, `SubstituteTT`, `SysSessions`, `SysSessionsLocks`, `TaskOutcomes`, `TeachingLanguages`, `TempPromotions`, `TieGroups`, `TimetableInputs`, `TrainingAttended`, `TransactionFiles`, `TransactionTypes`, `VenueTypes`

### Parent/Guardian Domain

- Tables: `3`
- `Parent_Child`, `Parent_Info`, `SchoolCommunityParents`

### System/Audit Domain

- Tables: `9`
- `__Patches`, `AssetMovementHistory`, `CancelLog`, `DeleteLog`, `GlobalSecLoginAttempts`, `GlobalSysLogs`, `PasswordHistory`, `SIAS_Consultation_Logs`, `SysLogs`

## Inferred Relationships

| From Table | From Column | To Table | To Column | Confidence |
|---|---|---|---|---:|
| `InventoryLocation` | `InventoryId` | `Inventory` | `InventoryId` | 16 |
| `InventoryQuantities` | `InventoryID` | `Inventory` | `InventoryId` | 16 |
| `InventoryWriteOff` | `InventoryId` | `Inventory` | `InventoryId` | 16 |
| `12_2_1_Old_Educatorgroups` | `EducatorGroupID` | `Educatorgroups` | `EducatorGroupID` | 8 |
| `12_2_1_Old_Educatorgroups` | `EducatorId` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `12_2_1_Old_Educatorgroups` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `12_2_1_Old_LearnerPromotion` | `LearnerId` | `17_3_0_LearnerCass` | `Learnerid` | 8 |
| `12_2_1_Old_LearnerPromotion` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `12_2_1_Old_LearnerSubjects` | `EducatorGroupId` | `12_2_1_Old_Educatorgroups` | `EducatorGroupID` | 8 |
| `12_2_1_Old_LearnerSubjects` | `ID` | `12_2_1_Old_ReportMarks` | `Id` | 8 |
| `12_2_1_Old_LearnerSubjects` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `12_2_1_Old_LearnerSubjects` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `12_2_1_Old_ReportMarks` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `12_2_1_Old_ReportMarks` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `12_2_1_Old_ReportMarks` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `12_2_1_Old_ReportMarks` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `12_2_1_Old_Subjects` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `12_2_1_Old_SubjectSets` | `SubjectID` | `GroupSubjects` | `SubjectID` | 8 |
| `12_2_1_Old_SubjectSpecialisation` | `Educatorid` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `12_2_1_Old_SubjectSpecialisation` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `12_2_1_Old_SubjectSpecialisation` | `Subjectid` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `17_3_0_LearnerCass` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `17_3_0_LearnerCass` | `RecId` | `ExtraMuralsLearners` | `RecID` | 8 |
| `17_3_0_LearnerCass` | `Subjectid` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `17_3_0_LearnerPromotion` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `17_3_0_LearnerPromotion` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `17_3_0_ReportMarks` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `17_3_0_ReportMarks` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `17_3_0_ReportMarks` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `17_3_0_ReportMarks` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `17_3_0_ReportMarksSplits` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `17_3_0_ReportMarksSplits` | `RecId` | `ExtraMuralsLearners` | `RecID` | 8 |
| `17_3_0_ReportMarksSplits` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `18_1_0_Old_Educator_Appraisal` | `EdID` | `18_1_0_Old_Educator_DSG` | `EdID` | 8 |
| `18_1_0_Old_Educator_DSG` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `18_1_0_Old_Educator_Final_Score` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `18_1_0_Old_Educator_Final_Score_Comment` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `18_1_0_Old_Educator_PGP` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `18_1_0_Old_PM_CheckList` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `Absentees` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Absentees` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `Absentees` | `ReasonID` | `AbsenteesReasons` | `ReasonID` | 8 |
| `AbsenteesPeriods` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `AbsenteesPeriods` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `AbsenteeStatistics` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `AccountInfo` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ActionCodeList` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Ana2012EvaluationLevels` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Ana2012FinalMarks` | `ClassID` | `Classes` | `ClassId` | 8 |
| `Ana2012FinalMarks` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Ana2012FinalMarks` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `AnaGrade1To3Marks` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `AnaGrade4To9Marks` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `BankPay` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `BankReceipt` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `BankRecon` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `BarrierCodeList` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Bustickets` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `CASubjects` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `CASubjectSections` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `ChartAccountsTable` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ChartofAccountsEC` | `AccountId` | `ChartofAccountsGE` | `AccountId` | 8 |
| `ChartofAccountsGE` | `AccountId` | `ChartofAccountsEC` | `AccountId` | 8 |
| `ChartofAccountsKZN` | `AccountId` | `ChartofAccountsEC` | `AccountId` | 8 |
| `ChartOfAccountsNC` | `AccountId` | `ChartofAccountsEC` | `AccountId` | 8 |
| `ChartofAccountsWC` | `AccountId` | `ChartofAccountsEC` | `AccountId` | 8 |
| `Cheque_Pay` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ChequeNum` | `BookId` | `PettyVoucherNumbers` | `BookId` | 8 |
| `CriteriaActivities` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `CriteriaAssessments` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `CriterionOutcomes` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `CurrentPeriod` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DAS` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DASCategories` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DASDevelopmentneedCategories` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DeletedItems` | `ItemId` | `IQMS_PM_CheckListItems` | `ItemID` | 8 |
| `DemeritMeritSettings` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DepositBooks` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DepositInfo` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DetentionNotificationSettings` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Deworming` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DewormingQue` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Disabilities` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Disciplinarycodelist` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DisciplinaryConsequences` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DisciplinaryLearnerMisconduct` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DisciplinaryRecords` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `DisciplinaryRecords` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `Districts` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Educator_CalendarTerms` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Educator_CalendarWeekSetup` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Educatorgroups` | `EducatorGroupID` | `12_2_1_Old_Educatorgroups` | `EducatorGroupID` | 8 |
| `Educatorgroups` | `EducatorId` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `Educatorgroups` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `EducatorQualificationTypes` | `EducatorID` | `EducatorSubjectsTaught` | `EducatorId` | 8 |
| `Educators` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `EducatorSubjectsTaught` | `EducatorId` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `EducatorSubjectsTaught` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `EducatorTeachingHours` | `EducatorId` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `EducatorTeachingLevel` | `EducatorId` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `ELNA_AssessmentScore` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ELNA_FinalScore` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ELNA_LearnerRegistration` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Events` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ExtraMurals` | `ExTypeID` | `ExtraMuralsTypes` | `ExTypeID` | 8 |
| `ExtraMuralsCompetitions` | `ExID` | `ExtraMurals` | `ExID` | 8 |
| `ExtraMuralsCompEvents` | `CompID` | `ExtraMuralsCompetitions` | `CompID` | 8 |
| `ExtraMuralsCompEvents` | `EventID` | `ExtraMuralsCompEventsLearners` | `EventID` | 8 |
| `ExtraMuralsCompEventsLearners` | `EventID` | `ExtraMuralsCompEvents` | `EventID` | 8 |
| `ExtraMuralsCompEventsLearners` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ExtraMuralsCompEventsLearners` | `TeamID` | `ExtraMuralsTeams` | `TeamID` | 8 |
| `ExtraMuralsCompEventsTeams` | `EventID` | `ExtraMuralsCompEvents` | `EventID` | 8 |
| `ExtraMuralsCompEventsTeams` | `TeamID` | `ExtraMuralsTeams` | `TeamID` | 8 |
| `ExtraMuralsHouses` | `HseID` | `ExtraMuralsHousesLinks` | `HseID` | 8 |
| `ExtraMuralsHousesLinks` | `HseID` | `ExtraMuralsHouses` | `HseID` | 8 |
| `ExtraMuralsHousesLinks` | `LinkID` | `Qualifications` | `LinkID` | 8 |
| `ExtraMuralsLearners` | `ExID` | `ExtraMurals` | `ExID` | 8 |
| `ExtraMuralsLearners` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ExtraMuralsLearners` | `TeamID` | `ExtraMuralsTeams` | `TeamID` | 8 |
| `ExtraMuralsTeams` | `ExID` | `ExtraMurals` | `ExID` | 8 |
| `FeederSchools` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `FeeExemptions` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `FormTemplates` | `UserID` | `GlobalSec` | `UserID` | 8 |
| `GlobalSec` | `LinkID` | `Qualifications` | `LinkID` | 8 |
| `GlobalSec` | `ProfID` | `GlobalSecProfiles` | `ProfID` | 8 |
| `GlobalSecLoginAttempts` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `GlobalSecMarks` | `ClassID` | `Classes` | `ClassId` | 8 |
| `GlobalSecMarks` | `GradeID` | `SNE_Survey2008GradeByPregnant` | `Gradeid` | 8 |
| `GlobalSecMarks` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `GlobalSecMarks` | `UserID` | `GlobalSec` | `UserID` | 8 |
| `GlobalSecProfiles` | `ProfID` | `GlobalSecRights` | `ProfID` | 8 |
| `GlobalSecRights` | `ProfID` | `GlobalSecProfiles` | `ProfID` | 8 |
| `GovMembers` | `LinkID` | `Qualifications` | `LinkID` | 8 |
| `GovMemberShips` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `GovMemberShips` | `MemberID` | `GovMembers` | `MemberID` | 8 |
| `GovPolicies` | `PolicyId` | `GovPoliciesRecords` | `PolicyId` | 8 |
| `GovPoliciesRecords` | `PolicyId` | `GovPolicies` | `PolicyId` | 8 |
| `GovTrainingCourses` | `TrainCatID` | `GovTrainingCategories` | `TrainCatID` | 8 |
| `GovTrainingReceived` | `CourseID` | `GovTrainingCourses` | `CourseID` | 8 |
| `GovTrainingReceived` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `GovTrainingReceived` | `MemberID` | `GovMembers` | `MemberID` | 8 |
| `GovTrainingRequired` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `GovTrainingRequired` | `MemberID` | `GovMembers` | `MemberID` | 8 |
| `GovTrainingRequired` | `TrainCatID` | `GovTrainingCategories` | `TrainCatID` | 8 |
| `GradeSubjectSets` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `GroupSubjects` | `GroupId` | `LsmAreasGroups` | `GroupID` | 8 |
| `GroupSubjects` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `HealthConsent` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `Hostels` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ICTAsistiveDeviceRecords` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ICTEConnectivityRecords` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ICTElectronicContentRecords` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ICTInfrastuctureRecords` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Info` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `InstructionLanguages` | `LangID` | `LsmLanguages` | `LangID` | 8 |
| `Inventory` | `InventoryId` | `InventoryLocation` | `InventoryId` | 8 |
| `InventoryLocation` | `VenueId` | `SchoolVenues` | `VenueId` | 8 |
| `InventoryQuantities` | `VenueId` | `SchoolVenues` | `VenueId` | 8 |
| `InventoryWriteOff` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `InventoryWriteOff` | `itemid` | `DeletedItems` | `ItemId` | 8 |
| `InventoryWriteOff` | `VenueId` | `SchoolVenues` | `VenueId` | 8 |
| `IQMS_Educator_Appraisal` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_Educator_Appraisal` | `StandardID` | `IQMS_Educator_ImprovementPlan` | `StandardID` | 8 |
| `IQMS_Educator_DSG` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_Educator_FinalScore` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_Educator_FinalScore` | `StandardID` | `IQMS_Educator_ImprovementPlan` | `StandardID` | 8 |
| `IQMS_Educator_FinalScoreComments` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_Educator_ImprovementPlan` | `StandardID` | `IQMS_PerformanceCriterias` | `StandardID` | 8 |
| `IQMS_Educator_PGP` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_Educator_PGP` | `StandardID` | `IQMS_Educator_ImprovementPlan` | `StandardID` | 8 |
| `IQMS_Educator_PGP_Subjects` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_PerformanceCriterias` | `StandardID` | `IQMS_Educator_ImprovementPlan` | `StandardID` | 8 |
| `IQMS_PerformanceLevels` | `StandardID` | `IQMS_Educator_ImprovementPlan` | `StandardID` | 8 |
| `IQMS_PerformanceStandards` | `StandardID` | `IQMS_Educator_ImprovementPlan` | `StandardID` | 8 |
| `IQMS_PM_CheckList` | `EdID` | `18_1_0_Old_Educator_Appraisal` | `EdID` | 8 |
| `IQMS_PM_CheckList` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `IQMS_PM_CheckListItems` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `Journals` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Learner_Info` | `BusRouteId` | `BusRoutes` | `BusRouteId` | 8 |
| `Learner_Info` | `HseID` | `ExtraMuralsHouses` | `HseID` | 8 |
| `Learner_Info` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Learner_Info` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerCass` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerCass` | `RecId` | `ExtraMuralsLearners` | `RecID` | 8 |
| `LearnerCass` | `Subjectid` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `LearnerCassActivities` | `ActivityID` | `SubjectCriteriaActivities` | `ActivityID` | 8 |
| `LearnerCassActivities` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerCassActivities` | `RecId` | `ExtraMuralsLearners` | `RecID` | 8 |
| `LearnerClasses` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearnerCTA` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerCTA` | `Subjectid` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `LearnerDeworming` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearnerDeworming` | `Linkid` | `Qualifications` | `LinkID` | 8 |
| `LearnerExamRegistration` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerExamRegistrationSubjects` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerExamRegistrationSubjects` | `OfficialSubjectID` | `SubjectsOfficialSettings` | `OfficialSubjectID` | 8 |
| `LearnerExamRegistrationV2` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerMedicals` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerMedicals` | `MedConTypeID` | `LearnerMedConTypes` | `MedConTypeID` | 8 |
| `LearnerMedications` | `MedicalID` | `LearnerMedicals` | `MedicalID` | 8 |
| `LearnerMentors` | `LinkID` | `Qualifications` | `LinkID` | 8 |
| `LearnerMentors` | `TypeID` | `LearnerMentorTypes` | `TypeID` | 8 |
| `LearnerMentorshipCats` | `CatID` | `LsmCategories` | `CatID` | 8 |
| `LearnerMentorships` | `CatID` | `LearnerMentorshipCats` | `CatID` | 8 |
| `LearnerMentorships` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearnerMentorships` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerMentorships` | `MentorID` | `LearnerMentors` | `MentorID` | 8 |
| `LearnerMovement` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearnerProgression` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerPromotion` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerPromotion` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `LearnerPromotionDefaultComments` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearnerSubjects` | `EducatorGroupId` | `12_2_1_Old_Educatorgroups` | `EducatorGroupID` | 8 |
| `LearnerSubjects` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearnerSubjects` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerSubjects` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `LearnerTranferCard` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `LearnerTranferCard` | `LinkID` | `Qualifications` | `LinkID` | 8 |
| `LearningBarriers` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `LearningBarriers` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `Look_UpGE` | `WordId` | `Look_UpNC` | `WordId` | 8 |
| `Look_UpNC` | `WordId` | `Look_UpGE` | `WordId` | 8 |
| `Look_UpWC` | `WordId` | `Look_UpGE` | `WordId` | 8 |
| `LsmAreas` | `AreaID` | `LsmAreasSubjects` | `AreaID` | 8 |
| `LsmAreas` | `GroupID` | `LsmAreasGroups` | `GroupID` | 8 |
| `LsmAreasSubjects` | `AreaID` | `LsmAreas` | `AreaID` | 8 |
| `LsmAreasSubjects` | `SubjID` | `SubjectsOfficial` | `SubjID` | 8 |
| `LsmCategories` | `CatID` | `LearnerMentorshipCats` | `CatID` | 8 |
| `LsmItems` | `AreaID` | `LsmAreas` | `AreaID` | 8 |
| `LsmItems` | `AuthID` | `LsmAuthors` | `AuthID` | 8 |
| `LsmItems` | `CatID` | `LearnerMentorshipCats` | `CatID` | 8 |
| `LsmItems` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `LsmItems` | `LangID` | `InstructionLanguages` | `LangID` | 8 |
| `LsmItems` | `ManuID` | `LsmManufacturers` | `ManuID` | 8 |
| `LsmItems` | `PubID` | `LsmPublishers` | `PubID` | 8 |
| `LsmItemsSubjects` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `LsmItemsSubjects` | `SubjID` | `SubjectsOfficial` | `SubjID` | 8 |
| `LsmLanguages` | `LangID` | `InstructionLanguages` | `LangID` | 8 |
| `LsmLoans` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `LsmQuantities` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `LsmWriteOff` | `ItemID` | `DeletedItems` | `ItemId` | 8 |
| `LsmWriteOff` | `QuantityID` | `LsmQuantities` | `QuantityID` | 8 |
| `ModeTransport` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Mortality` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Mortality` | `Linkid` | `Qualifications` | `LinkID` | 8 |
| `MultipleDisabilities` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `OBEEvaluations` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `PAMDisabilityCategory` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Parent_Child` | `Learnerid` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `Parent_Info` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Parent_Info` | `ParentID` | `Parent_Child` | `ParentId` | 8 |
| `PasswordHistory` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `PettyCashAccounts` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `PettyPay` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `PettyVoucherNumbers` | `BookId` | `ChequeNum` | `BookId` | 8 |
| `Receipt_Info` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReceiptBooks` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Religion` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportComments` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportCommentsSkills` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportCommentsSkills` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ReportCommentsSkills` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `ReportCommentsSkills` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `ReportCommentsVA` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportCommentsVA` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ReportCommentsVA` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `ReportCommentsVA` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `ReportGeneralComments` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportLanguages` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportMarks` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportMarks` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ReportMarks` | `ReportId` | `LetterHeadSettings` | `ReportId` | 8 |
| `ReportMarks` | `SubjectId` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `ReportMarksSplits` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ReportMarksSplits` | `RecId` | `ExtraMuralsLearners` | `RecID` | 8 |
| `ReportMarksSplits` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `ReportOutcomeMarks` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ReportOutcomeMarks` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `ReportOutcomeMarks` | `OutcomeID` | `SubjectOutcomes` | `OutcomeID` | 8 |
| `ReportOutcomeMarks` | `ReportID` | `LetterHeadSettings` | `ReportId` | 8 |
| `ReportOutcomeMarks` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `ReportsMortalityCategories` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Requisitions` | `AccountID` | `ChartofAccountsEC` | `AccountId` | 8 |
| `SchoolGrades` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SchoolSubVenues` | `VenueId` | `SchoolVenues` | `VenueId` | 8 |
| `SchoolTerms` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SeriousIncidents` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `ServiceProvider` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Settings` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SGBSalaries` | `StaffId` | `StaffMembers` | `StaffID` | 8 |
| `SIAS_AreaofFunctionalLimmitation` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Areas_Needing_Ongoing_support` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Areas_Of_Concern` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Areas_Of_Concern` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Consultation_Logs` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Consultation_Logs` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Criteria_For_Selection` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Criteria_For_Selection` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Curriculum_Intervention` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Curriculum_Intervention` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Curriculum_Intervention_AdditionalSupport_And_Plan` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Curriculum_Intervention_AdditionalSupport_And_Plan` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_DBST_Checklist` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_DBST_Checklist` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_DBST_Review` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_DBST_Review` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_DBST_Support_Request` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_DBST_Support_Request` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Disabilities_Categories` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_EarlyIntervention` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_EarlyIntervention` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Factors_Community` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Factors_Community` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Frequency_Of_Provision` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Health_Professional_Report` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Health_Professional_Report` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_IndividualSupportPlan` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_IndividualSupportPlan` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Learner_Action_Plan` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Learner_Action_Plan` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Learner_Action_Plan_Signature` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Learner_Action_Plan_Signature` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Learner_Background_Info` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Learner_Background_Info` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Learner_Profile` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Learner_Profile` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Learner_Support_Needs` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Learner_Support_Needs` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_LearnerDetails` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_LearnerDetails` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_SBST_Review` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_SBST_Review` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_School_Action_Plan` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Source` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Strength_and_Need` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Strength_and_Need` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SIAS_Strength_Needs_Areas` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Suport_Needs` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SIAS_Support_Areas` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Action_Review` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Action_Review` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Assessment_Supp_Req` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Assessment_Supp_Req` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Assessment_Supp_Req_Rating` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Assessment_Supp_Req_Rating` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Criteria_For_Selection` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Criteria_For_Selection` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Criteria_For_Selection_Other` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Criteria_For_Selection_Other` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_DBST_Review_ILST_Request` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_DBST_Review_ILST_Request` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_DBST_Support_Strategy` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_DBST_Support_Strategy` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Factors_Classroom` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Factors_Classroom` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Factors_Community` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Factors_Community` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Factors_School` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Factors_School` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Health_Professional_Report` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Health_Professional_Report` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_ILST_Intervention_Records` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_ILST_Intervention_Records` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_ISP` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_ISP` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Learner_Background_Info` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Learner_Background_Info` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Learner_Impairment_Area` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Learner_Impairment_Area` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Learner_Supp_Needs` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Learner_Supp_Needs` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Learner_Support_Needs` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Learner_Support_Needs` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_Learning_And_Development_Barriers` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Learning_And_Development_Barriers` | `LearnerID` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `SNE_lu_Activity_Domain_Limit_Desc` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_Activity_Domain_Sub_Section` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_AreaID_of_Support` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_Assessment_Support_Area` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_Impairment_Area` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_ISP_Actions` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_Sub_Support_Area` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_lu_Support_Area` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SNE_Survey2008GradeByPregnant` | `Gradeid` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008LearnerAge` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008LearnerDeceasedParent` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008LearnerEnrollment` | `Gradeid` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008LearnerLanguage` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008LearnerTransfers` | `gradeid` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008PopulationGroup` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008SchoolFees` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `SNE_Survey2008SocialGrant` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `SSE_Functions` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SSE_Functions` | `TabID` | `SSE_Responsibility` | `TabID` | 8 |
| `Staff_CalendarTerms` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Staff_CalendarWeekSetup` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `StaffAbsentees` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `StaffAbsentees` | `Staffid` | `StaffMembers` | `StaffID` | 8 |
| `StaffAbsenteeStatistics` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `StaffLeave` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `StaffLeave` | `LinkId` | `Qualifications` | `LinkID` | 8 |
| `SubjectAverages` | `ReportID` | `LetterHeadSettings` | `ReportId` | 8 |
| `SubjectAverages` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `SubjectCriteria` | `OffCriterionId` | `SubjectCriteriaDeviations` | `OffCriterionId` | 8 |
| `SubjectCriteria` | `SectionId` | `CASubjectSections` | `SectionId` | 8 |
| `SubjectCriteria` | `Subjectid` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `SubjectCriteriaActivities` | `ActivityID` | `LearnerCassActivities` | `ActivityID` | 8 |
| `SubjectCriteriaActivities` | `OffCriterionId` | `SubjectCriteriaDeviations` | `OffCriterionId` | 8 |
| `SubjectMainTopics` | `OfficialSubjectID` | `SubjectsOfficialSettings` | `OfficialSubjectID` | 8 |
| `SubjectMainTopics` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `SubjectOutcomes` | `MainTopicID` | `SubjectMainTopics` | `MainTopicID` | 8 |
| `SubjectOutcomes` | `OfficialSubjectID` | `SubjectsOfficialSettings` | `OfficialSubjectID` | 8 |
| `SubjectOutcomes` | `OutcomeID` | `TaskOutcomes` | `OutcomeId` | 8 |
| `SubjectOutcomes` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `Subjects` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Subjects` | `OfficialSubjectID` | `SubjectsOfficialSettings` | `OfficialSubjectID` | 8 |
| `SubjectSets` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `SubjectsOfficial` | `SubjID` | `SubjectsOfficial_OLD` | `SubjID` | 8 |
| `SubjectsOfficial_OLD` | `SubjID` | `SubjectsOfficial` | `SubjID` | 8 |
| `SubjectSpecialisation` | `Educatorid` | `EducatorQualificationTypes` | `EducatorID` | 8 |
| `SubjectSpecialisation` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SubjectSpecialisation` | `Subjectid` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `SubjectsReportSplits` | `OfficialSubjectID` | `SubjectsOfficialSettings` | `OfficialSubjectID` | 8 |
| `SubjectsReportSplits` | `SubjID` | `SubjectsOfficial` | `SubjID` | 8 |
| `SubjectsSettings` | `OfficialSubjectID` | `SubjectsOfficialSettings` | `OfficialSubjectID` | 8 |
| `SubjectsSettings` | `SubjID` | `SubjectsOfficial` | `SubjID` | 8 |
| `SubjMultiGetFrom` | `ID` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SubstituteTT` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `SysSessions` | `SessionID` | `SysSessionsLocks` | `SessionID` | 8 |
| `SysSessions` | `UserID` | `GlobalSec` | `UserID` | 8 |
| `SysSessionsLocks` | `EducatorGroupID` | `12_2_1_Old_Educatorgroups` | `EducatorGroupID` | 8 |
| `SysSessionsLocks` | `SessionID` | `SysSessions` | `SessionID` | 8 |
| `SysSessionsLocks` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `TaskOutcomes` | `GradeID` | `GlobalSecMarks` | `GradeID` | 8 |
| `TaskOutcomes` | `OutcomeId` | `SubjectOutcomes` | `OutcomeID` | 8 |
| `TaskOutcomes` | `SubjectID` | `12_2_1_Old_SubjectSets` | `SubjectID` | 8 |
| `TeachingLanguages` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `TempPromotions` | `LearnerId` | `12_2_1_Old_LearnerPromotion` | `LearnerId` | 8 |
| `TieClasses` | `TieID` | `TieEducators` | `TieID` | 8 |
| `TieEducators` | `TieID` | `TieClasses` | `TieID` | 8 |
| `TieGroups` | `TieID` | `TieClasses` | `TieID` | 8 |
| `TieSubjects` | `TieId` | `TieClasses` | `TieID` | 8 |
| `TrainingAttended` | `id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `VenueTypes` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `Weeksetup` | `Id` | `12_2_1_Old_LearnerSubjects` | `ID` | 8 |
| `12_2_1_Old_LearnerSubjects` | `SubjectSetId` | `Subjects` | `Id` | 5 |
| `12_2_1_Old_SubjectSets` | `SubjectSetId` | `Subjects` | `Id` | 5 |
| `AssetMovementHistory` | `InventoryStockID` | `Inventory` | `InventoryId` | 5 |
| `GradeSubjectSets` | `SubjectSetId` | `Subjects` | `Id` | 5 |
| `InventoryLocation` | `InventoryStockID` | `Inventory` | `InventoryId` | 5 |
| `InventoryQuantities` | `InventoryStockID` | `Inventory` | `InventoryId` | 5 |
| `InventoryVenueTypes` | `InventoryStockID` | `Inventory` | `InventoryId` | 5 |
| `InventoryWriteOff` | `InventoryStockID` | `Inventory` | `InventoryId` | 5 |
| `LearnerSubjects` | `SubjectSetId` | `Subjects` | `Id` | 5 |
| `SubjectSets` | `SubjectSetId` | `Subjects` | `Id` | 5 |

## Table Dictionary (All Tables and Columns)

### `'mdb-import$'_ImportErrors`

- Estimated rows: `71`
- Heuristic primary key: `Error`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Error` | `WVARCHAR` | 255 | Yes |
| `Field` | `WVARCHAR` | 255 | Yes |
| `Row` | `INTEGER` | 10 | Yes |

### `12_2_1_Old_Educatorgroups`

- Estimated rows: `88`
- Heuristic primary key: `EducatorGroupID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorGroupID` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `EducatorId` | `INTEGER` | 10 | Yes |
| `GroupName` | `WVARCHAR` | 100 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |

### `12_2_1_Old_LearnerPromotion`

- Estimated rows: `0`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `PromotionDecision` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `LearnerAverage` | `DOUBLE` | 53 | Yes |
| `LearnerScore` | `DOUBLE` | 53 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ReportComment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `12_2_1_Old_LearnerSubjects`

- Estimated rows: `2581`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `LearnerId` | `INTEGER` | 10 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `SubjectSetId` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `EducatorGroupId` | `INTEGER` | 10 | Yes |
| `Subjectlevel` | `WVARCHAR` | 20 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `LanguageType` | `INTEGER` | 10 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ExcludeAve` | `BIT` | 1 | No |

### `12_2_1_Old_ReportMarks`

- Estimated rows: `10072`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `OBEKey` | `INTEGER` | 10 | Yes |
| `Symbol` | `WVARCHAR` | 10 | Yes |
| `Mark` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Level` | `WVARCHAR` | 10 | Yes |
| `Comment1` | `WLONGVARCHAR` | 1073741823 | Yes |
| `CASS` | `DOUBLE` | 53 | Yes |
| `Comment2` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Mark400` | `INTEGER` | 10 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ExamMark` | `DOUBLE` | 53 | Yes |
| `TotalMark` | `INTEGER` | 10 | Yes |
| `CASSTerm` | `INTEGER` | 10 | Yes |
| `ExcludeAve` | `BIT` | 1 | No |

### `12_2_1_Old_Subjects`

- Estimated rows: `244`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | Yes |
| `Name` | `WVARCHAR` | 200 | Yes |
| `Key` | `WVARCHAR` | 50 | Yes |
| `Code` | `WVARCHAR` | 50 | Yes |
| `Group` | `WVARCHAR` | 10 | Yes |
| `Selected` | `INTEGER` | 10 | Yes |
| `Phase` | `INTEGER` | 10 | Yes |
| `Afrname` | `WVARCHAR` | 200 | Yes |
| `PrintOrder` | `INTEGER` | 10 | Yes |
| `LuritsCode` | `WVARCHAR` | 50 | Yes |
| `CTAWeight` | `INTEGER` | 10 | Yes |
| `ExcludeSchedule` | `INTEGER` | 10 | Yes |

### `12_2_1_Old_SubjectSets`

- Estimated rows: `89`
- Heuristic primary key: `SubjectID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Description` | `WVARCHAR` | 200 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `SubjectSetId` | `INTEGER` | 10 | Yes |

### `12_2_1_Old_SubjectSpecialisation`

- Estimated rows: `63`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | Yes |
| `Educatorid` | `INTEGER` | 10 | Yes |
| `Subjectid` | `INTEGER` | 10 | Yes |
| `TrainingYears` | `INTEGER` | 10 | Yes |
| `TeachingYears` | `INTEGER` | 10 | Yes |

### `17_3_0_LearnerCass`

- Estimated rows: `27`
- Heuristic primary key: `Learnerid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Learnerid` | `INTEGER` | 10 | Yes |
| `Subjectid` | `INTEGER` | 10 | Yes |
| `CriterionId` | `INTEGER` | 10 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Mark` | `DOUBLE` | 53 | Yes |
| `Comments` | `WVARCHAR` | 250 | Yes |
| `DateAdded` | `TIMESTAMP` | 19 | Yes |
| `Criterionscore` | `INTEGER` | 10 | Yes |
| `OBEsymbol` | `INTEGER` | 10 | Yes |
| `EvalVer` | `INTEGER` | 10 | Yes |
| `Status` | `TINYINT` | 3 | Yes |
| `RecId` | `INTEGER` | 10 | No |

### `17_3_0_LearnerPromotion`

- Estimated rows: `0`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `PromotionDecision` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `LearnerAverage` | `DOUBLE` | 53 | Yes |
| `LearnerScore` | `DOUBLE` | 53 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ReportComment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |
| `FETPassLevel` | `WVARCHAR` | 50 | Yes |
| `DistrictRemark` | `WLONGVARCHAR` | 1073741823 | Yes |
| `CodeSelected` | `WVARCHAR` | 5 | Yes |
| `CodeAuto` | `WVARCHAR` | 5 | Yes |
| `CodeAutoDesc` | `WLONGVARCHAR` | 1073741823 | Yes |
| `CodeSched` | `WVARCHAR` | 5 | Yes |

### `17_3_0_ReportMarks`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `OBEKey` | `INTEGER` | 10 | Yes |
| `Symbol` | `WVARCHAR` | 10 | Yes |
| `Mark` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Level` | `WVARCHAR` | 10 | Yes |
| `Comment1` | `WLONGVARCHAR` | 1073741823 | Yes |
| `CASS` | `DOUBLE` | 53 | Yes |
| `Comment2` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ExamMark` | `DOUBLE` | 53 | Yes |
| `TotalMark` | `INTEGER` | 10 | Yes |
| `CASSTerm` | `INTEGER` | 10 | Yes |
| `Mark400` | `INTEGER` | 10 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ExcludeAve` | `BIT` | 1 | No |

### `17_3_0_ReportMarksSplits`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Term` | `TINYINT` | 3 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `SubjSplitNo` | `INTEGER` | 10 | Yes |
| `CriterionID` | `INTEGER` | 10 | Yes |
| `Mark` | `DOUBLE` | 53 | Yes |
| `OBEKey` | `INTEGER` | 10 | Yes |
| `EvalVer` | `INTEGER` | 10 | Yes |
| `RecId` | `INTEGER` | 10 | No |

### `18_1_0_Old_Educator_Appraisal`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | Yes |
| `PerformanceStandard` | `INTEGER` | 10 | Yes |
| `Criteria` | `INTEGER` | 10 | Yes |
| `SelfEvaluation` | `INTEGER` | 10 | Yes |
| `DSG_Score` | `INTEGER` | 10 | Yes |
| `FinalScore` | `INTEGER` | 10 | Yes |
| `Strengths` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Development_Recommendation` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Contextual_Factors_Notes` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Datayear` | `INTEGER` | 10 | Yes |
| `row_no` | `INTEGER` | 10 | Yes |

### `18_1_0_Old_Educator_DSG`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | Yes |
| `DSG_Member` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `18_1_0_Old_Educator_Final_Score`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | Yes |
| `PerformanceStandard` | `INTEGER` | 10 | Yes |
| `FinalScore` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |
| `Adjusted` | `BIT` | 1 | No |

### `18_1_0_Old_Educator_Final_Score_Comment`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `18_1_0_Old_Educator_Improvement_Plan`

- Estimated rows: `0`
- Heuristic primary key: `PerformanceStandard`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PerformanceStandard` | `INTEGER` | 10 | Yes |
| `Criteria` | `INTEGER` | 10 | Yes |
| `Development_Area` | `WVARCHAR` | 255 | Yes |
| `Improvement_Strategies` | `WVARCHAR` | 255 | Yes |
| `Educator_Names` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Phase` | `WVARCHAR` | 100 | Yes |
| `No_Educ` | `INTEGER` | 10 | Yes |
| `Addressing_Needs` | `WVARCHAR` | 100 | Yes |
| `Budget` | `WVARCHAR` | 100 | Yes |
| `Time` | `WVARCHAR` | 100 | Yes |
| `SDT_Remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Circuit_Manager_Remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `18_1_0_Old_Educator_Level`

- Estimated rows: `1`
- Heuristic primary key: `Educator_Code`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Educator_Code` | `WVARCHAR` | 50 | Yes |
| `Level` | `INTEGER` | 10 | Yes |
| `User_Name` | `WVARCHAR` | 255 | Yes |
| `Password` | `WVARCHAR` | 20 | Yes |

### `18_1_0_Old_Educator_PGP`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | Yes |
| `PS_Criteria` | `WVARCHAR` | 255 | Yes |
| `Development_Area` | `WLONGVARCHAR` | 1073741823 | Yes |
| `How` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Who` | `WLONGVARCHAR` | 1073741823 | Yes |
| `When` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `18_1_0_Old_lu_Perfomance_Criteria`

- Estimated rows: `42`
- Heuristic primary key: `PerformanceStandard`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PerformanceStandard` | `INTEGER` | 10 | Yes |
| `Criteria` | `INTEGER` | 10 | Yes |
| `PerformanceCriteria` | `WVARCHAR` | 255 | Yes |

### `18_1_0_Old_lu_PerformanceStandards`

- Estimated rows: `10`
- Heuristic primary key: `PerformanceStandardCD`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PerformanceStandardCD` | `INTEGER` | 10 | Yes |
| `PerformanceStandard` | `WVARCHAR` | 255 | Yes |

### `18_1_0_Old_PM_CheckList`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | Yes |
| `CheckListItem` | `INTEGER` | 10 | Yes |
| `AvailabilityStatus` | `INTEGER` | 10 | Yes |
| `Comments` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `18_1_0_SGBFunctions`

- Estimated rows: `1`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `Datayear` | `WVARCHAR` | 50 | Yes |
| `Field32` | `INTEGER` | 10 | Yes |
| `Field331` | `INTEGER` | 10 | Yes |
| `Field332` | `INTEGER` | 10 | Yes |
| `Field333` | `INTEGER` | 10 | Yes |
| `Field334` | `INTEGER` | 10 | Yes |
| `Field34` | `INTEGER` | 10 | Yes |
| `Field351` | `INTEGER` | 10 | Yes |
| `Field352` | `INTEGER` | 10 | Yes |
| `Field353` | `INTEGER` | 10 | Yes |
| `Field354` | `INTEGER` | 10 | Yes |
| `Field355` | `INTEGER` | 10 | Yes |
| `Field356` | `INTEGER` | 10 | Yes |
| `Field357` | `INTEGER` | 10 | Yes |
| `Field358` | `INTEGER` | 10 | Yes |
| `Field359` | `INTEGER` | 10 | Yes |
| `Field3510` | `INTEGER` | 10 | Yes |
| `Field3511` | `INTEGER` | 10 | Yes |
| `Field3512` | `INTEGER` | 10 | Yes |
| `Field361` | `INTEGER` | 10 | Yes |
| `Field362` | `INTEGER` | 10 | Yes |
| `Field363` | `INTEGER` | 10 | Yes |
| `Field364` | `INTEGER` | 10 | Yes |
| `Field365` | `INTEGER` | 10 | Yes |
| `Field366` | `INTEGER` | 10 | Yes |
| `Field367` | `INTEGER` | 10 | Yes |
| `Field368` | `INTEGER` | 10 | Yes |
| `Field369` | `INTEGER` | 10 | Yes |
| `Field3610` | `INTEGER` | 10 | Yes |
| `Field3611` | `INTEGER` | 10 | Yes |
| `Field37` | `INTEGER` | 10 | Yes |
| `Field381` | `INTEGER` | 10 | Yes |
| `Field382` | `INTEGER` | 10 | Yes |
| `Field383` | `INTEGER` | 10 | Yes |
| `Field384` | `INTEGER` | 10 | Yes |
| `Field39` | `INTEGER` | 10 | Yes |
| `Field3101` | `INTEGER` | 10 | Yes |
| `Field3102` | `INTEGER` | 10 | Yes |
| `Field3103` | `INTEGER` | 10 | Yes |
| `Field3104` | `INTEGER` | 10 | Yes |
| `Field3111` | `INTEGER` | 10 | Yes |
| `Field3112` | `INTEGER` | 10 | Yes |
| `Field3113` | `INTEGER` | 10 | Yes |
| `Field3114` | `INTEGER` | 10 | Yes |
| `Field3115` | `INTEGER` | 10 | Yes |
| `Field3116` | `INTEGER` | 10 | Yes |
| `Field3117` | `INTEGER` | 10 | Yes |

### `__Patches`

- Estimated rows: `89`
- Heuristic primary key: `Patch_Ver`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Patch_Ver` | `WVARCHAR` | 15 | Yes |
| `Patch_Jobs` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Patch_Buccessful` | `BIT` | 1 | No |
| `Patch_DateTimeStart` | `TIMESTAMP` | 19 | Yes |
| `Patch_DateTimeEnd` | `TIMESTAMP` | 19 | Yes |
| `Patch_ExeVer` | `WVARCHAR` | 25 | Yes |

### `Absentees`

- Estimated rows: `71838`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Learnerid` | `int` |  | Yes |
| `DateAbsent` | `datetime.datetime` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Class` | `int` |  | Yes |
| `WeekId` | `datetime.datetime` |  | Yes |
| `Gender` | `str` |  | Yes |
| `DataYear` | `str` |  | Yes |
| `ReasonID` | `int` |  | Yes |
| `ReasonOther` | `str` |  | Yes |

### `AbsenteesPeriods`

- Estimated rows: `0`
- Heuristic primary key: `AbsentID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AbsentID` | `INTEGER` | 10 | No |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Class` | `INTEGER` | 10 | Yes |
| `WeekId` | `TIMESTAMP` | 19 | Yes |
| `AbsentDate` | `TIMESTAMP` | 19 | Yes |
| `AbsentPeriodNo` | `TINYINT` | 3 | Yes |
| `AbsentReason` | `WVARCHAR` | 255 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |

### `AbsenteesReasons`

- Estimated rows: `24`
- Heuristic primary key: `ReasonID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ReasonID` | `INTEGER` | 10 | Yes |
| `Reason` | `WVARCHAR` | 255 | Yes |
| `ReasonAfr` | `WVARCHAR` | 255 | Yes |
| `Status` | `WVARCHAR` | 1 | Yes |

### `AbsenteeStatistics`

- Estimated rows: `15548`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `WeekId` | `datetime.datetime` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Class` | `int` |  | Yes |
| `Gender` | `str` |  | Yes |
| `TotalAbsent` | `int` |  | Yes |
| `TotalAttended` | `int` |  | Yes |
| `PossAttended` | `int` |  | Yes |
| `Days` | `int` |  | Yes |
| `AveAttended` | `int` |  | Yes |
| `Enrolment` | `int` |  | Yes |
| `Datayear` | `str` |  | Yes |

### `AccCategories`

- Estimated rows: `16`
- Heuristic primary key: `CatCode`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CatCode` | `WVARCHAR` | 20 | Yes |
| `Name` | `str` |  | Yes |
| `TypeCode` | `str` |  | Yes |
| `StartNumber` | `int` |  | Yes |
| `EndNumber` | `int` |  | Yes |

### `AccountInfo`

- Estimated rows: `1`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Institution` | `str` |  | Yes |
| `BranchNumber` | `str` |  | Yes |
| `BranchName` | `str` |  | Yes |
| `TypeAccount` | `str` |  | Yes |
| `AccountNumber` | `str` |  | Yes |
| `OpBal` | `decimal.Decimal` |  | Yes |
| `OverdraftType` | `str` |  | Yes |
| `OverAmount` | `float` |  | Yes |
| `COANumber` | `int` |  | Yes |
| `CurBal` | `decimal.Decimal` |  | Yes |
| `LastStateNumber` | `int` |  | Yes |
| `Active` | `bool` |  | Yes |
| `DateOpened` | `datetime.datetime` |  | Yes |
| `InterestRate` | `int` |  | Yes |

### `ActionCodeList`

- Estimated rows: `8`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Action` | `str` |  | Yes |

### `Ana2012EvaluationLevels`

- Estimated rows: `90`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `DateFrom` | `TIMESTAMP` | 19 | Yes |
| `DateTo` | `TIMESTAMP` | 19 | Yes |
| `EvalVer` | `INTEGER` | 10 | Yes |
| `GradeFrom` | `INTEGER` | 10 | Yes |
| `GradeTo` | `INTEGER` | 10 | Yes |
| `Code` | `TINYINT` | 3 | Yes |
| `Description` | `WVARCHAR` | 250 | Yes |
| `AfrDescription` | `WVARCHAR` | 250 | Yes |
| `MarkFrom` | `DOUBLE` | 53 | Yes |
| `MarkTo` | `DOUBLE` | 53 | Yes |

### `Ana2012FinalMarks`

- Estimated rows: `990`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `DataYear` | `WVARCHAR` | 4 | Yes |
| `Grade` | `TINYINT` | 3 | Yes |
| `ClassID` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `Lang_HL` | `WVARCHAR` | 50 | Yes |
| `Lang_FAL` | `WVARCHAR` | 50 | Yes |
| `Lang_Math` | `WVARCHAR` | 50 | Yes |
| `EvalVer` | `INTEGER` | 10 | Yes |
| `Mark_HL` | `INTEGER` | 10 | Yes |
| `Mark_FAL` | `INTEGER` | 10 | Yes |
| `Mark_Math` | `INTEGER` | 10 | Yes |
| `Status` | `TINYINT` | 3 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `TSSentFileName` | `WVARCHAR` | 200 | Yes |
| `DateLastUpdate` | `TIMESTAMP` | 19 | Yes |
| `TSLastUpdatedBy` | `WVARCHAR` | 200 | Yes |
| `RecErr` | `WVARCHAR` | 255 | Yes |

### `Ana2012TotalMarksPerGrade`

- Estimated rows: `32`
- Heuristic primary key: `DataYear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 4 | Yes |
| `Grade` | `TINYINT` | 3 | Yes |
| `Max_HL` | `INTEGER` | 10 | Yes |
| `Max_FAL` | `INTEGER` | 10 | Yes |
| `Max_Math` | `INTEGER` | 10 | Yes |
| `Avg_HL` | `INTEGER` | 10 | Yes |
| `Avg_FAL` | `INTEGER` | 10 | Yes |
| `Avg_Math` | `INTEGER` | 10 | Yes |

### `AnaGrade1To3Marks`

- Estimated rows: `97`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 50 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Class` | `INTEGER` | 10 | Yes |
| `LiteracyLangauge` | `WVARCHAR` | 100 | Yes |
| `NumeracyLangauge` | `WVARCHAR` | 100 | Yes |
| `LiteracyRawMark` | `INTEGER` | 10 | Yes |
| `LiteracyAverage` | `INTEGER` | 10 | Yes |
| `Numeracyrawmark` | `INTEGER` | 10 | Yes |
| `NumeracyAverage` | `INTEGER` | 10 | Yes |
| `Comments` | `WVARCHAR` | 50 | Yes |
| `SchoolQuintileStatus` | `INTEGER` | 10 | Yes |
| `Male` | `INTEGER` | 10 | Yes |
| `Female` | `INTEGER` | 10 | Yes |
| `GradeLAverage` | `INTEGER` | 10 | Yes |
| `GradeNAverage` | `INTEGER` | 10 | Yes |

### `AnaGrade4To9Marks`

- Estimated rows: `94`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 50 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Class` | `INTEGER` | 10 | Yes |
| `Languages` | `WVARCHAR` | 100 | Yes |
| `MathematicsLanguages` | `WVARCHAR` | 100 | Yes |
| `LanguageRawMark` | `INTEGER` | 10 | Yes |
| `LanguageAverage` | `INTEGER` | 10 | Yes |
| `Mathematicsrawmark` | `INTEGER` | 10 | Yes |
| `MathematicsAverage` | `INTEGER` | 10 | Yes |
| `Comments` | `WVARCHAR` | 50 | Yes |
| `SchoolQuintileStatus` | `INTEGER` | 10 | Yes |
| `Male` | `INTEGER` | 10 | Yes |
| `Female` | `INTEGER` | 10 | Yes |
| `GradeLAverage` | `INTEGER` | 10 | Yes |
| `GradeMAverage` | `INTEGER` | 10 | Yes |

### `AssetMovementHistory`

- Estimated rows: `0`
- Heuristic primary key: `OldVenueID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Movement_Date` | `TIMESTAMP` | 19 | Yes |
| `stock_code` | `WVARCHAR` | 200 | Yes |
| `Quantity` | `INTEGER` | 10 | Yes |
| `OldVenueID` | `INTEGER` | 10 | Yes |
| `NewVenueID` | `INTEGER` | 10 | Yes |
| `InventoryStockID` | `INTEGER` | 10 | Yes |

### `BankPay`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Date` | `datetime.datetime` |  | Yes |
| `Description` | `str` |  | Yes |
| `Amount` | `float` |  | Yes |
| `Bankrec` | `str` |  | Yes |
| `COANo` | `int` |  | Yes |
| `Month` | `int` |  | Yes |
| `Year` | `str` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNo` | `int` |  | Yes |
| `ReconMonth` | `int` |  | Yes |

### `BankReceipt`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Amount` | `decimal.Decimal` |  | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `AccNumber` | `int` |  | Yes |
| `BankRecon` | `str` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNo` | `int` |  | Yes |
| `ReconMonth` | `int` |  | Yes |

### `BankRecon`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Statement` | `INTEGER` | 10 | Yes |
| `ItemType` | `WVARCHAR` | 50 | Yes |
| `ItemNo` | `INTEGER` | 10 | Yes |
| `AccNo` | `INTEGER` | 10 | Yes |
| `BankItem` | `INTEGER` | 10 | Yes |

### `BankState`

- Estimated rows: `0`
- Heuristic primary key: `Statement`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Statement` | `INTEGER` | 10 | Yes |
| `AccNo` | `int` |  | Yes |
| `OpenBal` | `decimal.Decimal` |  | Yes |
| `CloseBal` | `decimal.Decimal` |  | Yes |
| `StateDate` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `Year` | `str` |  | Yes |
| `Completed` | `str` |  | Yes |

### `BankStateDetails`

- Estimated rows: `0`
- Heuristic primary key: `COANo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `COANo` | `INTEGER` | 10 | Yes |
| `BankStateNo` | `INTEGER` | 10 | Yes |
| `Entrydate` | `WVARCHAR` | 50 | Yes |
| `Item` | `WVARCHAR` | 70 | Yes |
| `ChequeNo` | `INTEGER` | 10 | Yes |
| `DbAmt` | `NUMERIC` | 19 | Yes |
| `CrAmt` | `NUMERIC` | 19 | Yes |
| `ItemNo` | `INTEGER` | 10 | No |
| `Recon` | `WVARCHAR` | 10 | Yes |
| `Year` | `WVARCHAR` | 50 | Yes |
| `Month` | `INTEGER` | 10 | Yes |

### `BarrierCodeList`

- Estimated rows: `12`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Barrier` | `str` |  | Yes |

### `BusRoutes`

- Estimated rows: `11`
- Heuristic primary key: `BusRouteId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `BusRouteId` | `INTEGER` | 10 | No |
| `Route` | `WVARCHAR` | 50 | Yes |
| `DepartureTime` | `WVARCHAR` | 20 | Yes |
| `RouteDescription` | `WVARCHAR` | 255 | Yes |
| `BusName` | `WVARCHAR` | 100 | Yes |
| `Responsible` | `WVARCHAR` | 150 | Yes |

### `Bustickets`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TicketNumber` | `INTEGER` | 10 | No |
| `Route` | `WVARCHAR` | 50 | Yes |
| `FName` | `WVARCHAR` | 50 | Yes |
| `SName` | `WVARCHAR` | 50 | Yes |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `DepartureTime` | `WVARCHAR` | 20 | Yes |
| `RouteDescription` | `WVARCHAR` | 255 | Yes |
| `BusName` | `WVARCHAR` | 100 | Yes |
| `Responsible` | `WVARCHAR` | 150 | Yes |
| `startdate` | `TIMESTAMP` | 19 | Yes |
| `enddate` | `TIMESTAMP` | 19 | Yes |
| `Price` | `INTEGER` | 10 | Yes |
| `Paid` | `WVARCHAR` | 5 | Yes |
| `SeatNumber` | `INTEGER` | 10 | Yes |

### `CancelLog`

- Estimated rows: `0`
- Heuristic primary key: `CancelId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CancelId` | `INTEGER` | 10 | No |
| `CancelDate` | `datetime.datetime` |  | Yes |
| `UserName` | `str` |  | Yes |
| `Item` | `str` |  | Yes |
| `ItemNo` | `int` |  | Yes |
| `Reason` | `str` |  | Yes |
| `CoaNum` | `int` |  | Yes |
| `Book` | `str` |  | Yes |

### `CASubjects`

- Estimated rows: `103`
- Heuristic primary key: `StructureId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `StructureId` | `INTEGER` | 10 | No |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `SubjectLevel` | `WVARCHAR` | 10 | Yes |
| `CassTotal` | `INTEGER` | 10 | Yes |
| `Grade` | `int` |  | Yes |

### `CASubjectSections`

- Estimated rows: `0`
- Heuristic primary key: `SectionId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SectionId` | `INTEGER` | 10 | No |
| `Description` | `WVARCHAR` | 200 | Yes |
| `SectionTotal` | `INTEGER` | 10 | Yes |
| `RawScoreTotal` | `int` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Active` | `bool` |  | Yes |
| `SectionHeading` | `str` |  | Yes |
| `SubjectId` | `int` |  | Yes |
| `SubjectLevel` | `str` |  | Yes |

### `ChartAccountsTable`

- Estimated rows: `5`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `TableName` | `WVARCHAR` | 100 | Yes |
| `Description` | `str` |  | Yes |
| `Selected` | `bool` |  | Yes |

### `ChartofAccountDetails`

- Estimated rows: `0`
- Heuristic primary key: `AccNum`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccNum` | `DOUBLE` | 53 | Yes |
| `BudgetCredit` | `float` |  | Yes |
| `BudgetDebit` | `float` |  | Yes |
| `OpenCredit` | `float` |  | Yes |
| `OpenDebit` | `float` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `str` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `SubAccNo` | `int` |  | Yes |

### `ChartofAccountsEC`

- Estimated rows: `201`
- Heuristic primary key: `AccountId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccountId` | `INTEGER` | 10 | No |
| `AccNumber` | `INTEGER` | 10 | Yes |
| `SubAccNo` | `INTEGER` | 10 | Yes |
| `AccCat` | `WVARCHAR` | 30 | Yes |
| `Description` | `WVARCHAR` | 200 | Yes |
| `OpenCredit` | `NUMERIC` | 19 | Yes |
| `OpenDebit` | `NUMERIC` | 19 | Yes |
| `BSGroup` | `INTEGER` | 10 | Yes |
| `Type` | `WVARCHAR` | 10 | Yes |

### `ChartofAccountsGE`

- Estimated rows: `85`
- Heuristic primary key: `AccountId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccountId` | `INTEGER` | 10 | No |
| `AccNumber` | `int` |  | Yes |
| `SubAccNo` | `int` |  | Yes |
| `AccCat` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `OpenCredit` | `decimal.Decimal` |  | Yes |
| `OpenDebit` | `decimal.Decimal` |  | Yes |
| `BSGroup` | `int` |  | Yes |
| `Type` | `str` |  | Yes |

### `ChartofAccountsKZN`

- Estimated rows: `198`
- Heuristic primary key: `AccountId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccountId` | `INTEGER` | 10 | No |
| `AccNumber` | `INTEGER` | 10 | Yes |
| `SubAccNo` | `INTEGER` | 10 | Yes |
| `AccCat` | `WVARCHAR` | 30 | Yes |
| `Description` | `WVARCHAR` | 200 | Yes |
| `OpenCredit` | `NUMERIC` | 19 | Yes |
| `OpenDebit` | `NUMERIC` | 19 | Yes |
| `BSGroup` | `INTEGER` | 10 | Yes |
| `Type` | `WVARCHAR` | 10 | Yes |

### `ChartOfAccountsNC`

- Estimated rows: `169`
- Heuristic primary key: `AccountId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccountId` | `INTEGER` | 10 | No |
| `AccNumber` | `int` |  | Yes |
| `SubAccNo` | `int` |  | Yes |
| `AccCat` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `OpenCredit` | `decimal.Decimal` |  | Yes |
| `OpenDebit` | `decimal.Decimal` |  | Yes |
| `BSGroup` | `int` |  | Yes |
| `Type` | `str` |  | Yes |

### `ChartofAccountsWC`

- Estimated rows: `75`
- Heuristic primary key: `AccountId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccountId` | `INTEGER` | 10 | No |
| `AccNumber` | `int` |  | Yes |
| `SubAccNo` | `int` |  | Yes |
| `AccCat` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `OpenCredit` | `decimal.Decimal` |  | Yes |
| `OpenDebit` | `decimal.Decimal` |  | Yes |
| `BSGroup` | `int` |  | Yes |
| `Type` | `str` |  | Yes |

### `Cheque_Pay`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `ChequeNum` | `int` |  | Yes |
| `BranchName` | `str` |  | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `PayWho` | `str` |  | Yes |
| `PayFor` | `str` |  | Yes |
| `Amount` | `decimal.Decimal` |  | Yes |
| `Department` | `str` |  | Yes |
| `AccNum` | `str` |  | Yes |
| `Bankrec` | `str` |  | Yes |
| `COANo` | `int` |  | Yes |
| `Month` | `int` |  | Yes |
| `Year` | `str` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNo` | `int` |  | Yes |
| `ReconMonth` | `int` |  | Yes |

### `ChequeNum`

- Estimated rows: `1`
- Heuristic primary key: `BookId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `BookId` | `INTEGER` | 10 | No |
| `AccNumber` | `str` |  | Yes |
| `ChequeStart` | `int` |  | Yes |
| `ChequeEnd` | `int` |  | Yes |
| `LastNum` | `int` |  | Yes |
| `COANo` | `int` |  | Yes |

### `Classes`

- Estimated rows: `16`
- Heuristic primary key: `ClassId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ClassId` | `INTEGER` | 10 | No |
| `Grade` | `int` |  | Yes |
| `ClassName` | `str` |  | Yes |
| `EdCode` | `str` |  | Yes |
| `Room` | `str` |  | Yes |
| `Type` | `int` |  | Yes |

### `ClassTT`

- Estimated rows: `0`
- Heuristic primary key: `Class`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Class` | `WVARCHAR` | 50 | Yes |
| `Day` | `INTEGER` | 10 | Yes |
| `Period` | `INTEGER` | 10 | Yes |
| `Edcode` | `WVARCHAR` | 150 | Yes |
| `SubjectKey` | `WVARCHAR` | 50 | Yes |
| `Locked` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Tie` | `INTEGER` | 10 | Yes |
| `TieCode` | `WVARCHAR` | 200 | Yes |

### `Comments`

- Estimated rows: `0`
- Heuristic primary key: `CommentId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CommentId` | `INTEGER` | 10 | No |
| `Comment` | `WVARCHAR` | 205 | Yes |

### `CostCentres`

- Estimated rows: `7`
- Heuristic primary key: `SubAccNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SubAccNumber` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 100 | Yes |

### `Countries`

- Estimated rows: `249`
- Heuristic primary key: `ISONo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ISONo` | `INTEGER` | 10 | Yes |
| `CountryName` | `WVARCHAR` | 255 | Yes |
| `Alpha2Code` | `WVARCHAR` | 2 | Yes |
| `Alpha3Code` | `WVARCHAR` | 3 | Yes |

### `CriteriaActivities`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `CriterionId` | `INTEGER` | 10 | Yes |
| `Activity` | `WVARCHAR` | 250 | Yes |
| `Type` | `str` |  | Yes |

### `CriteriaAssessments`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `CriterionId` | `INTEGER` | 10 | Yes |
| `Assessment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `CriterionOutcomes`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `CriterionId` | `INTEGER` | 10 | Yes |
| `CriterionOutcome` | `WVARCHAR` | 250 | Yes |

### `CurrentPeriod`

- Estimated rows: `13`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `StartYear` | `WVARCHAR` | 10 | Yes |
| `StartMonth` | `INTEGER` | 10 | Yes |
| `EndMonth` | `INTEGER` | 10 | Yes |
| `EndYear` | `WVARCHAR` | 10 | Yes |
| `ID` | `INTEGER` | 10 | No |
| `Closed` | `str` |  | Yes |
| `CloseDate` | `datetime.datetime` |  | Yes |
| `StatementText` | `str` |  | Yes |
| `AfrDescription` | `str` |  | Yes |
| `YearEndProcessed` | `str` |  | Yes |

### `CycleInfo`

- Estimated rows: `1`
- Heuristic primary key: `SID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Schoolname` | `WVARCHAR` | 150 | Yes |
| `FETDays` | `int` |  | Yes |
| `Rooms` | `int` |  | Yes |
| `FETPeriods` | `int` |  | Yes |
| `LowestGrade` | `int` |  | Yes |
| `HighestGrade` | `int` |  | Yes |
| `FETlength` | `int` |  | Yes |
| `LSEN` | `str` |  | Yes |
| `Remedial` | `str` |  | Yes |
| `FETTotal` | `int` |  | Yes |
| `GETDays` | `int` |  | Yes |
| `GETPeriods` | `int` |  | Yes |
| `GETLength` | `int` |  | Yes |
| `GETTotal` | `int` |  | Yes |
| `LSENSchool` | `bool` |  | Yes |
| `SNESpec` | `int` |  | Yes |
| `SNESpecOther` | `str` |  | Yes |
| `SchoolType` | `int` |  | Yes |
| `MultiGrade` | `str` |  | Yes |
| `SID` | `str` |  | Yes |
| `SIDLowestYear` | `int` |  | Yes |
| `SIDHighestYear` | `int` |  | Yes |

### `DAS`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Staffmemberid` | `int` |  | Yes |
| `DYear` | `str` |  | Yes |
| `DateAppraised` | `datetime.datetime` |  | Yes |
| `PersonConductingPraised` | `str` |  | Yes |
| `Comments` | `str` |  | Yes |
| `StaffCategory` | `str` |  | Yes |

### `DASCategories`

- Estimated rows: `24`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `CategoryName` | `str` |  | Yes |
| `Type` | `str` |  | Yes |

### `DASDevelopmentneedCategories`

- Estimated rows: `0`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Staffmemberid` | `INTEGER` | 10 | Yes |
| `Categoryname` | `str` |  | Yes |
| `Type` | `str` |  | Yes |
| `StaffCategory` | `str` |  | Yes |

### `DebtorsTrans`

- Estimated rows: `11563`
- Heuristic primary key: `TransID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TransID` | `INTEGER` | 10 | No |
| `DebAcc` | `int` |  | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `DebitAmount` | `decimal.Decimal` |  | Yes |
| `Desc` | `str` |  | Yes |
| `CreditAmt` | `decimal.Decimal` |  | Yes |
| `Month` | `int` |  | Yes |
| `Year` | `str` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNum` | `int` |  | Yes |

### `DeletedItems`

- Estimated rows: `31`
- Heuristic primary key: `ItemId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemId` | `INTEGER` | 10 | No |
| `ItemType` | `WVARCHAR` | 20 | Yes |
| `ItemNo` | `int` |  | Yes |
| `Book` | `str` |  | Yes |
| `ReversalDate` | `datetime.datetime` |  | Yes |
| `UserName` | `str` |  | Yes |
| `TransNo` | `int` |  | Yes |

### `DeleteLog`

- Estimated rows: `62`
- Heuristic primary key: `ReversalDate`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ReversalDate` | `TIMESTAMP` | 19 | Yes |
| `ItemDate` | `datetime.datetime` |  | Yes |
| `UserName` | `str` |  | Yes |
| `TransNo` | `int` |  | Yes |
| `ItemNo` | `int` |  | Yes |
| `Book` | `str` |  | Yes |
| `ItemType` | `str` |  | Yes |
| `CreditAmount` | `decimal.Decimal` |  | Yes |
| `DebitAmount` | `decimal.Decimal` |  | Yes |
| `AccNumber` | `int` |  | Yes |
| `SubAccNumber` | `int` |  | Yes |

### `DemeritMeritSettings`

- Estimated rows: `1`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Action` | `WVARCHAR` | 100 | Yes |
| `Type` | `WVARCHAR` | 1 | Yes |
| `Points` | `INTEGER` | 10 | Yes |

### `DepositBooks`

- Estimated rows: `1`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Book` | `WVARCHAR` | 200 | Yes |
| `StartNo` | `int` |  | Yes |
| `CurNo` | `int` |  | Yes |
| `EndNo` | `int` |  | Yes |
| `BankAcc` | `float` |  | Yes |

### `DepositInfo`

- Estimated rows: `7459`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Amount` | `decimal.Decimal` |  | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `AccNumber` | `int` |  | Yes |
| `DepSlipNo` | `int` |  | Yes |
| `Book` | `int` |  | Yes |
| `BankRecon` | `str` |  | Yes |
| `Cash` | `decimal.Decimal` |  | Yes |
| `Cheque` | `decimal.Decimal` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNo` | `int` |  | Yes |
| `ReconMonth` | `int` |  | Yes |

### `DetentionNotificationSettings`

- Estimated rows: `3`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `DetentionType` | `WVARCHAR` | 100 | Yes |
| `StartTime` | `WVARCHAR` | 20 | Yes |
| `EndTime` | `WVARCHAR` | 20 | Yes |
| `DetentionDay` | `WVARCHAR` | 20 | Yes |
| `MeritPoint` | `INTEGER` | 10 | Yes |

### `Deworming`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Grade` | `INTEGER` | 10 | Yes |
| `Datayear` | `WVARCHAR` | 4 | Yes |
| `Gender` | `WVARCHAR` | 6 | Yes |
| `TotalDewormed` | `INTEGER` | 10 | Yes |
| `TotalWithSideEffects` | `INTEGER` | 10 | Yes |
| `TotalEducatorsOrientated` | `INTEGER` | 10 | Yes |

### `DewormingQue`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Datayear` | `WVARCHAR` | 4 | Yes |
| `TotalConsRecieved` | `INTEGER` | 10 | Yes |
| `TotalDewTabletRecieved` | `INTEGER` | 10 | Yes |
| `TotalTabletDestroyed` | `INTEGER` | 10 | Yes |
| `TotalTabletReturned` | `INTEGER` | 10 | Yes |

### `Disabilities`

- Estimated rows: `60`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Name` | `str` |  | Yes |
| `NscCode` | `str` |  | Yes |
| `DomainCode` | `str` |  | Yes |

### `Disciplinarycodelist`

- Estimated rows: `9`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Level` | `WVARCHAR` | 30 | Yes |
| `Description` | `str` |  | Yes |
| `AfrDesc` | `str` |  | Yes |
| `Type` | `str` |  | Yes |

### `DisciplinaryConsequences`

- Estimated rows: `19`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Level` | `int` |  | Yes |
| `Code` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `EditStatus` | `str` |  | Yes |
| `AfrDesc` | `str` |  | Yes |

### `DisciplinaryLearnerMisconduct`

- Estimated rows: `128`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Level` | `int` |  | Yes |
| `Code` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `EditStatus` | `str` |  | Yes |
| `AfrDesc` | `str` |  | Yes |
| `Type` | `str` |  | Yes |
| `Point` | `int` |  | Yes |

### `DisciplinaryRecords`

- Estimated rows: `10136`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Learnerid` | `INTEGER` | 10 | Yes |
| `Date` | `TIMESTAMP` | 19 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `LevelMisconduct` | `str` |  | Yes |
| `MisconductCode` | `str` |  | Yes |
| `MisconductDescription` | `str` |  | Yes |
| `ActionLevel` | `str` |  | Yes |
| `ActionCode` | `str` |  | Yes |
| `ActionDescription` | `str` |  | Yes |
| `DisciplinedBy` | `str` |  | Yes |
| `AuthorisedBy` | `str` |  | Yes |
| `Agency` | `str` |  | Yes |
| `Suspension` | `int` |  | Yes |
| `Option` | `str` |  | Yes |
| `ExpulsionDate` | `str` |  | Yes |
| `Month` | `str` |  | Yes |
| `RecommendedExpulsion` | `str` |  | Yes |
| `Datayear` | `str` |  | Yes |
| `Demerit` | `int` |  | Yes |
| `Merit` | `int` |  | Yes |
| `Type` | `str` |  | Yes |

### `Districts`

- Estimated rows: `1804`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `District` | `WVARCHAR` | 50 | Yes |
| `Circuit` | `WVARCHAR` | 50 | Yes |
| `ProvID` | `INTEGER` | 10 | Yes |

### `Educator_CalendarTerms`

- Estimated rows: `60`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Quater` | `WVARCHAR` | 50 | Yes |
| `StartDate` | `TIMESTAMP` | 19 | Yes |
| `EndDate` | `TIMESTAMP` | 19 | Yes |
| `CurrentYear` | `WVARCHAR` | 50 | Yes |
| `Term` | `INTEGER` | 10 | Yes |

### `Educator_CalendarWeekSetup`

- Estimated rows: `112`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Weekid` | `TIMESTAMP` | 19 | Yes |
| `Holiday` | `TIMESTAMP` | 19 | Yes |
| `TermId` | `INTEGER` | 10 | Yes |
| `Reason` | `WVARCHAR` | 100 | Yes |

### `Educatorgroups`

- Estimated rows: `89`
- Heuristic primary key: `EducatorGroupID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorGroupID` | `INTEGER` | 10 | No |
| `Grade` | `INTEGER` | 10 | Yes |
| `EducatorId` | `INTEGER` | 10 | Yes |
| `GroupName` | `WVARCHAR` | 100 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `TimetableClass` | `WVARCHAR` | 50 | Yes |

### `EducatorQualificationTypes`

- Estimated rows: `82`
- Heuristic primary key: `EducatorID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorID` | `INTEGER` | 10 | No |
| `QualificationID` | `INTEGER` | 10 | Yes |

### `Educators`

- Estimated rows: `69`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EdID` | `INTEGER` | 10 | No |
| `FName` | `WVARCHAR` | 60 | Yes |
| `SName` | `str` |  | Yes |
| `Initials` | `str` |  | Yes |
| `Key` | `str` |  | Yes |
| `Address1` | `str` |  | Yes |
| `Address2` | `str` |  | Yes |
| `Address3` | `str` |  | Yes |
| `Code` | `str` |  | Yes |
| `Tel1Code` | `str` |  | Yes |
| `Tel1` | `str` |  | Yes |
| `BirthDate` | `str` |  | Yes |
| `IDNumber` | `str` |  | Yes |
| `DepCode` | `str` |  | Yes |
| `Subsidies` | `str` |  | Yes |
| `MedName` | `str` |  | Yes |
| `MedNo` | `str` |  | Yes |
| `Spouse` | `str` |  | Yes |
| `ENumber` | `str` |  | Yes |
| `Licenses` | `str` |  | Yes |
| `TaxNo` | `str` |  | Yes |
| `Academic` | `str` |  | Yes |
| `Institution` | `str` |  | Yes |
| `Skills` | `str` |  | Yes |
| `DateJoined` | `str` |  | Yes |
| `ManagementPosition` | `str` |  | Yes |
| `PostLevel` | `str` |  | Yes |
| `Tel2Code` | `str` |  | Yes |
| `Tel2` | `str` |  | Yes |
| `Professional` | `str` |  | Yes |
| `RegisterClass` | `str` |  | Yes |
| `PersalNumber` | `str` |  | Yes |
| `Homelanguage` | `str` |  | Yes |
| `2ndlanguage` | `str` |  | Yes |
| `Race` | `str` |  | Yes |
| `Title` | `str` |  | Yes |
| `Gender` | `str` |  | Yes |
| `EducatorType` | `str` |  | Yes |
| `MaritalStatus` | `str` |  | Yes |
| `DisabilityStatus` | `str` |  | Yes |
| `Actual` | `str` |  | Yes |
| `Acting` | `str` |  | Yes |
| `NatureofApointment` | `str` |  | Yes |
| `Remuneration` | `str` |  | Yes |
| `Qualification` | `str` |  | Yes |
| `QualificationType` | `str` |  | Yes |
| `PreGradeR` | `str` |  | Yes |
| `Secondary` | `str` |  | Yes |
| `GradeR` | `str` |  | Yes |
| `Primary` | `str` |  | Yes |
| `LSEN` | `str` |  | Yes |
| `AcademicDegree` | `str` |  | Yes |
| `ProfessionalDegree` | `str` |  | Yes |
| `TechnicalCerDip` | `str` |  | Yes |
| `ProfessionalDiploma` | `str` |  | Yes |
| `YearsExperience` | `int` |  | Yes |
| `Time` | `str` |  | Yes |
| `InstructionLanguage` | `str` |  | Yes |
| `Status` | `str` |  | Yes |
| `SACE` | `str` |  | Yes |
| `WCType` | `int` |  | Yes |
| `Intermediate` | `str` |  | Yes |
| `TSTransactionCategory` | `int` |  | Yes |
| `TSStatusFlag` | `int` |  | Yes |
| `TSReportStatusFlag` | `int` |  | Yes |
| `TSReasonCode` | `int` |  | Yes |
| `LuritsIndicator` | `int` |  | Yes |
| `TSSentFileName` | `str` |  | Yes |
| `TSDateLastUpdate` | `datetime.datetime` |  | Yes |
| `TSLastUpdatedBy` | `str` |  | Yes |
| `LuritsNumber` | `int` |  | Yes |
| `LuritsFlag` | `int` |  | Yes |
| `EmailAddress` | `str` |  | Yes |
| `ICTSkill` | `str` |  | Yes |
| `ICTUsage` | `str` |  | Yes |
| `Country` | `str` |  | Yes |
| `LuritsStatus` | `str` |  | Yes |
| `Photoname` | `str` |  | Yes |
| `KinSName` | `str` |  | Yes |
| `KinFName` | `str` |  | Yes |
| `SACitizen` | `int` |  | Yes |
| `WorkPermit` | `int` |  | Yes |
| `WorkPermitNo` | `str` |  | Yes |
| `WorkPermitDate` | `str` |  | Yes |
| `PrevSName` | `str` |  | Yes |
| `CompUsage` | `str` |  | Yes |
| `ReasonForNoSACE` | `int` |  | Yes |
| `UnionName` | `str` |  | Yes |
| `UnionNo` | `str` |  | Yes |
| `UnionName2` | `str` |  | Yes |
| `UnionNo2` | `str` |  | Yes |
| `UnionNameX` | `str` |  | Yes |
| `UnionNoX` | `str` |  | Yes |
| `Religion` | `str` |  | Yes |
| `ForeignID` | `str` |  | Yes |
| `Bursar` | `int` |  | Yes |

### `EducatorSubjectsTaught`

- Estimated rows: `1717`
- Heuristic primary key: `EducatorId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorId` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 50 | Yes |
| `EmisNumber` | `float` |  | Yes |
| `SubjectId` | `int` |  | Yes |
| `SubjectCode` | `str` |  | Yes |
| `Examinable` | `str` |  | Yes |
| `QtyLearners` | `int` |  | Yes |
| `Qtyperiods` | `int` |  | Yes |
| `Phase` | `str` |  | Yes |
| `Teachingyrs` | `int` |  | Yes |
| `Trainingyrs` | `int` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Hours` | `int` |  | Yes |
| `Minutes` | `int` |  | Yes |
| `ConfidenceLevel` | `int` |  | Yes |

### `EducatorTeachingHours`

- Estimated rows: `0`
- Heuristic primary key: `EducatorId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorId` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 50 | Yes |
| `EmisNumber` | `float` |  | Yes |
| `Phase` | `int` |  | Yes |
| `Hours` | `int` |  | Yes |

### `EducatorTeachingLevel`

- Estimated rows: `0`
- Heuristic primary key: `EducatorId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorId` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 50 | Yes |
| `EmisNumber` | `float` |  | Yes |
| `TeachingLevel` | `int` |  | Yes |

### `EducatorTT`

- Estimated rows: `0`
- Heuristic primary key: `EducatorCode`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorCode` | `WVARCHAR` | 50 | Yes |
| `Day` | `INTEGER` | 10 | Yes |
| `Period` | `INTEGER` | 10 | Yes |
| `Class` | `WVARCHAR` | 100 | Yes |
| `Subjectkey` | `WVARCHAR` | 50 | Yes |
| `Locked` | `INTEGER` | 10 | Yes |
| `Tie` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `TieCode` | `WVARCHAR` | 200 | Yes |

### `ELNA_Assessments`

- Estimated rows: `87`
- Heuristic primary key: `ItemNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemNo` | `INTEGER` | 10 | Yes |
| `SubjGroup` | `INTEGER` | 10 | Yes |
| `Numbering` | `DOUBLE` | 53 | Yes |
| `QuestionL1` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL2` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL3` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL4` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL5` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL6` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL7` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL8` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL9` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL10` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL11` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ItemPic` | `LONGVARBINARY` | 1073741823 | Yes |
| `keyquestion` | `INTEGER` | 10 | Yes |

### `ELNA_AssessmentScore`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `ItemNo` | `INTEGER` | 10 | Yes |
| `FinalScore` | `INTEGER` | 10 | Yes |
| `Numbering` | `DOUBLE` | 53 | Yes |
| `SubjectGroup` | `INTEGER` | 10 | Yes |
| `Mark` | `INTEGER` | 10 | Yes |
| `keyquestion` | `INTEGER` | 10 | Yes |

### `ELNA_Assessor`

- Estimated rows: `0`
- Heuristic primary key: `LNID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `LNID` | `INTEGER` | 10 | Yes |
| `Assessor` | `INTEGER` | 10 | Yes |

### `ELNA_AssessorInstructionV1`

- Estimated rows: `22`
- Heuristic primary key: `ItemNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemNo` | `INTEGER` | 10 | Yes |
| `SubjGroup` | `INTEGER` | 10 | Yes |
| `Numbering` | `DOUBLE` | 53 | Yes |
| `QuestionL1` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL2` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL3` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL4` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL5` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL6` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL7` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL8` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL9` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL10` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QuestionL11` | `WLONGVARCHAR` | 1073741823 | Yes |
| `keyquestion` | `INTEGER` | 10 | Yes |

### `ELNA_FinalScore`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `ItemNo` | `INTEGER` | 10 | Yes |
| `SubjectGroup` | `INTEGER` | 10 | Yes |
| `FinalScore` | `INTEGER` | 10 | Yes |

### `ELNA_Intructions`

- Estimated rows: `22`
- Heuristic primary key: `ItemNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemNo` | `INTEGER` | 10 | Yes |
| `SubjGroup` | `INTEGER` | 10 | Yes |
| `Instruction1` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction2` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction3` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction4` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction5` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction6` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction7` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction8` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction9` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction10` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Instruction11` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ScoringGuide` | `WLONGVARCHAR` | 1073741823 | Yes |

### `ELNA_Items`

- Estimated rows: `22`
- Heuristic primary key: `ItemNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemNo` | `INTEGER` | 10 | Yes |
| `SubjGroup` | `INTEGER` | 10 | Yes |
| `Description1` | `WVARCHAR` | 255 | Yes |
| `Description2` | `WVARCHAR` | 255 | Yes |
| `LevelsOfPerformance` | `WLONGVARCHAR` | 1073741823 | Yes |

### `ELNA_LearnerRegistration`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Name` | `WVARCHAR` | 255 | Yes |
| `IDNo` | `WVARCHAR` | 255 | Yes |
| `Gender` | `WVARCHAR` | 255 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Class` | `WVARCHAR` | 255 | Yes |
| `LOLT` | `WVARCHAR` | 255 | Yes |
| `DOB` | `WVARCHAR` | 255 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |
| `Status` | `WVARCHAR` | 255 | Yes |
| `CitizenShip` | `WVARCHAR` | 255 | Yes |
| `LSENStatus` | `WVARCHAR` | 255 | Yes |
| `GradeYears` | `WVARCHAR` | 255 | Yes |
| `RegistrationDate` | `WVARCHAR` | 255 | Yes |
| `PreviousPlacementofSchool` | `WVARCHAR` | 255 | Yes |

### `Events`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Date` | `TIMESTAMP` | 19 | Yes |
| `StartTime` | `WVARCHAR` | 50 | Yes |
| `EndTime` | `WVARCHAR` | 50 | Yes |
| `Description` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Compulsory` | `WVARCHAR` | 10 | Yes |
| `Category` | `WVARCHAR` | 50 | Yes |
| `ExEventID` | `INTEGER` | 10 | Yes |

### `ExtraMurals`

- Estimated rows: `66`
- Heuristic primary key: `ExID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ExID` | `INTEGER` | 10 | No |
| `ExTypeID` | `INTEGER` | 10 | Yes |
| `ExName` | `WVARCHAR` | 250 | Yes |
| `ExAfrName` | `WVARCHAR` | 250 | Yes |
| `ExPicKey` | `WVARCHAR` | 5 | Yes |
| `ExPicture` | `LONGVARBINARY` | 1073741823 | Yes |
| `ExOfficialID` | `INTEGER` | 10 | Yes |
| `RecSelected` | `BIT` | 1 | No |
| `RecLocked` | `BIT` | 1 | No |

### `ExtraMuralsAccolades`

- Estimated rows: `22`
- Heuristic primary key: `AccID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccID` | `INTEGER` | 10 | No |
| `AccName` | `WVARCHAR` | 250 | Yes |
| `AccAfrName` | `WVARCHAR` | 250 | Yes |
| `AccMerits` | `INTEGER` | 10 | Yes |
| `AccOfficialID` | `INTEGER` | 10 | Yes |
| `RecSelected` | `BIT` | 1 | No |
| `RecLocked` | `BIT` | 1 | No |

### `ExtraMuralsCompetitions`

- Estimated rows: `773`
- Heuristic primary key: `CompID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CompID` | `INTEGER` | 10 | No |
| `ExID` | `INTEGER` | 10 | Yes |
| `CompName` | `WVARCHAR` | 250 | Yes |
| `CompAfrName` | `WVARCHAR` | 250 | Yes |
| `CompPicture` | `LONGVARBINARY` | 1073741823 | Yes |
| `CompOfficialID` | `INTEGER` | 10 | Yes |
| `RecSelected` | `BIT` | 1 | No |
| `RecLocked` | `BIT` | 1 | No |

### `ExtraMuralsCompEvents`

- Estimated rows: `0`
- Heuristic primary key: `EventID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EventID` | `INTEGER` | 10 | No |
| `CompID` | `INTEGER` | 10 | Yes |
| `EventDate` | `TIMESTAMP` | 19 | Yes |
| `EventTimeStart` | `WVARCHAR` | 5 | Yes |
| `EventTimeEnd` | `WVARCHAR` | 5 | Yes |
| `EventDesc` | `WVARCHAR` | 250 | Yes |
| `EventAfrDesc` | `WVARCHAR` | 250 | Yes |

### `ExtraMuralsCompEventsLearners`

- Estimated rows: `0`
- Heuristic primary key: `EventID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EventID` | `INTEGER` | 10 | Yes |
| `TeamID` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `ExtraMuralsCompEventsTeams`

- Estimated rows: `0`
- Heuristic primary key: `EventID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EventID` | `INTEGER` | 10 | Yes |
| `TeamID` | `INTEGER` | 10 | Yes |

### `ExtraMuralsHouses`

- Estimated rows: `4`
- Heuristic primary key: `HseID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `HseID` | `INTEGER` | 10 | No |
| `HseName` | `WVARCHAR` | 250 | Yes |
| `HseAfrName` | `WVARCHAR` | 250 | Yes |
| `HseColour` | `WVARCHAR` | 20 | Yes |
| `HseAfrColour` | `WVARCHAR` | 20 | Yes |
| `HsePicture` | `LONGVARBINARY` | 1073741823 | Yes |
| `RecSelected` | `BIT` | 1 | No |

### `ExtraMuralsHousesLinks`

- Estimated rows: `2`
- Heuristic primary key: `HseID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `HseID` | `INTEGER` | 10 | Yes |
| `LinkIDType` | `TINYINT` | 3 | Yes |
| `LinkID` | `INTEGER` | 10 | Yes |
| `LinkPosition` | `TINYINT` | 3 | Yes |

### `ExtraMuralsLearners`

- Estimated rows: `0`
- Heuristic primary key: `RecID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `RecID` | `INTEGER` | 10 | No |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `TermNo` | `TINYINT` | 3 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `ExID` | `INTEGER` | 10 | Yes |
| `TeamID` | `INTEGER` | 10 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |

### `ExtraMuralsTeams`

- Estimated rows: `288`
- Heuristic primary key: `TeamID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TeamID` | `INTEGER` | 10 | No |
| `ExID` | `INTEGER` | 10 | Yes |
| `TeamName` | `WVARCHAR` | 250 | Yes |
| `TeamAfrName` | `WVARCHAR` | 250 | Yes |
| `TeamAgeFrom` | `TINYINT` | 3 | Yes |
| `TeamAgeTo` | `TINYINT` | 3 | Yes |
| `TeamEdID` | `INTEGER` | 10 | Yes |
| `TeamDepEdID` | `INTEGER` | 10 | Yes |
| `TeamPicture` | `LONGVARBINARY` | 1073741823 | Yes |
| `TeamOfficialID` | `INTEGER` | 10 | Yes |
| `RecSelected` | `BIT` | 1 | No |
| `RecLocked` | `BIT` | 1 | No |

### `ExtraMuralsTypes`

- Estimated rows: `2`
- Heuristic primary key: `ExTypeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ExTypeID` | `INTEGER` | 10 | No |
| `ExTypeName` | `WVARCHAR` | 250 | Yes |
| `ExTypeAfrName` | `WVARCHAR` | 250 | Yes |
| `ExTypeShortName` | `WVARCHAR` | 20 | Yes |
| `ExTypeShortAfrName` | `WVARCHAR` | 20 | Yes |
| `ExTypePicKey` | `WVARCHAR` | 5 | Yes |
| `ExTypePicture` | `LONGVARBINARY` | 1073741823 | Yes |
| `ExTypeOfficialID` | `INTEGER` | 10 | Yes |
| `RecSelected` | `BIT` | 1 | No |
| `RecLocked` | `BIT` | 1 | No |

### `FeederSchools`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Name` | `str` |  | Yes |
| `Tel` | `str` |  | Yes |
| `Principal` | `str` |  | Yes |
| `Address` | `str` |  | Yes |

### `FeeExemptions`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `AccessionNo` | `WVARCHAR` | 50 | Yes |
| `Sname` | `WVARCHAR` | 100 | Yes |
| `FName` | `WVARCHAR` | 200 | Yes |
| `Class` | `WVARCHAR` | 50 | Yes |
| `AppType` | `str` |  | Yes |
| `SuccessfulApp` | `str` |  | Yes |
| `Condition` | `str` |  | Yes |
| `RefusalReason` | `str` |  | Yes |
| `ExemptionAmount` | `decimal.Decimal` |  | Yes |
| `Year` | `str` |  | Yes |
| `DateApplied` | `datetime.datetime` |  | Yes |

### `Fees`

- Estimated rows: `156`
- Heuristic primary key: `Fees`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Grade` | `INTEGER` | 10 | Yes |
| `Fees` | `INTEGER` | 10 | Yes |
| `Year` | `WVARCHAR` | 10 | Yes |

### `FormLetters`

- Estimated rows: `1`
- Heuristic primary key: `LetterId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LetterId` | `INTEGER` | 10 | No |
| `LetterName` | `WVARCHAR` | 100 | Yes |
| `Lettertext` | `WLONGVARCHAR` | 1073741823 | Yes |

### `FormLock`

- Estimated rows: `0`
- Heuristic primary key: `FormName`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `FormName` | `WVARCHAR` | 50 | Yes |
| `UniqueCode` | `str` |  | Yes |
| `DateActive` | `datetime.datetime` |  | Yes |
| `UserName` | `str` |  | Yes |

### `FormTemplates`

- Estimated rows: `20`
- Heuristic primary key: `TemplateID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TemplateID` | `INTEGER` | 10 | No |
| `FormName` | `WVARCHAR` | 100 | Yes |
| `UserID` | `INTEGER` | 10 | Yes |
| `TemplateName` | `WVARCHAR` | 50 | Yes |
| `TemplateData` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ShareTemplate` | `BIT` | 1 | No |

### `General_Info`

- Estimated rows: `1`
- Heuristic primary key: `SchoolID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SchoolID` | `INTEGER` | 10 | No |
| `SchoolName` | `str` |  | Yes |
| `ProvincialDep` | `str` |  | Yes |
| `District` | `str` |  | Yes |
| `Region` | `str` |  | Yes |
| `Circuit` | `str` |  | Yes |
| `Address1` | `str` |  | Yes |
| `Address2` | `str` |  | Yes |
| `Address3` | `str` |  | Yes |
| `AddressCode` | `str` |  | Yes |
| `PostAddress1` | `str` |  | Yes |
| `PostAddress2` | `str` |  | Yes |
| `PostAddress3` | `str` |  | Yes |
| `PostCode` | `str` |  | Yes |
| `TelCode1` | `str` |  | Yes |
| `Telephone1` | `str` |  | Yes |
| `TelCode2` | `str` |  | Yes |
| `Telephone2` | `str` |  | Yes |
| `Telcode3` | `str` |  | Yes |
| `Telephone3` | `str` |  | Yes |
| `FaxCode` | `str` |  | Yes |
| `Fax` | `str` |  | Yes |
| `TSchool` | `str` |  | Yes |
| `TAdd1` | `str` |  | Yes |
| `TAdd2` | `str` |  | Yes |
| `TAdd3` | `str` |  | Yes |
| `TCode` | `str` |  | Yes |
| `ttelcode1` | `str` |  | Yes |
| `TTel1` | `str` |  | Yes |
| `Tfaxcode` | `str` |  | Yes |
| `TFax` | `str` |  | Yes |
| `TPrincipal` | `str` |  | Yes |
| `ContactPerson` | `str` |  | Yes |
| `EmisCode` | `str` |  | Yes |
| `EMail` | `str` |  | Yes |
| `PredominantLanguage` | `int` |  | Yes |
| `PersalPayPoint` | `str` |  | Yes |
| `PersalComponent` | `str` |  | Yes |
| `InternetAccess` | `str` |  | Yes |
| `Ownership` | `str` |  | Yes |
| `LandOwnership` | `str` |  | Yes |
| `Platoon` | `str` |  | Yes |
| `HostSchool` | `str` |  | Yes |
| `DoubleShifts` | `str` |  | Yes |
| `ExamAuthority` | `str` |  | Yes |
| `ExamCentre` | `str` |  | Yes |
| `ExamCentreNumber` | `str` |  | Yes |
| `Specialised` | `str` |  | Yes |
| `Specialisation` | `str` |  | Yes |
| `FeePeriod` | `str` |  | Yes |
| `FeeMonths` | `int` |  | Yes |
| `Multigrade` | `int` |  | Yes |
| `Remedial` | `int` |  | Yes |
| `SGBStatus` | `str` |  | Yes |
| `MaintainProperty` | `bool` |  | Yes |
| `ExtraMural` | `bool` |  | Yes |
| `Textbooks` | `bool` |  | Yes |
| `Services` | `bool` |  | Yes |
| `Abet` | `bool` |  | Yes |
| `OtherFunctions` | `bool` |  | Yes |
| `CensusArea` | `str` |  | Yes |
| `ErfNumber` | `str` |  | Yes |
| `EmisHostSchool` | `str` |  | Yes |
| `HostTime` | `int` |  | Yes |
| `ExamAuthName` | `str` |  | Yes |
| `CorrespondenceLang` | `int` |  | Yes |
| `NearestTown` | `str` |  | Yes |
| `DistanceTown` | `float` |  | Yes |
| `DistrictCode` | `int` |  | Yes |
| `SchoolLevel` | `int` |  | Yes |
| `TSSchoolStatus` | `int` |  | Yes |
| `TSTransactionCategory` | `int` |  | Yes |
| `TSStatusFlag` | `int` |  | Yes |
| `TSReportStatusFlag` | `int` |  | Yes |
| `TSReasonCode` | `int` |  | Yes |
| `TSSentFileName` | `str` |  | Yes |
| `TSDateLastUpdate` | `datetime.datetime` |  | Yes |
| `TSLastUpdatedBy` | `str` |  | Yes |
| `OwnerBuildings` | `str` |  | Yes |
| `LuritsIndicator` | `int` |  | Yes |
| `LuritsYear` | `int` |  | Yes |
| `PostalAddressType` | `str` |  | Yes |
| `Multigrades` | `int` |  | Yes |
| `EmisOfficer` | `int` |  | Yes |
| `EmisOffEducator` | `bool` |  | Yes |
| `EmailAlt` | `str` |  | Yes |
| `Telcode4` | `str` |  | Yes |
| `Telephone4` | `str` |  | Yes |
| `AdminComputers` | `int` |  | Yes |
| `PostAddress0` | `str` |  | Yes |
| `PostAddress0No` | `str` |  | Yes |
| `TEmisCode` | `str` |  | Yes |
| `UseMarksSecurity` | `bool` |  | Yes |
| `PSNP` | `int` |  | Yes |
| `TSIncludesANA` | `int` |  | Yes |
| `LastDBCompact` | `datetime.datetime` |  | Yes |
| `IQMS_LastExpDate` | `datetime.datetime` |  | Yes |
| `IQMS_LastImpDate` | `datetime.datetime` |  | Yes |
| `ExamBoard` | `int` |  | Yes |
| `ExamBoardOther` | `str` |  | Yes |
| `LocalMunicipality` | `str` |  | Yes |
| `UMALUSIRegistered` | `str` |  | Yes |
| `UmalusiRegDate` | `str` |  | Yes |
| `Umalusinr` | `str` |  | Yes |

### `GlobalSec`

- Estimated rows: `89`
- Heuristic primary key: `UserID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `UserID` | `INTEGER` | 10 | No |
| `UserCode` | `INTEGER` | 10 | Yes |
| `UserName` | `WVARCHAR` | 50 | Yes |
| `UserPassword` | `WVARCHAR` | 30 | Yes |
| `LinkType` | `TINYINT` | 3 | Yes |
| `LinkID` | `INTEGER` | 10 | Yes |
| `SName` | `WVARCHAR` | 100 | Yes |
| `FName` | `WVARCHAR` | 70 | Yes |
| `ProfID` | `INTEGER` | 10 | Yes |
| `PrefShowMenuNo` | `TINYINT` | 3 | Yes |
| `PrefSubjectListLanguage` | `TINYINT` | 3 | Yes |
| `PrefShowVernacular` | `TINYINT` | 3 | Yes |
| `ChgPsw` | `BIT` | 1 | No |
| `Status` | `WVARCHAR` | 20 | Yes |
| `PrefGridEditEnterAction` | `TINYINT` | 3 | Yes |
| `LuritsPrincipalApproval` | `BIT` | 1 | No |
| `Library` | `BIT` | 1 | No |
| `ExpiryDate` | `TIMESTAMP` | 19 | Yes |
| `Prov` | `INTEGER` | 10 | Yes |

### `GlobalSecLoginAttempts`

- Estimated rows: `16`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Username` | `WLONGVARCHAR` | 1073741823 | Yes |
| `FailedAttempts` | `INTEGER` | 10 | Yes |
| `FirstFailedAttemptTime` | `TIMESTAMP` | 19 | Yes |
| `IsLockedOut` | `BIT` | 1 | No |

### `GlobalSecMarks`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `FType` | `WVARCHAR` | 2 | Yes |
| `GradeID` | `INTEGER` | 10 | Yes |
| `ClassID` | `INTEGER` | 10 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `UserID` | `INTEGER` | 10 | Yes |

### `GlobalSecMenus`

- Estimated rows: `63`
- Heuristic primary key: `MnuNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MnuNo` | `WVARCHAR` | 25 | Yes |
| `MnuTitle` | `WVARCHAR` | 100 | Yes |
| `MnuOpt0` | `WVARCHAR` | 100 | Yes |
| `MnuOpt1` | `WVARCHAR` | 100 | Yes |
| `MnuOpt2` | `WVARCHAR` | 100 | Yes |
| `MnuOpt3` | `WVARCHAR` | 100 | Yes |
| `MnuOpt4` | `WVARCHAR` | 100 | Yes |
| `MnuOpt5` | `WVARCHAR` | 100 | Yes |
| `MnuOpt6` | `WVARCHAR` | 100 | Yes |
| `MnuOpt7` | `WVARCHAR` | 100 | Yes |
| `MnuOpt8` | `WVARCHAR` | 100 | Yes |
| `MnuOpt9` | `WVARCHAR` | 100 | Yes |
| `MnuOpt10` | `WVARCHAR` | 100 | Yes |
| `MnuOpt11` | `WVARCHAR` | 100 | Yes |
| `MnuOpt12` | `WVARCHAR` | 100 | Yes |
| `MnuOpt13` | `WVARCHAR` | 100 | Yes |
| `MnuOpt14` | `WVARCHAR` | 100 | Yes |
| `MnuOpt15` | `WVARCHAR` | 100 | Yes |
| `MnuOpt16` | `WVARCHAR` | 100 | Yes |
| `MnuOpt17` | `WVARCHAR` | 100 | Yes |
| `MnuOpt18` | `WVARCHAR` | 100 | Yes |
| `MnuOpt19` | `WVARCHAR` | 100 | Yes |

### `GlobalSecProfiles`

- Estimated rows: `12`
- Heuristic primary key: `ProfID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ProfID` | `INTEGER` | 10 | No |
| `ProfLevel` | `TINYINT` | 3 | Yes |
| `ProfName` | `WVARCHAR` | 30 | Yes |

### `GlobalSecRights`

- Estimated rows: `913`
- Heuristic primary key: `ProfID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ProfID` | `INTEGER` | 10 | Yes |
| `MnuNo` | `WVARCHAR` | 25 | Yes |
| `MnuOptOn1` | `BIT` | 1 | No |
| `MnuOptOn2` | `BIT` | 1 | No |
| `MnuOptOn3` | `BIT` | 1 | No |
| `MnuOptOn4` | `BIT` | 1 | No |
| `MnuOptOn5` | `BIT` | 1 | No |
| `MnuOptOn6` | `BIT` | 1 | No |
| `MnuOptOn7` | `BIT` | 1 | No |
| `MnuOptOn8` | `BIT` | 1 | No |
| `MnuOptOn9` | `BIT` | 1 | No |
| `MnuOptOn10` | `BIT` | 1 | No |
| `MnuOptOn11` | `BIT` | 1 | No |
| `MnuOptOn12` | `BIT` | 1 | No |
| `MnuOptOn13` | `BIT` | 1 | No |
| `MnuOptOn14` | `BIT` | 1 | No |
| `MnuOptOn15` | `BIT` | 1 | No |
| `MnuOptOn16` | `BIT` | 1 | No |
| `MnuOptOn17` | `BIT` | 1 | No |
| `MnuOptOn18` | `BIT` | 1 | No |
| `MnuOptOn19` | `BIT` | 1 | No |

### `GlobalSysLogs`

- Estimated rows: `41`
- Heuristic primary key: `RecNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `RecNo` | `INTEGER` | 10 | Yes |
| `RecDesc` | `WVARCHAR` | 50 | Yes |
| `RecEnabled` | `BIT` | 1 | No |
| `RecValue` | `WVARCHAR` | 200 | Yes |

### `GLTrans`

- Estimated rows: `36918`
- Heuristic primary key: `AccNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccNumber` | `DOUBLE` | 53 | Yes |
| `SubAccNumber` | `INTEGER` | 10 | Yes |
| `TransNumber` | `float` |  | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `DebitAmount` | `decimal.Decimal` |  | Yes |
| `CreditAmount` | `decimal.Decimal` |  | Yes |
| `Source` | `str` |  | Yes |
| `Operation` | `str` |  | Yes |
| `ProcDate` | `datetime.datetime` |  | Yes |
| `Paymeth` | `str` |  | Yes |
| `DocNo` | `str` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `Processed` | `bool` |  | Yes |
| `TransType` | `int` |  | Yes |
| `User` | `str` |  | Yes |
| `Capturer` | `str` |  | Yes |

### `GovMembers`

- Estimated rows: `51`
- Heuristic primary key: `MemberID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MemberID` | `INTEGER` | 10 | No |
| `TypeOfMember` | `WVARCHAR` | 50 | Yes |
| `LinkID` | `INTEGER` | 10 | Yes |
| `Sname` | `WVARCHAR` | 100 | Yes |
| `Fname` | `WVARCHAR` | 100 | Yes |
| `Initials` | `WVARCHAR` | 10 | Yes |
| `Title` | `WVARCHAR` | 10 | Yes |
| `Race` | `WVARCHAR` | 20 | Yes |
| `Gender` | `WVARCHAR` | 20 | Yes |
| `LangHome` | `WVARCHAR` | 100 | Yes |
| `Lang2nd` | `WVARCHAR` | 100 | Yes |
| `TelCode` | `WVARCHAR` | 50 | Yes |
| `TelNumber` | `WVARCHAR` | 50 | Yes |
| `CellPhone` | `WVARCHAR` | 50 | Yes |
| `FaxCode` | `WVARCHAR` | 50 | Yes |
| `FaxNumber` | `WVARCHAR` | 50 | Yes |
| `Email` | `WVARCHAR` | 200 | Yes |
| `pAddress1` | `WVARCHAR` | 50 | Yes |
| `pAddress2` | `WVARCHAR` | 50 | Yes |
| `pAddress3` | `WVARCHAR` | 50 | Yes |
| `pAddressCode` | `WVARCHAR` | 5 | Yes |
| `PoliceStationName` | `WVARCHAR` | 50 | Yes |
| `PoliceStationNo` | `WVARCHAR` | 50 | Yes |
| `PoliceStationTelCode` | `WVARCHAR` | 5 | Yes |
| `PoliceStationTelNumber` | `WVARCHAR` | 10 | Yes |
| `PoliceStationAddress1` | `WVARCHAR` | 50 | Yes |
| `PoliceStationAddress2` | `WVARCHAR` | 50 | Yes |
| `PoliceStationAddress3` | `WVARCHAR` | 50 | Yes |
| `PoliceStationAddressCode` | `WVARCHAR` | 5 | Yes |
| `PoliceCommanderInitials` | `WVARCHAR` | 10 | Yes |
| `PoliceCommanderSname` | `WVARCHAR` | 100 | Yes |
| `PoliceCommanderRank` | `WVARCHAR` | 50 | Yes |
| `PoliceCommanderTelCode` | `WVARCHAR` | 50 | Yes |
| `PoliceCommanderTelNumber` | `WVARCHAR` | 50 | Yes |
| `PoliceMemberRank` | `WVARCHAR` | 50 | Yes |
| `DisabilityStatus` | `WVARCHAR` | 50 | Yes |
| `BirthDate` | `WVARCHAR` | 15 | Yes |
| `SACitizen` | `TINYINT` | 3 | Yes |
| `Country` | `WVARCHAR` | 20 | Yes |
| `IDNumber` | `WVARCHAR` | 20 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `LuritsIndicator` | `INTEGER` | 10 | Yes |
| `LuritsFlag` | `INTEGER` | 10 | Yes |
| `TSSentFileName` | `WVARCHAR` | 200 | Yes |
| `TSDateLastUpdate` | `TIMESTAMP` | 19 | Yes |
| `TSLastUpdatedBy` | `WVARCHAR` | 200 | Yes |
| `LuritsStatus` | `WVARCHAR` | 200 | Yes |

### `GovMemberShips`

- Estimated rows: `53`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `GovType` | `WVARCHAR` | 5 | Yes |
| `MemberID` | `INTEGER` | 10 | Yes |
| `Status` | `WVARCHAR` | 1 | Yes |
| `Capacity` | `WVARCHAR` | 240 | Yes |
| `DateElected` | `TIMESTAMP` | 19 | Yes |
| `DateResigned` | `TIMESTAMP` | 19 | Yes |
| `TermEnds` | `TIMESTAMP` | 19 | Yes |
| `EdLevel` | `INTEGER` | 10 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `LuritsIndicator` | `INTEGER` | 10 | Yes |
| `LuritsFlag` | `INTEGER` | 10 | Yes |
| `TSSentFileName` | `WVARCHAR` | 200 | Yes |
| `TSDateLastUpdate` | `TIMESTAMP` | 19 | Yes |
| `TSLastUpdatedBy` | `WVARCHAR` | 200 | Yes |
| `LuritsStatus` | `WVARCHAR` | 200 | Yes |

### `GovPolicies`

- Estimated rows: `29`
- Heuristic primary key: `PolicyId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PolicyId` | `INTEGER` | 10 | No |
| `PolicyName` | `WVARCHAR` | 200 | Yes |
| `EditStatus` | `WVARCHAR` | 1 | Yes |

### `GovPoliciesRecords`

- Estimated rows: `15`
- Heuristic primary key: `PolicyId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PolicyId` | `INTEGER` | 10 | Yes |
| `GovType` | `WVARCHAR` | 5 | Yes |
| `DateOriginated` | `WVARCHAR` | 10 | Yes |
| `DatePresented` | `WVARCHAR` | 10 | Yes |
| `Approved` | `WVARCHAR` | 10 | Yes |
| `DateAmended` | `WVARCHAR` | 10 | Yes |
| `DateSubmitted` | `WVARCHAR` | 10 | Yes |
| `DateApproved` | `WVARCHAR` | 10 | Yes |

### `GovTrainingCategories`

- Estimated rows: `8`
- Heuristic primary key: `TrainCatID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TrainCatID` | `INTEGER` | 10 | No |
| `TrainCatName` | `WVARCHAR` | 100 | Yes |

### `GovTrainingCourses`

- Estimated rows: `0`
- Heuristic primary key: `CourseID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CourseID` | `INTEGER` | 10 | No |
| `TrainCatID` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 4 | Yes |
| `CourseName` | `WVARCHAR` | 100 | Yes |
| `ServiceProvider` | `WVARCHAR` | 150 | Yes |
| `DateStart` | `TIMESTAMP` | 19 | Yes |
| `DateEnd` | `TIMESTAMP` | 19 | Yes |
| `Duration` | `INTEGER` | 10 | Yes |
| `FundedBy` | `WVARCHAR` | 50 | Yes |

### `GovTrainingReceived`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `DataYear` | `WVARCHAR` | 4 | Yes |
| `GovType` | `WVARCHAR` | 5 | Yes |
| `CourseID` | `INTEGER` | 10 | Yes |
| `MemberID` | `INTEGER` | 10 | Yes |

### `GovTrainingRequired`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `DataYear` | `WVARCHAR` | 4 | Yes |
| `GovType` | `WVARCHAR` | 5 | Yes |
| `TrainCatID` | `INTEGER` | 10 | Yes |
| `MemberID` | `INTEGER` | 10 | Yes |

### `GradeSubjectSets`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Grade` | `INTEGER` | 10 | Yes |
| `SubjectSetId` | `INTEGER` | 10 | Yes |

### `GroupSubjects`

- Estimated rows: `0`
- Heuristic primary key: `SubjectID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Description` | `WVARCHAR` | 200 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `GroupId` | `INTEGER` | 10 | Yes |

### `HealthConsent`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerID` | `INTEGER` | 10 | Yes |
| `Yes1` | `INTEGER` | 10 | Yes |
| `Yes2` | `INTEGER` | 10 | Yes |
| `Yes3` | `INTEGER` | 10 | Yes |
| `Yes4` | `INTEGER` | 10 | Yes |
| `Yes5` | `INTEGER` | 10 | Yes |
| `Yes6` | `INTEGER` | 10 | Yes |
| `Yes7` | `INTEGER` | 10 | Yes |
| `Yes8` | `INTEGER` | 10 | Yes |
| `Yes9` | `INTEGER` | 10 | Yes |
| `Yes10` | `INTEGER` | 10 | Yes |
| `No1` | `INTEGER` | 10 | Yes |
| `No2` | `INTEGER` | 10 | Yes |
| `No3` | `INTEGER` | 10 | Yes |
| `No4` | `INTEGER` | 10 | Yes |
| `No5` | `INTEGER` | 10 | Yes |
| `No6` | `INTEGER` | 10 | Yes |
| `No7` | `INTEGER` | 10 | Yes |
| `No8` | `INTEGER` | 10 | Yes |
| `No9` | `INTEGER` | 10 | Yes |
| `No10` | `INTEGER` | 10 | Yes |
| `Ans11` | `INTEGER` | 10 | Yes |
| `Ans12` | `INTEGER` | 10 | Yes |
| `Ans13` | `INTEGER` | 10 | Yes |
| `Ans14` | `INTEGER` | 10 | Yes |
| `Ans15` | `INTEGER` | 10 | Yes |
| `Ans16` | `WVARCHAR` | 50 | Yes |
| `Datayear` | `WVARCHAR` | 4 | Yes |

### `Hostels`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Name` | `WVARCHAR` | 200 | Yes |
| `ContactPerson` | `WVARCHAR` | 250 | Yes |
| `address` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Tel` | `WVARCHAR` | 30 | Yes |

### `ICTAsistiveDeviceRecords`

- Estimated rows: `3`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `HasAsssDevice` | `TINYINT` | 3 | Yes |
| `NoHeld` | `INTEGER` | 10 | Yes |
| `NoReq` | `INTEGER` | 10 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `ICTCourseData`

- Estimated rows: `16`
- Heuristic primary key: `Course`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Course` | `WVARCHAR` | 50 | Yes |
| `Datayear` | `INTEGER` | 10 | Yes |
| `Managers` | `INTEGER` | 10 | Yes |
| `Educators` | `INTEGER` | 10 | Yes |
| `Administrators` | `INTEGER` | 10 | Yes |

### `ICTdata`

- Estimated rows: `97`
- Heuristic primary key: `Question`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Question` | `WVARCHAR` | 50 | Yes |
| `Answer` | `WVARCHAR` | 250 | Yes |
| `Datayear` | `INTEGER` | 10 | Yes |

### `ICTEConnectivityRecords`

- Estimated rows: `2`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `HasConnectivityTL` | `TINYINT` | 3 | Yes |
| `HasConnectivityadmin` | `TINYINT` | 3 | Yes |
| `ConSpeed` | `INTEGER` | 10 | Yes |
| `Broadband` | `WVARCHAR` | 1 | Yes |
| `ADSL` | `WVARCHAR` | 1 | Yes |
| `3GOr4GOrLTE` | `WVARCHAR` | 1 | Yes |
| `Other` | `WVARCHAR` | 1 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `ConnectivitySpeed` | `WLONGVARCHAR` | 1073741823 | Yes |

### `ICTElectronicContentRecords`

- Estimated rows: `3`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `HasElectronicContent` | `TINYINT` | 3 | Yes |
| `ContentSourceCom` | `WVARCHAR` | 1 | Yes |
| `ContentSourcePED` | `WVARCHAR` | 1 | Yes |
| `ContentSourceDBE` | `WVARCHAR` | 1 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `ICTInfrastuctureRecords`

- Estimated rows: `24`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `EquipCategory` | `INTEGER` | 10 | Yes |
| `QtyTL` | `INTEGER` | 10 | Yes |
| `QtyAdmin` | `INTEGER` | 10 | Yes |
| `Name` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `ICTSecuritydata`

- Estimated rows: `0`
- Heuristic primary key: `Roomtype`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Roomtype` | `WVARCHAR` | 50 | Yes |
| `Amount` | `INTEGER` | 10 | Yes |
| `Datayear` | `INTEGER` | 10 | Yes |
| `BurglarBars` | `BIT` | 1 | No |
| `SecurityDoor` | `BIT` | 1 | No |
| `Alarm` | `BIT` | 1 | No |

### `Info`

- Estimated rows: `1`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `UserName` | `WVARCHAR` | 50 | Yes |
| `Password` | `WVARCHAR` | 50 | Yes |
| `Level` | `INTEGER` | 10 | Yes |

### `InstructionLanguages`

- Estimated rows: `13`
- Heuristic primary key: `LangID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LangID` | `INTEGER` | 10 | No |
| `LangDesc` | `WVARCHAR` | 20 | Yes |

### `Inventory`

- Estimated rows: `0`
- Heuristic primary key: `InventoryId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `InventoryId` | `INTEGER` | 10 | No |
| `itemcode` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `AveCost` | `decimal.Decimal` |  | Yes |

### `InventoryLocation`

- Estimated rows: `0`
- Heuristic primary key: `InventoryId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `InventoryId` | `INTEGER` | 10 | Yes |
| `stockcode` | `str` |  | Yes |
| `Quantity` | `int` |  | Yes |
| `VenueId` | `int` |  | Yes |
| `SubVenue` | `int` |  | Yes |
| `InventoryStockID` | `int` |  | Yes |

### `InventoryQuantities`

- Estimated rows: `0`
- Heuristic primary key: `InventoryID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `InventoryID` | `INTEGER` | 10 | No |
| `stockcode` | `WVARCHAR` | 200 | Yes |
| `Quantity` | `int` |  | Yes |
| `AveCost` | `decimal.Decimal` |  | Yes |
| `TotalCost` | `decimal.Decimal` |  | Yes |
| `DateAdded` | `datetime.datetime` |  | Yes |
| `Register` | `str` |  | Yes |
| `VenueId` | `int` |  | Yes |
| `InventoryStockID` | `int` |  | Yes |

### `InventoryVenueTypes`

- Estimated rows: `0`
- Heuristic primary key: `VenueTypeId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `stockcode` | `WVARCHAR` | 200 | Yes |
| `VenueTypeId` | `INTEGER` | 10 | Yes |
| `InventoryStockID` | `INTEGER` | 10 | Yes |

### `InventoryWriteOff`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `itemid` | `str` |  | Yes |
| `InventoryId` | `int` |  | Yes |
| `WriteOffDate` | `datetime.datetime` |  | Yes |
| `Reason` | `str` |  | Yes |
| `Quantity` | `int` |  | Yes |
| `Authorised` | `str` |  | Yes |
| `Cost` | `decimal.Decimal` |  | Yes |
| `VenueId` | `int` |  | Yes |
| `InventoryStockID` | `int` |  | Yes |

### `IQMS_Educator_Appraisal`

- Estimated rows: `56`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `StandardID` | `INTEGER` | 10 | Yes |
| `CriteriaID` | `INTEGER` | 10 | Yes |
| `SelfEvaluation` | `INTEGER` | 10 | Yes |
| `DSG_Score` | `INTEGER` | 10 | Yes |
| `DSG1_Score` | `INTEGER` | 10 | Yes |
| `FinalScore` | `INTEGER` | 10 | Yes |
| `Strengths` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DevelopmentRecommendation` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ContextualFactorsNotes` | `WLONGVARCHAR` | 1073741823 | Yes |

### `IQMS_Educator_DSG`

- Estimated rows: `10`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `DSG_Member` | `INTEGER` | 10 | Yes |

### `IQMS_Educator_FinalScore`

- Estimated rows: `14`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `StandardID` | `INTEGER` | 10 | Yes |
| `FinalScore` | `INTEGER` | 10 | Yes |
| `Adjusted` | `BIT` | 1 | No |

### `IQMS_Educator_FinalScoreComments`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `IQMS_Educator_ImprovementPlan`

- Estimated rows: `0`
- Heuristic primary key: `StandardID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `StandardID` | `INTEGER` | 10 | Yes |
| `CriteriaID` | `INTEGER` | 10 | Yes |
| `CountFoundation` | `INTEGER` | 10 | Yes |
| `CountIntermediate` | `INTEGER` | 10 | Yes |
| `CountSenior` | `INTEGER` | 10 | Yes |
| `CountFET` | `INTEGER` | 10 | Yes |
| `ImprovementStrategies` | `WVARCHAR` | 255 | Yes |
| `EducatorIDs` | `WLONGVARCHAR` | 1073741823 | Yes |
| `EIPDate` | `WVARCHAR` | 100 | Yes |
| `Budget` | `WVARCHAR` | 100 | Yes |
| `AddressingNeeds` | `WVARCHAR` | 10 | Yes |

### `IQMS_Educator_PGP`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `StandardID` | `INTEGER` | 10 | Yes |
| `CriteriaID` | `INTEGER` | 10 | Yes |
| `Action` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Responsibility` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Timeframe` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Remarks` | `WLONGVARCHAR` | 1073741823 | Yes |

### `IQMS_Educator_PGP_Subjects`

- Estimated rows: `0`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `SubjLocalID` | `INTEGER` | 10 | Yes |
| `SubjOfficialID` | `INTEGER` | 10 | Yes |
| `Topic` | `WVARCHAR` | 255 | Yes |
| `Action` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Responsibility` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Timeframe` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Remarks` | `WLONGVARCHAR` | 1073741823 | Yes |

### `IQMS_PerformanceCriterias`

- Estimated rows: `52`
- Heuristic primary key: `StandardID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `StandardID` | `INTEGER` | 10 | Yes |
| `CriteriaID` | `INTEGER` | 10 | Yes |
| `CriteriaLetter` | `WVARCHAR` | 5 | Yes |
| `Criteria` | `WVARCHAR` | 255 | Yes |

### `IQMS_PerformanceLevels`

- Estimated rows: `208`
- Heuristic primary key: `StandardID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `StandardID` | `INTEGER` | 10 | Yes |
| `CriteriaID` | `INTEGER` | 10 | Yes |
| `LevelNo` | `INTEGER` | 10 | Yes |
| `LevelDesc` | `WLONGVARCHAR` | 1073741823 | Yes |

### `IQMS_PerformanceStandards`

- Estimated rows: `12`
- Heuristic primary key: `StandardID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `StandardID` | `INTEGER` | 10 | Yes |
| `Standard` | `WVARCHAR` | 255 | Yes |
| `MaxScore` | `INTEGER` | 10 | Yes |
| `Expectation` | `WVARCHAR` | 255 | Yes |
| `Question` | `WVARCHAR` | 255 | Yes |
| `LevelsOfPerformance` | `WVARCHAR` | 255 | Yes |

### `IQMS_PM_CheckList`

- Estimated rows: `13`
- Heuristic primary key: `EdID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `INTEGER` | 10 | Yes |
| `EdID` | `INTEGER` | 10 | Yes |
| `ItemID` | `INTEGER` | 10 | Yes |
| `AvailabilityStatus` | `INTEGER` | 10 | Yes |
| `Comments` | `WLONGVARCHAR` | 1073741823 | Yes |

### `IQMS_PM_CheckListItems`

- Estimated rows: `13`
- Heuristic primary key: `ItemID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemID` | `INTEGER` | 10 | Yes |
| `ItemDesc` | `WVARCHAR` | 255 | Yes |

### `Journals`

- Estimated rows: `4334`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `JournalNumber` | `INTEGER` | 10 | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `CoaNum` | `int` |  | Yes |
| `Dept` | `int` |  | Yes |
| `DebitAmount` | `decimal.Decimal` |  | Yes |
| `CreditAmount` | `decimal.Decimal` |  | Yes |
| `Description` | `str` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNum` | `int` |  | Yes |

### `Learner_Info`

- Estimated rows: `1656`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `AccessionNo` | `str` |  | Yes |
| `TheDate` | `str` |  | Yes |
| `SName` | `str` |  | Yes |
| `FName` | `str` |  | Yes |
| `NickName` | `str` |  | Yes |
| `BirthDate` | `str` |  | Yes |
| `IDNo` | `str` |  | Yes |
| `Gender` | `str` |  | Yes |
| `HomeLanguage` | `int` |  | Yes |
| `InstructionLanguage` | `int` |  | Yes |
| `PreferredLanguage` | `int` |  | Yes |
| `Address1` | `str` |  | Yes |
| `Address2` | `str` |  | Yes |
| `Address3` | `str` |  | Yes |
| `AddressCode` | `str` |  | Yes |
| `Guardian` | `str` |  | Yes |
| `Tel1Code` | `str` |  | Yes |
| `Tel1` | `str` |  | Yes |
| `Tel2Code` | `str` |  | Yes |
| `Tel2` | `str` |  | Yes |
| `Tel3Code` | `str` |  | Yes |
| `Tel3` | `str` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Class` | `int` |  | Yes |
| `GradeYears` | `int` |  | Yes |
| `PreviousSchool` | `str` |  | Yes |
| `SchoolAddress1` | `str` |  | Yes |
| `SchoolAddress2` | `str` |  | Yes |
| `SchoolAddress3` | `str` |  | Yes |
| `SchoolCode` | `str` |  | Yes |
| `Religion` | `str` |  | Yes |
| `Disciplinary` | `str` |  | Yes |
| `MedicalConditions` | `str` |  | Yes |
| `DrInfo` | `str` |  | Yes |
| `MedicalAidName` | `str` |  | Yes |
| `MedicalAidNo` | `str` |  | Yes |
| `MedicalAidMember` | `str` |  | Yes |
| `Guidance` | `str` |  | Yes |
| `Initials` | `str` |  | Yes |
| `Citizenship` | `str` |  | Yes |
| `Provincial` | `str` |  | Yes |
| `SchoolProvince` | `str` |  | Yes |
| `PreviousSchoolProvince` | `str` |  | Yes |
| `AssignClass` | `bool` |  | Yes |
| `PhysProvince` | `str` |  | Yes |
| `Race` | `str` |  | Yes |
| `Title` | `str` |  | Yes |
| `PreviousPlacementofSchool` | `int` |  | Yes |
| `Transport` | `int` |  | Yes |
| `LSENDisabilities` | `int` |  | Yes |
| `DateLeft` | `str` |  | Yes |
| `Reason` | `str` |  | Yes |
| `LSENStatus` | `int` |  | Yes |
| `Status` | `str` |  | Yes |
| `Boarder` | `int` |  | Yes |
| `CountryResidence` | `str` |  | Yes |
| `ProvinceResidence` | `str` |  | Yes |
| `FirstProvince` | `int` |  | Yes |
| `DeceasedParent` | `int` |  | Yes |
| `SGRegister` | `int` |  | Yes |
| `SGReceive` | `int` |  | Yes |
| `DrName` | `str` |  | Yes |
| `DrTel` | `str` |  | Yes |
| `Dexterity` | `int` |  | Yes |
| `PSNP` | `int` |  | Yes |
| `NoFamily` | `int` |  | Yes |
| `PositionFamily` | `str` |  | Yes |
| `ReportLanguage` | `int` |  | Yes |
| `GradeEntered` | `int` |  | Yes |
| `GradeLeft` | `int` |  | Yes |
| `BoarderNumber` | `str` |  | Yes |
| `ThirdName` | `str` |  | Yes |
| `Email` | `str` |  | Yes |
| `PhotoName` | `str` |  | Yes |
| `BoarderHostel` | `str` |  | Yes |
| `TSTransactionCategory` | `int` |  | Yes |
| `TSStatusFlag` | `int` |  | Yes |
| `TSReportStatusFlag` | `int` |  | Yes |
| `TSReasonCode` | `int` |  | Yes |
| `LuritsIndicator` | `int` |  | Yes |
| `LuritsNumber` | `float` |  | Yes |
| `TSSentfileName` | `str` |  | Yes |
| `TSDateLastUpdate` | `datetime.datetime` |  | Yes |
| `TSLastUpdatedBy` | `str` |  | Yes |
| `LearnerName2` | `str` |  | Yes |
| `LearnerName3` | `str` |  | Yes |
| `NameDiacritics` | `str` |  | Yes |
| `OtherHomeLanguage` | `str` |  | Yes |
| `OtherLanguage` | `str` |  | Yes |
| `OtherPreferredLanguage` | `str` |  | Yes |
| `OtherTeachingLanguage` | `str` |  | Yes |
| `SecondName` | `str` |  | Yes |
| `SocialGrantNo` | `str` |  | Yes |
| `LuritsFlag` | `int` |  | Yes |
| `PastelCode` | `str` |  | Yes |
| `ForeignID` | `str` |  | Yes |
| `LuritsStatus` | `str` |  | Yes |
| `BusRouteId` | `int` |  | Yes |
| `LearnerComment` | `str` |  | Yes |
| `LearnerTotalNumber` | `int` |  | Yes |
| `Subj_HL` | `str` |  | Yes |
| `Subj_FAL` | `str` |  | Yes |
| `PrevSName` | `str` |  | Yes |
| `PositionFamilyF` | `str` |  | Yes |
| `ReasonForNoIDNo` | `int` |  | Yes |
| `GrantCReg` | `int` |  | Yes |
| `GrantCReceive` | `int` |  | Yes |
| `GrantCNo` | `str` |  | Yes |
| `Grant4Reg` | `int` |  | Yes |
| `Grant4Receive` | `int` |  | Yes |
| `Grant4No` | `str` |  | Yes |
| `Grant5Reg` | `int` |  | Yes |
| `Grant5Receive` | `int` |  | Yes |
| `Grant5No` | `str` |  | Yes |
| `Grant9Reg` | `int` |  | Yes |
| `Grant9Receive` | `int` |  | Yes |
| `Grant9No` | `str` |  | Yes |
| `ClinicName` | `str` |  | Yes |
| `ClinicAccRef` | `str` |  | Yes |
| `ClinicTelCode` | `str` |  | Yes |
| `ClinicTel` | `str` |  | Yes |
| `Subj_LOI` | `str` |  | Yes |
| `HseID` | `int` |  | Yes |
| `PhaseYears` | `int` |  | Yes |
| `ProgressedToGrade` | `bool` |  | Yes |
| `StudyPermit` | `int` |  | Yes |
| `StudyPermitNo` | `str` |  | Yes |
| `StudyPermitDate` | `str` |  | Yes |
| `IDNoNotValidating` | `str` |  | Yes |
| `OldMentor` | `str` |  | Yes |
| `LSENAnaInc` | `bool` |  | Yes |
| `LSENAnaHL` | `str` |  | Yes |
| `LSENAnaFAL` | `str` |  | Yes |
| `PreviousPlacementofSchoolYear` | `int` |  | Yes |
| `ForeignIDType` | `int` |  | Yes |
| `AgeRuleOverwritten` | `bool` |  | Yes |
| `ReasonForNoForeignID` | `int` |  | Yes |
| `FarmProj` | `str` |  | Yes |
| `Road2Health` | `bool` |  | Yes |
| `ImmunizationCard` | `bool` |  | Yes |
| `ICEName` | `str` |  | Yes |
| `ICESurname` | `str` |  | Yes |
| `ICERelation` | `str` |  | Yes |
| `Repeat12` | `bool` |  | Yes |
| `ExamNr` | `str` |  | Yes |
| `SAMS12LRNID` | `str` |  | Yes |
| `GrRFund` | `str` |  | Yes |
| `FeeExempt` | `str` |  | Yes |
| `StudyTime` | `str` |  | Yes |
| `LearnerPAMDisability` | `float` |  | Yes |

### `LearnerApplications`

- Estimated rows: `0`
- Heuristic primary key: `ApplicationId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ApplicationId` | `INTEGER` | 10 | No |
| `Sname` | `str` |  | Yes |
| `Fname` | `str` |  | Yes |
| `GradeAppliedFor` | `str` |  | Yes |
| `YearAppliedFor` | `str` |  | Yes |
| `ApplicationDate` | `datetime.datetime` |  | Yes |
| `DateOfBirth` | `str` |  | Yes |
| `Gender` | `str` |  | Yes |
| `Race` | `str` |  | Yes |
| `HomeLanguage` | `str` |  | Yes |
| `Siblings` | `int` |  | Yes |
| `ParentTitle` | `str` |  | Yes |
| `ParentSname` | `str` |  | Yes |
| `ParentInitials` | `str` |  | Yes |
| `PostAddress1` | `str` |  | Yes |
| `PostAddress2` | `str` |  | Yes |
| `PostCity` | `str` |  | Yes |
| `PostCode` | `str` |  | Yes |
| `PhysicalAddress1` | `str` |  | Yes |
| `PhysicalAddress2` | `str` |  | Yes |
| `PhysicalCity` | `str` |  | Yes |
| `PhysicalCode` | `str` |  | Yes |
| `Tel1` | `str` |  | Yes |
| `Tel2` | `str` |  | Yes |
| `FeederSchool` | `str` |  | Yes |
| `AppStatus` | `str` |  | Yes |
| `Reason` | `str` |  | Yes |
| `Boarder` | `int` |  | Yes |
| `BoarderNumber` | `str` |  | Yes |
| `BoarderHostel` | `str` |  | Yes |

### `LearnerAttendance`

- Estimated rows: `2784`
- Heuristic primary key: `DataYear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Quarter` | `int` |  | Yes |
| `Gender` | `str` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Quantity` | `float` |  | Yes |
| `Type` | `str` |  | Yes |
| `Enrolment` | `int` |  | Yes |

### `LearnerCass`

- Estimated rows: `406992`
- Heuristic primary key: `Learnerid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Learnerid` | `INTEGER` | 10 | Yes |
| `Subjectid` | `int` |  | Yes |
| `CriterionId` | `int` |  | Yes |
| `Datayear` | `str` |  | Yes |
| `Mark` | `float` |  | Yes |
| `Comments` | `str` |  | Yes |
| `DateAdded` | `datetime.datetime` |  | Yes |
| `Criterionscore` | `int` |  | Yes |
| `OBEsymbol` | `int` |  | Yes |
| `EvalVer` | `int` |  | Yes |
| `Status` | `int` |  | Yes |
| `RecId` | `int` |  | Yes |
| `ModMark` | `int` |  | Yes |

### `LearnerCassActivities`

- Estimated rows: `264713`
- Heuristic primary key: `ActivityID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ActivityID` | `INTEGER` | 10 | Yes |
| `LearnerId` | `INTEGER` | 10 | Yes |
| `CriterionID` | `INTEGER` | 10 | Yes |
| `RawMark` | `DOUBLE` | 53 | Yes |
| `Datayear` | `WVARCHAR` | 20 | Yes |
| `Status` | `TINYINT` | 3 | Yes |
| `RecId` | `INTEGER` | 10 | No |

### `LearnerClasses`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccessionNo` | `WVARCHAR` | 50 | Yes |
| `Class` | `WVARCHAR` | 50 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Id` | `INTEGER` | 10 | No |

### `LearnerCTA`

- Estimated rows: `0`
- Heuristic primary key: `Learnerid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Learnerid` | `INTEGER` | 10 | Yes |
| `Subjectid` | `int` |  | Yes |
| `TaskId` | `int` |  | Yes |
| `Datayear` | `str` |  | Yes |
| `Mark` | `int` |  | Yes |
| `Comments` | `str` |  | Yes |
| `DateAdded` | `datetime.datetime` |  | Yes |
| `TaskScore` | `int` |  | Yes |
| `OBeSymbol` | `int` |  | Yes |

### `LearnerDeworming`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Linkid` | `INTEGER` | 10 | Yes |
| `Sname` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Initials` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Incident` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Datayear` | `WVARCHAR` | 4 | Yes |
| `Gender` | `WVARCHAR` | 6 | Yes |
| `SideEffects` | `INTEGER` | 10 | Yes |

### `LearnerExamRegistration`

- Estimated rows: `362`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerID` | `INTEGER` | 10 | Yes |
| `ExamYear` | `INTEGER` | 10 | Yes |
| `RegistrationType` | `WVARCHAR` | 10 | Yes |
| `ExamName` | `WVARCHAR` | 10 | Yes |
| `ExamType` | `WVARCHAR` | 10 | Yes |
| `ImmigrationStatus` | `WVARCHAR` | 20 | Yes |
| `CandidateReferenceNumber` | `WVARCHAR` | 20 | Yes |
| `RegistrationIDType` | `WVARCHAR` | 10 | Yes |
| `PostalAddress1` | `WVARCHAR` | 70 | Yes |
| `PostalAddress2` | `WVARCHAR` | 70 | Yes |
| `PostalAddress3` | `WVARCHAR` | 70 | Yes |
| `PostalAddress4` | `WVARCHAR` | 70 | Yes |
| `PostalCode` | `WVARCHAR` | 10 | Yes |
| `EndorsementType` | `WVARCHAR` | 50 | Yes |
| `CertificateLanguage` | `INTEGER` | 10 | Yes |
| `SpecialNeed` | `WVARCHAR` | 50 | Yes |
| `NSCSpecialNeed` | `WVARCHAR` | 10 | Yes |
| `WrittenRsa` | `WVARCHAR` | 10 | Yes |
| `CountryWritten` | `WVARCHAR` | 100 | Yes |
| `PaperLanguage` | `WVARCHAR` | 50 | Yes |

### `LearnerExamRegistrationSubjects`

- Estimated rows: `1720`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ExamYear` | `INTEGER` | 10 | Yes |
| `LearnerId` | `INTEGER` | 10 | Yes |
| `OfficialSubjectID` | `INTEGER` | 10 | Yes |
| `SortNo` | `TINYINT` | 3 | Yes |
| `NscCode` | `WVARCHAR` | 10 | Yes |
| `SubjName` | `WVARCHAR` | 200 | Yes |
| `NscInstrument` | `WVARCHAR` | 50 | Yes |

### `LearnerExamRegistrationV2`

- Estimated rows: `246`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ExamYear` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `RegistrationType` | `TINYINT` | 3 | Yes |
| `NoFeeCandidate` | `WVARCHAR` | 1 | Yes |
| `SNEAccommodationConcession` | `WVARCHAR` | 255 | Yes |
| `SpecialNeedsCodes` | `WVARCHAR` | 255 | Yes |
| `PostalAddress1` | `WVARCHAR` | 50 | Yes |
| `PostalAddress2` | `WVARCHAR` | 50 | Yes |
| `PostalAddress3` | `WVARCHAR` | 50 | Yes |
| `PostalCode` | `WVARCHAR` | 10 | Yes |
| `SecChanceProgrammeReg` | `WVARCHAR` | 1 | Yes |
| `ImmigrantLanguageConcession` | `WVARCHAR` | 1 | Yes |
| `Mathematicalconcession` | `WVARCHAR` | 1 | Yes |
| `Languageconcession` | `WVARCHAR` | 1 | Yes |
| `PublicationOffinalResults` | `WVARCHAR` | 1 | Yes |
| `ResultsViaSMS` | `WVARCHAR` | 1 | Yes |
| `SubmissionOfResultsToHI` | `WVARCHAR` | 1 | Yes |
| `SubmissionOfResultsToNFSAS` | `WVARCHAR` | 1 | Yes |
| `SubmissionOfDataForResearch` | `WVARCHAR` | 1 | Yes |
| `SubmissionOfDataForResearch1` | `WVARCHAR` | 1 | Yes |
| `FiveSubjectEntry` | `WVARCHAR` | 1 | Yes |
| `AccommodationConcessionOther` | `WVARCHAR` | 100 | Yes |

### `LearnerMAttendance`

- Estimated rows: `15`
- Heuristic primary key: `EnrolmentMale`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EnrolmentMale` | `INTEGER` | 10 | Yes |
| `EnrolmentFemale` | `INTEGER` | 10 | Yes |
| `TotalEnrolment` | `INTEGER` | 10 | Yes |
| `PossibleAttendanceMale` | `INTEGER` | 10 | Yes |
| `PossibleAttendanceFemale` | `INTEGER` | 10 | Yes |
| `TotalPossible` | `INTEGER` | 10 | Yes |
| `DaysAbsentForMonthMale` | `INTEGER` | 10 | Yes |
| `DaysAbsentForMonthFemale` | `INTEGER` | 10 | Yes |
| `TotalDaysAbsentForMonth` | `INTEGER` | 10 | Yes |
| `ActualLearnerAttendanceMale` | `INTEGER` | 10 | Yes |
| `ActualLearnerAttendanceFemale` | `INTEGER` | 10 | Yes |
| `TotalActualLearnerAttendance` | `INTEGER` | 10 | Yes |
| `AverageAttendance` | `INTEGER` | 10 | Yes |
| `AverageAbsentees` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |
| `DataMonth` | `INTEGER` | 10 | Yes |

### `LearnerMedConTypes`

- Estimated rows: `27`
- Heuristic primary key: `MedConTypeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MedConTypeID` | `INTEGER` | 10 | Yes |
| `MedConditionDesc` | `WVARCHAR` | 100 | Yes |
| `DomainCode` | `WVARCHAR` | 10 | Yes |

### `LearnerMedicals`

- Estimated rows: `0`
- Heuristic primary key: `MedicalID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MedicalID` | `INTEGER` | 10 | No |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `MedConTypeID` | `INTEGER` | 10 | Yes |
| `MedConTypeOther` | `WVARCHAR` | 100 | Yes |
| `DateStart` | `TIMESTAMP` | 19 | Yes |
| `DateEnd` | `TIMESTAMP` | 19 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `LearnerMedications`

- Estimated rows: `0`
- Heuristic primary key: `MedicationID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MedicationID` | `INTEGER` | 10 | No |
| `MedicalID` | `INTEGER` | 10 | Yes |
| `MedicationTime` | `WVARCHAR` | 5 | Yes |
| `MedicationDesc` | `WVARCHAR` | 100 | Yes |
| `MedicationComment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `LearnerMentors`

- Estimated rows: `0`
- Heuristic primary key: `MentorID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MentorID` | `INTEGER` | 10 | No |
| `TypeID` | `INTEGER` | 10 | Yes |
| `LinkID` | `INTEGER` | 10 | Yes |
| `SName` | `WVARCHAR` | 100 | Yes |
| `FName` | `WVARCHAR` | 70 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Status` | `WVARCHAR` | 20 | Yes |

### `LearnerMentorshipCats`

- Estimated rows: `3`
- Heuristic primary key: `CatID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CatID` | `INTEGER` | 10 | No |
| `CatDesc` | `WVARCHAR` | 100 | Yes |
| `CatDescAfr` | `WVARCHAR` | 100 | Yes |

### `LearnerMentorships`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `CatID` | `INTEGER` | 10 | Yes |
| `MentorID` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `DateStart` | `TIMESTAMP` | 19 | Yes |
| `DateEnd` | `TIMESTAMP` | 19 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `LearnerMentorTypes`

- Estimated rows: `16`
- Heuristic primary key: `TypeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TypeID` | `INTEGER` | 10 | No |
| `TypeDesc` | `WVARCHAR` | 100 | Yes |
| `TypeDescAfr` | `WVARCHAR` | 100 | Yes |

### `LearnerMovement`

- Estimated rows: `1842`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `AccessionNo` | `str` |  | Yes |
| `DateArrived` | `datetime.datetime` |  | Yes |
| `DateLeft` | `datetime.datetime` |  | Yes |
| `Reason` | `str` |  | Yes |
| `GradeLeft` | `int` |  | Yes |
| `GradeEntered` | `int` |  | Yes |

### `LearnerPerformance`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field811` | `WVARCHAR` | 10 | Yes |
| `Field812` | `str` |  | Yes |
| `Field813` | `str` |  | Yes |
| `Field814` | `str` |  | Yes |
| `Field815` | `str` |  | Yes |
| `Field816` | `str` |  | Yes |
| `Field817` | `str` |  | Yes |
| `Field818` | `str` |  | Yes |
| `Field82` | `int` |  | Yes |
| `Field83` | `str` |  | Yes |
| `Field84` | `int` |  | Yes |
| `Field851` | `int` |  | Yes |
| `Field852` | `int` |  | Yes |
| `Field853` | `int` |  | Yes |
| `Field854` | `int` |  | Yes |

### `LearnerProgression`

- Estimated rows: `6650`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerID` | `INTEGER` | 10 | Yes |
| `AcademicYear` | `WVARCHAR` | 20 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Class` | `INTEGER` | 10 | Yes |
| `ProgressionStatus` | `WVARCHAR` | 20 | Yes |
| `AccessionNo` | `WVARCHAR` | 100 | Yes |
| `ClassName` | `WVARCHAR` | 50 | Yes |

### `LearnerPromotion`

- Estimated rows: `19070`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `PromotionDecision` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `LearnerAverage` | `DOUBLE` | 53 | Yes |
| `LearnerScore` | `DOUBLE` | 53 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ReportComment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |
| `FETPassLevel` | `WVARCHAR` | 50 | Yes |
| `DistrictRemark` | `WLONGVARCHAR` | 1073741823 | Yes |
| `CodeSelected` | `WVARCHAR` | 5 | Yes |
| `CodeAuto` | `WVARCHAR` | 5 | Yes |
| `CodeAutoDesc` | `WLONGVARCHAR` | 1073741823 | Yes |
| `CodeSched` | `WVARCHAR` | 5 | Yes |

### `LearnerPromotionDefaultComments`

- Estimated rows: `75`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `SortNo` | `INTEGER` | 10 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |
| `AfrComment` | `WVARCHAR` | 250 | Yes |
| `GradeFrom` | `INTEGER` | 10 | Yes |
| `GradeTo` | `INTEGER` | 10 | Yes |
| `ForTerm` | `INTEGER` | 10 | Yes |

### `LearnerSubjectLanguages`

- Estimated rows: `0`
- Heuristic primary key: `LanguageId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Phase` | `WVARCHAR` | 20 | Yes |
| `LanguageId` | `INTEGER` | 10 | Yes |
| `LanguageLevel` | `str` |  | Yes |
| `Quantity` | `int` |  | Yes |
| `DataYear` | `str` |  | Yes |

### `LearnerSubjects`

- Estimated rows: `3325`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerId` | `INTEGER` | 10 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `SubjectSetId` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `EducatorGroupId` | `INTEGER` | 10 | Yes |
| `Subjectlevel` | `WVARCHAR` | 20 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `LanguageType` | `INTEGER` | 10 | Yes |
| `TSTransactionCategory` | `INTEGER` | 10 | Yes |
| `TSStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReportStatusFlag` | `INTEGER` | 10 | Yes |
| `TSReasonCode` | `INTEGER` | 10 | Yes |
| `ExcludeAve` | `BIT` | 1 | No |

### `LearnerSupportMaterials`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field911` | `INTEGER` | 10 | Yes |
| `Field912` | `int` |  | Yes |
| `Field913` | `int` |  | Yes |
| `Field914` | `int` |  | Yes |
| `Field921` | `int` |  | Yes |
| `Field922` | `int` |  | Yes |
| `Field923` | `int` |  | Yes |
| `Field924` | `int` |  | Yes |
| `Field931` | `int` |  | Yes |
| `Field932` | `int` |  | Yes |
| `Field933` | `int` |  | Yes |
| `Field934` | `int` |  | Yes |
| `Field935` | `int` |  | Yes |
| `Field936` | `int` |  | Yes |
| `Field937` | `int` |  | Yes |
| `Field938` | `int` |  | Yes |
| `Field941` | `int` |  | Yes |
| `Field942` | `int` |  | Yes |
| `Field95` | `int` |  | Yes |
| `Field96` | `str` |  | Yes |
| `Field97` | `int` |  | Yes |

### `LearnerTranferCard`

- Estimated rows: `0`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `DateIssued` | `TIMESTAMP` | 19 | Yes |
| `ReportMarksDatayear` | `WVARCHAR` | 10 | Yes |
| `PassYear` | `WVARCHAR` | 10 | Yes |
| `PassGrade` | `INTEGER` | 10 | Yes |
| `LinkID` | `TINYINT` | 3 | Yes |

### `LearningBarriers`

- Estimated rows: `0`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Date` | `datetime.datetime` |  | Yes |
| `Learnerid` | `int` |  | Yes |
| `Comment` | `str` |  | Yes |
| `Barriercode` | `int` |  | Yes |
| `ActionCode` | `int` |  | Yes |

### `LetterHeadSettings`

- Estimated rows: `13`
- Heuristic primary key: `ReportId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ReportId` | `INTEGER` | 10 | Yes |
| `ReportDescription` | `WVARCHAR` | 100 | Yes |
| `SystemPageHeaderHeight` | `DOUBLE` | 53 | Yes |
| `SystemPageFooterHeight` | `DOUBLE` | 53 | Yes |
| `SystemPageLeftMargin` | `DOUBLE` | 53 | Yes |
| `SystemPageRightMargin` | `DOUBLE` | 53 | Yes |
| `PrintedPageHeaderHeight` | `DOUBLE` | 53 | Yes |
| `PrintedPageFooterHeight` | `DOUBLE` | 53 | Yes |
| `PrintedPageLeftMargin` | `DOUBLE` | 53 | Yes |
| `PrintedPageRightMargin` | `DOUBLE` | 53 | Yes |

### `Look_UpGE`

- Estimated rows: `367`
- Heuristic primary key: `WordId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `WordId` | `INTEGER` | 10 | No |
| `Dept` | `INTEGER` | 10 | Yes |
| `Keyword` | `WVARCHAR` | 200 | Yes |
| `KeyCounter` | `INTEGER` | 10 | Yes |
| `CoaNo` | `INTEGER` | 10 | Yes |

### `Look_UpNC`

- Estimated rows: `793`
- Heuristic primary key: `WordId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `WordId` | `INTEGER` | 10 | No |
| `Dept` | `INTEGER` | 10 | Yes |
| `Keyword` | `WVARCHAR` | 200 | Yes |
| `KeyCounter` | `INTEGER` | 10 | Yes |
| `CoaNo` | `INTEGER` | 10 | Yes |

### `Look_UpWC`

- Estimated rows: `373`
- Heuristic primary key: `WordId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `WordId` | `INTEGER` | 10 | No |
| `Dept` | `INTEGER` | 10 | Yes |
| `Keyword` | `WVARCHAR` | 200 | Yes |
| `KeyCounter` | `INTEGER` | 10 | Yes |
| `CoaNo` | `INTEGER` | 10 | Yes |

### `LsmAreas`

- Estimated rows: `54`
- Heuristic primary key: `AreaID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AreaID` | `INTEGER` | 10 | No |
| `GroupID` | `INTEGER` | 10 | Yes |
| `Area` | `WVARCHAR` | 255 | Yes |
| `OffAreaID` | `INTEGER` | 10 | Yes |

### `LsmAreasGroups`

- Estimated rows: `4`
- Heuristic primary key: `GroupID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `GroupID` | `INTEGER` | 10 | Yes |
| `Group` | `WVARCHAR` | 255 | Yes |

### `LsmAreasSubjects`

- Estimated rows: `1454`
- Heuristic primary key: `AreaID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AreaID` | `INTEGER` | 10 | Yes |
| `SubjID` | `INTEGER` | 10 | Yes |
| `OffSubjID` | `INTEGER` | 10 | Yes |

### `LsmAuthors`

- Estimated rows: `1233`
- Heuristic primary key: `AuthID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AuthID` | `INTEGER` | 10 | No |
| `Author` | `WVARCHAR` | 255 | Yes |

### `LsmCategories`

- Estimated rows: `25`
- Heuristic primary key: `CatID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CatID` | `INTEGER` | 10 | No |
| `Category` | `WVARCHAR` | 255 | Yes |

### `LsmItems`

- Estimated rows: `14380`
- Heuristic primary key: `ItemID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemID` | `INTEGER` | 10 | No |
| `AreaID` | `INTEGER` | 10 | Yes |
| `TypeNo` | `INTEGER` | 10 | Yes |
| `Item` | `WVARCHAR` | 255 | Yes |
| `ISBN` | `WVARCHAR` | 50 | Yes |
| `PubID` | `INTEGER` | 10 | Yes |
| `AuthID` | `INTEGER` | 10 | Yes |
| `ManuID` | `INTEGER` | 10 | Yes |
| `ItemYear` | `WVARCHAR` | 20 | Yes |
| `CatID` | `INTEGER` | 10 | Yes |
| `LangID` | `INTEGER` | 10 | Yes |
| `OffItemID` | `INTEGER` | 10 | Yes |
| `OffAreaID` | `INTEGER` | 10 | Yes |
| `OffSubjID` | `INTEGER` | 10 | Yes |
| `Status` | `WVARCHAR` | 1 | Yes |

### `LsmItemsSubjects`

- Estimated rows: `26587`
- Heuristic primary key: `ItemID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ItemID` | `INTEGER` | 10 | Yes |
| `SubjID` | `INTEGER` | 10 | Yes |
| `OffSubjID` | `INTEGER` | 10 | Yes |

### `LsmLanguages`

- Estimated rows: `14`
- Heuristic primary key: `LangID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LangID` | `INTEGER` | 10 | Yes |
| `Language` | `WVARCHAR` | 20 | Yes |

### `LsmLoans`

- Estimated rows: `621`
- Heuristic primary key: `LoanID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LoanID` | `INTEGER` | 10 | No |
| `ItemID` | `INTEGER` | 10 | Yes |
| `DateLoaned` | `TIMESTAMP` | 19 | Yes |
| `ExpectedReturn` | `TIMESTAMP` | 19 | Yes |
| `DateReturned` | `TIMESTAMP` | 19 | Yes |
| `LoanedToType` | `INTEGER` | 10 | Yes |
| `LoanedTo` | `INTEGER` | 10 | Yes |
| `LoanQuantity` | `INTEGER` | 10 | Yes |
| `ReturnQuantity` | `INTEGER` | 10 | Yes |
| `Condition` | `WVARCHAR` | 100 | Yes |
| `LoanVenue` | `INTEGER` | 10 | Yes |

### `LsmManufacturers`

- Estimated rows: `1`
- Heuristic primary key: `ManuID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ManuID` | `INTEGER` | 10 | No |
| `Manufacturer` | `WVARCHAR` | 255 | Yes |

### `LsmPublishers`

- Estimated rows: `219`
- Heuristic primary key: `PubID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PubID` | `INTEGER` | 10 | No |
| `Publisher` | `WVARCHAR` | 255 | Yes |

### `LsmQuantities`

- Estimated rows: `293`
- Heuristic primary key: `QuantityID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `QuantityID` | `INTEGER` | 10 | No |
| `ItemID` | `INTEGER` | 10 | Yes |
| `Quantity` | `INTEGER` | 10 | Yes |
| `UnitCost` | `NUMERIC` | 19 | Yes |
| `TotalCost` | `NUMERIC` | 19 | Yes |
| `DateAdded` | `TIMESTAMP` | 19 | Yes |
| `Register` | `WVARCHAR` | 50 | Yes |

### `LsmWriteOff`

- Estimated rows: `91`
- Heuristic primary key: `WriteOffID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `WriteOffID` | `INTEGER` | 10 | No |
| `ItemID` | `INTEGER` | 10 | Yes |
| `QuantityID` | `INTEGER` | 10 | Yes |
| `WriteOffDate` | `TIMESTAMP` | 19 | Yes |
| `Quantity` | `INTEGER` | 10 | Yes |
| `Cost` | `NUMERIC` | 19 | Yes |
| `Reason` | `WVARCHAR` | 100 | Yes |
| `Authorised` | `WVARCHAR` | 100 | Yes |

### `LuritsDatabaseDeployment`

- Estimated rows: `115`
- Heuristic primary key: `DeploymentId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DeploymentId` | `INTEGER` | 10 | No |
| `DeploymentCode` | `WVARCHAR` | 50 | Yes |
| `DeploymentDate` | `TIMESTAMP` | 19 | Yes |

### `ModeTransport`

- Estimated rows: `16`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Mode` | `str` |  | Yes |

### `MonthlyBudgets`

- Estimated rows: `0`
- Heuristic primary key: `AccNo`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AccNo` | `INTEGER` | 10 | Yes |
| `Month` | `INTEGER` | 10 | Yes |
| `Amount` | `DOUBLE` | 53 | Yes |
| `Year` | `WVARCHAR` | 10 | Yes |
| `SubAccNo` | `INTEGER` | 10 | Yes |

### `Mortality`

- Estimated rows: `67`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Linkid` | `INTEGER` | 10 | Yes |
| `Individualid` | `str` |  | Yes |
| `Category` | `str` |  | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `Sname` | `str` |  | Yes |
| `Initials` | `str` |  | Yes |
| `Incident` | `str` |  | Yes |
| `Comment` | `str` |  | Yes |
| `Mortality` | `str` |  | Yes |
| `AgeRange` | `str` |  | Yes |
| `Gender` | `str` |  | Yes |
| `PregLeaveFrom` | `datetime.datetime` |  | Yes |
| `PregLeaveTo` | `datetime.datetime` |  | Yes |
| `ReJoinedDate` | `datetime.datetime` |  | Yes |
| `ReJoinedReason` | `str` |  | Yes |
| `Maternity_card` | `bool` |  | Yes |
| `Est_Delivery_date` | `datetime.datetime` |  | Yes |
| `Ref_4_Care` | `bool` |  | Yes |
| `Ref_By` | `str` |  | Yes |
| `Out_Ref_agent` | `str` |  | Yes |

### `MultipleDisabilities`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerID` | `INTEGER` | 10 | Yes |
| `DisabilityID` | `INTEGER` | 10 | Yes |
| `Knumber` | `WVARCHAR` | 200 | Yes |
| `TestDate` | `TIMESTAMP` | 19 | Yes |

### `NonInstructionalAreas`

- Estimated rows: `8`
- Heuristic primary key: `Datayear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Type` | `INTEGER` | 10 | Yes |
| `Quantity` | `INTEGER` | 10 | Yes |

### `OBEEvaluations`

- Estimated rows: `11`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Code` | `str` |  | Yes |
| `Description` | `str` |  | Yes |
| `AfrDescription` | `str` |  | Yes |
| `Phase` | `str` |  | Yes |

### `OtherPurposeAreas`

- Estimated rows: `6`
- Heuristic primary key: `Datayear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Type` | `INTEGER` | 10 | Yes |
| `Quantity` | `INTEGER` | 10 | Yes |

### `PAMDisabilityCategory`

- Estimated rows: `14`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Description` | `WVARCHAR` | 100 | Yes |
| `Weight` | `WVARCHAR` | 10 | Yes |

### `Parent_Child`

- Estimated rows: `2098`
- Heuristic primary key: `ParentId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ParentId` | `INTEGER` | 10 | Yes |
| `ChildId` | `int` |  | Yes |
| `Learnerid` | `str` |  | Yes |
| `AccPayer` | `bool` |  | Yes |
| `Status` | `str` |  | Yes |
| `Resides` | `str` |  | Yes |
| `FamilyCode` | `str` |  | Yes |
| `PastelCustomerAccountDescription` | `str` |  | Yes |
| `PastelCustomerCategoryCode` | `int` |  | Yes |
| `PastelContact` | `str` |  | Yes |
| `SGBReg` | `str` |  | Yes |
| `Relation` | `str` |  | Yes |

### `Parent_Info`

- Estimated rows: `1912`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ParentID` | `INTEGER` | 10 | No |
| `Initials` | `WVARCHAR` | 10 | Yes |
| `FName` | `WVARCHAR` | 70 | Yes |
| `SName` | `WVARCHAR` | 70 | Yes |
| `Title` | `WVARCHAR` | 20 | Yes |
| `Employer` | `WVARCHAR` | 100 | Yes |
| `Occupation` | `WVARCHAR` | 60 | Yes |
| `StreetAddress1` | `WVARCHAR` | 70 | Yes |
| `StreetAddress2` | `WVARCHAR` | 70 | Yes |
| `StreetAddress3` | `WVARCHAR` | 50 | Yes |
| `StreetCode` | `WVARCHAR` | 10 | Yes |
| `PostalAddress1` | `WVARCHAR` | 70 | Yes |
| `PostalAddress2` | `WVARCHAR` | 70 | Yes |
| `PostalAddress3` | `WVARCHAR` | 50 | Yes |
| `PostalCode` | `WVARCHAR` | 10 | Yes |
| `Tel1Code` | `WVARCHAR` | 10 | Yes |
| `Tel1` | `WVARCHAR` | 25 | Yes |
| `Tel2Code` | `WVARCHAR` | 10 | Yes |
| `Tel2` | `WVARCHAR` | 25 | Yes |
| `Tel3Code` | `WVARCHAR` | 10 | Yes |
| `Tel3` | `WVARCHAR` | 25 | Yes |
| `EMail` | `WVARCHAR` | 70 | Yes |
| `GovBody` | `WVARCHAR` | 10 | Yes |
| `ParentsAss` | `WVARCHAR` | 10 | Yes |
| `Poverty` | `WVARCHAR` | 50 | Yes |
| `ID` | `WVARCHAR` | 50 | Yes |
| `Relship` | `WVARCHAR` | 50 | Yes |
| `IDNumber` | `WVARCHAR` | 20 | Yes |
| `AccPayer` | `WVARCHAR` | 10 | Yes |
| `Custodial` | `WVARCHAR` | 10 | Yes |
| `Gender` | `WVARCHAR` | 20 | Yes |
| `Race` | `WVARCHAR` | 50 | Yes |
| `Homelanguage` | `WVARCHAR` | 50 | Yes |
| `CorrTitle` | `WVARCHAR` | 20 | Yes |
| `CorrSurname` | `WVARCHAR` | 150 | Yes |
| `Spouse` | `WVARCHAR` | 50 | Yes |
| `FaxCode` | `WVARCHAR` | 10 | Yes |
| `FaxNo` | `WVARCHAR` | 50 | Yes |
| `SpouseOccupation` | `WVARCHAR` | 100 | Yes |
| `SpouseWorkTel` | `WVARCHAR` | 30 | Yes |
| `Status` | `str` |  | Yes |
| `SpouseGender` | `str` |  | Yes |
| `SpouseFname` | `str` |  | Yes |
| `SpouseID` | `str` |  | Yes |
| `SpouseCell` | `str` |  | Yes |
| `maritalstatus` | `str` |  | Yes |
| `SpouseEmail` | `str` |  | Yes |
| `DateLeft` | `str` |  | Yes |
| `Reason` | `str` |  | Yes |
| `Archive_Date` | `datetime.datetime` |  | Yes |
| `Archive_Reason` | `str` |  | Yes |
| `BirthDate` | `str` |  | Yes |
| `ReasonNoID` | `str` |  | Yes |
| `Religion` | `str` |  | Yes |
| `SACitizen` | `bool` |  | Yes |
| `Notes` | `str` |  | Yes |

### `PasswordHistory`

- Estimated rows: `227`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `UserPassword` | `WVARCHAR` | 30 | Yes |

### `Paste Errors`

- Estimated rows: `72`
- Heuristic primary key: `F1`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `F1` | `DOUBLE` | 53 | Yes |
| `F2` | `DOUBLE` | 53 | Yes |
| `F3` | `TIMESTAMP` | 19 | Yes |
| `F4` | `TIMESTAMP` | 19 | Yes |
| `F5` | `WVARCHAR` | 255 | Yes |
| `F6` | `WVARCHAR` | 255 | Yes |
| `F7` | `WVARCHAR` | 255 | Yes |
| `F8` | `WVARCHAR` | 255 | Yes |
| `F9` | `WVARCHAR` | 255 | Yes |
| `F10` | `WVARCHAR` | 255 | Yes |
| `F11` | `WVARCHAR` | 255 | Yes |
| `F12` | `WVARCHAR` | 255 | Yes |
| `F13` | `WVARCHAR` | 255 | Yes |
| `F14` | `DOUBLE` | 53 | Yes |
| `F15` | `WVARCHAR` | 255 | Yes |
| `F16` | `WVARCHAR` | 255 | Yes |
| `F17` | `DOUBLE` | 53 | Yes |
| `F18` | `WVARCHAR` | 255 | Yes |
| `F19` | `DOUBLE` | 53 | Yes |
| `F20` | `DOUBLE` | 53 | Yes |
| `F21` | `DOUBLE` | 53 | Yes |
| `F22` | `WVARCHAR` | 255 | Yes |

### `PastelCompanyPath`

- Estimated rows: `0`
- Heuristic primary key: `CompanyCode`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CompanyCode` | `INTEGER` | 10 | No |
| `CompanyName` | `WVARCHAR` | 100 | Yes |
| `CompanyPath` | `WLONGVARCHAR` | 1073741823 | Yes |

### `PastelCustomerCategory`

- Estimated rows: `99`
- Heuristic primary key: `Code`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Code` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 100 | Yes |

### `PettyCashAccounts`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `COANo` | `int` |  | Yes |
| `Name` | `str` |  | Yes |
| `Person` | `str` |  | Yes |
| `Float` | `decimal.Decimal` |  | Yes |
| `OpenAmount` | `decimal.Decimal` |  | Yes |

### `PettyPay`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Amount` | `NUMERIC` | 19 | Yes |
| `Date` | `datetime.datetime` |  | Yes |
| `VNum` | `int` |  | Yes |
| `CoaNum` | `int` |  | Yes |
| `Id` | `int` |  | Yes |
| `Description` | `str` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNo` | `int` |  | Yes |

### `PettyVoucherNumbers`

- Estimated rows: `0`
- Heuristic primary key: `BookId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `BookId` | `INTEGER` | 10 | No |
| `COANum` | `INTEGER` | 10 | Yes |
| `startVoucher` | `INTEGER` | 10 | Yes |
| `endVoucher` | `INTEGER` | 10 | Yes |
| `Lastvoucher` | `INTEGER` | 10 | Yes |

### `PhysicalInfrastructure`

- Estimated rows: `4`
- Heuristic primary key: `Electricity`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Electricity` | `INTEGER` | 10 | Yes |
| `Water` | `INTEGER` | 10 | Yes |
| `WaterQuality` | `WVARCHAR` | 50 | Yes |
| `WaterDistance` | `INTEGER` | 10 | Yes |
| `Toilets` | `INTEGER` | 10 | Yes |
| `FlushSystem` | `INTEGER` | 10 | Yes |
| `VentilatedPit` | `INTEGER` | 10 | Yes |
| `SepticTank` | `INTEGER` | 10 | Yes |
| `PitLatrine` | `INTEGER` | 10 | Yes |
| `Bucket` | `INTEGER` | 10 | Yes |
| `MaleLearners` | `INTEGER` | 10 | Yes |
| `MaleStaff` | `INTEGER` | 10 | Yes |
| `MaleDisabled` | `INTEGER` | 10 | Yes |
| `FemaleLearners` | `INTEGER` | 10 | Yes |
| `FemaleStaff` | `INTEGER` | 10 | Yes |
| `FemaleDisabled` | `INTEGER` | 10 | Yes |
| `LearnersNotFunctioning` | `INTEGER` | 10 | Yes |
| `StaffNotFunctioning` | `INTEGER` | 10 | Yes |
| `DisabledNotFunctioning` | `INTEGER` | 10 | Yes |
| `LearnerUrinals` | `INTEGER` | 10 | Yes |
| `StaffUrinals` | `INTEGER` | 10 | Yes |
| `DisabledUrinals` | `INTEGER` | 10 | Yes |
| `LearnerUrinalNotFunctioning` | `INTEGER` | 10 | Yes |
| `StaffUrinalNotFunctioning` | `INTEGER` | 10 | Yes |
| `DisabledUrinalNotFunctioning` | `INTEGER` | 10 | Yes |
| `FenceHeight` | `DOUBLE` | 53 | Yes |
| `MeshWire` | `WVARCHAR` | 10 | Yes |
| `BrickFence` | `WVARCHAR` | 10 | Yes |
| `BarbedWire` | `WVARCHAR` | 10 | Yes |
| `Woodfence` | `WVARCHAR` | 10 | Yes |
| `ConcreteFence` | `WVARCHAR` | 10 | Yes |
| `FenceCondition` | `INTEGER` | 10 | Yes |
| `RoadAccess` | `INTEGER` | 10 | Yes |
| `RoadCondition` | `INTEGER` | 10 | Yes |
| `TarDistance` | `INTEGER` | 10 | Yes |
| `BoardingFacilities` | `INTEGER` | 10 | Yes |
| `EducatorAccommodation` | `INTEGER` | 10 | Yes |
| `MaxMaleAccom` | `INTEGER` | 10 | Yes |
| `MaxFemaleAccom` | `INTEGER` | 10 | Yes |
| `ActualMaleAccom` | `INTEGER` | 10 | Yes |
| `ActualFemaleAccom` | `INTEGER` | 10 | Yes |
| `PayM` | `INTEGER` | 10 | Yes |
| `PayF` | `INTEGER` | 10 | Yes |
| `Walltype` | `WVARCHAR` | 50 | Yes |
| `RoofType` | `WVARCHAR` | 50 | Yes |
| `Ceiling` | `WVARCHAR` | 50 | Yes |
| `InternalWallFinish` | `WVARCHAR` | 50 | Yes |
| `FloorFinish` | `WVARCHAR` | 50 | Yes |
| `Photocopier` | `WVARCHAR` | 10 | Yes |
| `Fax` | `WVARCHAR` | 10 | Yes |
| `CopierMachine` | `WVARCHAR` | 10 | Yes |
| `RisoMachine` | `WVARCHAR` | 10 | Yes |
| `GeneralCondition` | `WVARCHAR` | 100 | Yes |
| `year` | `WVARCHAR` | 10 | Yes |
| `entrydate` | `TIMESTAMP` | 19 | Yes |

### `PhysicalRooms`

- Estimated rows: `5`
- Heuristic primary key: `PrincipalOffice`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PrincipalOffice` | `INTEGER` | 10 | Yes |
| `OtherOffice` | `INTEGER` | 10 | Yes |
| `SchoolHall` | `INTEGER` | 10 | Yes |
| `Staffroom` | `INTEGER` | 10 | Yes |
| `Safe` | `INTEGER` | 10 | Yes |
| `SickRoom` | `INTEGER` | 10 | Yes |
| `DuplicatingRoom` | `INTEGER` | 10 | Yes |
| `Storeroom` | `INTEGER` | 10 | Yes |
| `Quad` | `INTEGER` | 10 | Yes |
| `StrongRoom` | `INTEGER` | 10 | Yes |
| `OtherNumber` | `INTEGER` | 10 | Yes |
| `OtherType` | `WVARCHAR` | 100 | Yes |
| `ClassPerm` | `int` |  | Yes |
| `ClassPrefab` | `int` |  | Yes |
| `ClassUnderCon` | `int` |  | Yes |
| `ClassOffSite` | `int` |  | Yes |
| `MultigradePerm` | `int` |  | Yes |
| `MultigradePrefab` | `int` |  | Yes |
| `MultigradeUnderCon` | `int` |  | Yes |
| `MultigradeOffsite` | `int` |  | Yes |
| `LabPerm` | `int` |  | Yes |
| `LabPrefab` | `int` |  | Yes |
| `LabUndercon` | `int` |  | Yes |
| `LabOffsite` | `int` |  | Yes |
| `SpecialPerm` | `int` |  | Yes |
| `SpecialPrefab` | `int` |  | Yes |
| `SpecialUndercon` | `int` |  | Yes |
| `SpecialOffSite` | `int` |  | Yes |
| `WorkshopPerm` | `int` |  | Yes |
| `WorkshopPrefab` | `int` |  | Yes |
| `WorkshopUnderCon` | `int` |  | Yes |
| `WorkshopOffSite` | `int` |  | Yes |
| `MultiPurPerm` | `int` |  | Yes |
| `MultiPurPrefab` | `int` |  | Yes |
| `MultiPurUnderCon` | `int` |  | Yes |
| `MultiPurOffSite` | `int` |  | Yes |
| `CompPerm` | `int` |  | Yes |
| `CompPrefab` | `int` |  | Yes |
| `CompUnderCon` | `int` |  | Yes |
| `CompOffSite` | `int` |  | Yes |
| `MediaPerm` | `int` |  | Yes |
| `MediaPrefab` | `int` |  | Yes |
| `MediaUnderCon` | `int` |  | Yes |
| `MediaOffSite` | `int` |  | Yes |
| `MediaCentre` | `str` |  | Yes |
| `MediaType` | `str` |  | Yes |
| `BuildingOwner` | `str` |  | Yes |
| `LandOwner` | `int` |  | Yes |
| `OwnerOther` | `str` |  | Yes |
| `OwnerSName` | `str` |  | Yes |
| `OwnerTitle` | `str` |  | Yes |
| `OwnerInitials` | `str` |  | Yes |
| `Farm` | `str` |  | Yes |
| `PostalAddress` | `str` |  | Yes |
| `PhysicalAddress` | `str` |  | Yes |
| `Telcode` | `str` |  | Yes |
| `Tel` | `str` |  | Yes |
| `Faxcode` | `str` |  | Yes |
| `Fax` | `str` |  | Yes |
| `Stateowned` | `int` |  | Yes |
| `SecuritySystem` | `str` |  | Yes |
| `Alarm` | `str` |  | Yes |
| `Guard` | `str` |  | Yes |
| `ArmedResponse` | `str` |  | Yes |
| `Year` | `str` |  | Yes |
| `Entrydate` | `datetime.datetime` |  | Yes |
| `Transport` | `int` |  | Yes |
| `TransportLearners` | `int` |  | Yes |
| `Typetransport` | `int` |  | Yes |
| `TransportOther` | `str` |  | Yes |
| `ClassroomCon` | `int` |  | Yes |
| `StaffroomCon` | `int` |  | Yes |
| `OfficesCon` | `int` |  | Yes |
| `LaboratoryCon` | `int` |  | Yes |
| `LibraryCon` | `int` |  | Yes |
| `ToiletsCon` | `int` |  | Yes |
| `StoreroomCon` | `int` |  | Yes |
| `Sportfields` | `int` |  | Yes |

### `PromotionDescriptions`

- Estimated rows: `10`
- Heuristic primary key: `PromotionId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PromotionId` | `INTEGER` | 10 | No |
| `Description` | `str` |  | Yes |
| `AfrDescription` | `str` |  | Yes |
| `ReportCode` | `str` |  | Yes |
| `DescriptionTerm1to3` | `str` |  | Yes |
| `AfrDescriptionTerm1to3` | `str` |  | Yes |
| `DeviatedDesc` | `str` |  | Yes |
| `DeviatedAfrDesc` | `str` |  | Yes |

### `Promotions`

- Estimated rows: `384`
- Heuristic primary key: `YearPromoted`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `YearPromoted` | `WVARCHAR` | 50 | Yes |
| `Processed` | `BIT` | 1 | No |
| `Grade` | `INTEGER` | 10 | Yes |
| `Passed` | `INTEGER` | 10 | Yes |
| `Repeats` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 50 | Yes |
| `NotPromoted` | `INTEGER` | 10 | Yes |

### `PromotionsExport`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Gender` | `str` |  | Yes |
| `Category` | `int` |  | Yes |
| `Quantity` | `int` |  | Yes |

### `Qualifications`

- Estimated rows: `40`
- Heuristic primary key: `LinkID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LinkType` | `TINYINT` | 3 | Yes |
| `LinkID` | `INTEGER` | 10 | Yes |
| `QualType` | `TINYINT` | 3 | Yes |
| `QualNo` | `INTEGER` | 10 | Yes |
| `QualYear` | `WVARCHAR` | 4 | Yes |
| `QualInstitution` | `WVARCHAR` | 100 | Yes |
| `QualSubjects` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QualOtherSubjects` | `WVARCHAR` | 250 | Yes |
| `HighestLevel1` | `DOUBLE` | 53 | Yes |
| `HighestLevel` | `DOUBLE` | 53 | Yes |
| `QualInstitution1` | `WLONGVARCHAR` | 1073741823 | Yes |
| `QualSubjects1` | `WLONGVARCHAR` | 1073741823 | Yes |

### `QualificationsTypes`

- Estimated rows: `44`
- Heuristic primary key: `QualType`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `QualType` | `TINYINT` | 3 | Yes |
| `QualNo` | `INTEGER` | 10 | Yes |
| `QualDesc` | `WVARCHAR` | 255 | Yes |

### `ReasonCodes`

- Estimated rows: `17`
- Heuristic primary key: `ReasonCode`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ReasonCode` | `INTEGER` | 10 | Yes |
| `ReasonDescription` | `WVARCHAR` | 200 | Yes |

### `Receipt_Info`

- Estimated rows: `11493`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `InputDate` | `datetime.datetime` |  | Yes |
| `FromP` | `str` |  | Yes |
| `Amount` | `decimal.Decimal` |  | Yes |
| `Method` | `str` |  | Yes |
| `RNum` | `int` |  | Yes |
| `DepFlag` | `str` |  | Yes |
| `DepNo` | `int` |  | Yes |
| `Book` | `int` |  | Yes |
| `Year` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `EntryDate` | `datetime.datetime` |  | Yes |
| `TransNo` | `int` |  | Yes |

### `ReceiptBooks`

- Estimated rows: `116`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Book` | `WVARCHAR` | 200 | Yes |
| `StartNo` | `INTEGER` | 10 | Yes |
| `CurNo` | `INTEGER` | 10 | Yes |
| `EndNo` | `INTEGER` | 10 | Yes |

### `RegisterEducators`

- Estimated rows: `0`
- Heuristic primary key: `EducatorCode`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EducatorCode` | `WVARCHAR` | 50 | Yes |
| `Class` | `WVARCHAR` | 30 | Yes |
| `Room` | `WVARCHAR` | 50 | Yes |

### `Religion`

- Estimated rows: `52`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Description` | `WLONGVARCHAR` | 1073741823 | Yes |

### `ReportComments`

- Estimated rows: `7`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `CommentKey` | `INTEGER` | 10 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `AfrComment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `ReportCommentsSkills`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `LearnerId` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |

### `ReportCommentsVA`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `LearnerId` | `INTEGER` | 10 | Yes |
| `ReportId` | `INTEGER` | 10 | Yes |
| `SubjectId` | `INTEGER` | 10 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |

### `ReportCycles`

- Estimated rows: `418`
- Heuristic primary key: `CycleId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `CycleId` | `INTEGER` | 10 | No |
| `Name` | `str` |  | Yes |
| `CycleNo` | `int` |  | Yes |
| `Phase` | `str` |  | Yes |
| `Datayear` | `str` |  | Yes |
| `Term` | `int` |  | Yes |
| `FinalPromotion` | `bool` |  | Yes |
| `Afrname` | `str` |  | Yes |
| `EndDate` | `datetime.datetime` |  | Yes |
| `StartDate` | `datetime.datetime` |  | Yes |
| `ReportMessage` | `str` |  | Yes |
| `AfrReportMessage` | `str` |  | Yes |

### `ReportGeneralComments`

- Estimated rows: `54`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `SortNo` | `INTEGER` | 10 | Yes |
| `Comment` | `WVARCHAR` | 250 | Yes |
| `AfrComment` | `WVARCHAR` | 250 | Yes |

### `ReportLanguages`

- Estimated rows: `13`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Name` | `WVARCHAR` | 50 | Yes |

### `ReportMarks`

- Estimated rows: `162646`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `LearnerID` | `int` |  | Yes |
| `SubjectId` | `int` |  | Yes |
| `OBEKey` | `int` |  | Yes |
| `Symbol` | `str` |  | Yes |
| `Mark` | `int` |  | Yes |
| `ReportId` | `int` |  | Yes |
| `Datayear` | `str` |  | Yes |
| `Level` | `str` |  | Yes |
| `Comment1` | `str` |  | Yes |
| `CASS` | `float` |  | Yes |
| `Comment2` | `str` |  | Yes |
| `ExamMark` | `float` |  | Yes |
| `TotalMark` | `int` |  | Yes |
| `CASSTerm` | `int` |  | Yes |
| `Mark400` | `int` |  | Yes |
| `TSTransactionCategory` | `int` |  | Yes |
| `TSStatusFlag` | `int` |  | Yes |
| `TSReportStatusFlag` | `int` |  | Yes |
| `TSReasonCode` | `int` |  | Yes |
| `ExcludeAve` | `bool` |  | Yes |

### `ReportMarksSplits`

- Estimated rows: `113966`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Term` | `TINYINT` | 3 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `SubjSplitNo` | `INTEGER` | 10 | Yes |
| `CriterionID` | `INTEGER` | 10 | Yes |
| `Mark` | `DOUBLE` | 53 | Yes |
| `OBEKey` | `INTEGER` | 10 | Yes |
| `EvalVer` | `INTEGER` | 10 | Yes |
| `RecId` | `INTEGER` | 10 | No |

### `ReportOutcomeMarks`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `LearnerID` | `INTEGER` | 10 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `ReportID` | `INTEGER` | 10 | Yes |
| `OutcomeID` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 20 | Yes |
| `Term1RatingCode` | `WVARCHAR` | 5 | Yes |
| `Term1Comment` | `WVARCHAR` | 200 | Yes |
| `term1Mark` | `DOUBLE` | 53 | Yes |
| `Term2RatingCode` | `WVARCHAR` | 5 | Yes |
| `Term2Comment` | `WVARCHAR` | 200 | Yes |
| `Term2Mark` | `DOUBLE` | 53 | Yes |
| `Term3RatingCode` | `WVARCHAR` | 5 | Yes |
| `Term3Comment` | `WVARCHAR` | 200 | Yes |
| `Term3Mark` | `DOUBLE` | 53 | Yes |
| `Term4RatingCode` | `WVARCHAR` | 5 | Yes |
| `Term4Comment` | `WVARCHAR` | 200 | Yes |
| `Term4Mark` | `DOUBLE` | 53 | Yes |

### `ReportsMortalityCategories`

- Estimated rows: `4`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Name` | `WVARCHAR` | 50 | Yes |

### `Requisitions`

- Estimated rows: `0`
- Heuristic primary key: `ReqId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ReqId` | `INTEGER` | 10 | No |
| `ReqNo` | `WVARCHAR` | 50 | Yes |
| `ReqDate` | `TIMESTAMP` | 19 | Yes |
| `ItemDescription` | `WVARCHAR` | 255 | Yes |
| `Amount` | `DOUBLE` | 53 | Yes |
| `NoItems` | `INTEGER` | 10 | Yes |
| `AccountID` | `INTEGER` | 10 | Yes |
| `Status` | `WVARCHAR` | 80 | Yes |

### `SchoolAdministration`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field61` | `INTEGER` | 10 | Yes |
| `Field62` | `INTEGER` | 10 | Yes |
| `Field631` | `INTEGER` | 10 | Yes |
| `Field632` | `int` |  | Yes |
| `Field633` | `int` |  | Yes |
| `Field634` | `int` |  | Yes |
| `Field635` | `int` |  | Yes |
| `Field64` | `int` |  | Yes |
| `Field65` | `int` |  | Yes |
| `Field66` | `int` |  | Yes |
| `Field67` | `int` |  | Yes |
| `Field68` | `int` |  | Yes |
| `Field69` | `int` |  | Yes |
| `Field610` | `int` |  | Yes |
| `Field611` | `int` |  | Yes |
| `Field612` | `int` |  | Yes |
| `Field6131` | `int` |  | Yes |
| `Field6132` | `int` |  | Yes |
| `Field6133` | `int` |  | Yes |
| `Field6134` | `int` |  | Yes |
| `Field6135` | `int` |  | Yes |
| `Field6136` | `int` |  | Yes |
| `Field6137` | `int` |  | Yes |
| `Field6138` | `int` |  | Yes |
| `Field6139` | `int` |  | Yes |

### `SchoolBoarding`

- Estimated rows: `0`
- Heuristic primary key: `Datayear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Gender` | `str` |  | Yes |
| `Premises` | `str` |  | Yes |
| `Category` | `str` |  | Yes |
| `Quantity` | `int` |  | Yes |

### `SchoolCommunityParents`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field101` | `int` |  | Yes |
| `Field102` | `int` |  | Yes |
| `Field103` | `int` |  | Yes |
| `Field104` | `int` |  | Yes |
| `Field105` | `int` |  | Yes |
| `Field1061` | `int` |  | Yes |
| `Field1062` | `int` |  | Yes |
| `Field1063` | `int` |  | Yes |
| `Field1064` | `int` |  | Yes |
| `Field1065` | `int` |  | Yes |
| `Field1066` | `int` |  | Yes |
| `Field1067` | `int` |  | Yes |
| `Field1068` | `int` |  | Yes |
| `Field1071` | `int` |  | Yes |
| `Field1072` | `int` |  | Yes |
| `Field1073` | `int` |  | Yes |
| `Field1074` | `int` |  | Yes |
| `Field1075` | `int` |  | Yes |
| `Field1076` | `int` |  | Yes |
| `Field1077` | `int` |  | Yes |

### `SchoolCurriculum`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field71` | `INTEGER` | 10 | Yes |
| `Field72` | `INTEGER` | 10 | Yes |
| `Field731` | `INTEGER` | 10 | Yes |
| `Field732` | `int` |  | Yes |
| `Field733` | `int` |  | Yes |
| `Field734` | `int` |  | Yes |
| `Field741` | `int` |  | Yes |
| `Field742` | `int` |  | Yes |
| `Field743` | `int` |  | Yes |
| `Field744` | `int` |  | Yes |
| `Field745` | `int` |  | Yes |
| `Field75` | `int` |  | Yes |
| `Field76` | `int` |  | Yes |
| `Field77` | `int` |  | Yes |
| `Field78` | `int` |  | Yes |
| `Field79` | `int` |  | Yes |
| `Field710` | `int` |  | Yes |
| `Field711` | `int` |  | Yes |
| `Field712` | `int` |  | Yes |
| `Field713` | `int` |  | Yes |
| `Field714` | `int` |  | Yes |

### `SchoolFees`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field1711` | `INTEGER` | 10 | Yes |
| `Field1712` | `int` |  | Yes |
| `Field1713` | `int` |  | Yes |
| `Field1714` | `int` |  | Yes |
| `Field1715` | `int` |  | Yes |
| `Field1721` | `int` |  | Yes |
| `Field1722` | `int` |  | Yes |
| `Field1723` | `int` |  | Yes |
| `Field1724` | `int` |  | Yes |
| `Field1731` | `int` |  | Yes |
| `Field1732` | `int` |  | Yes |
| `Field1733` | `int` |  | Yes |
| `Field1734` | `int` |  | Yes |
| `Field1735` | `int` |  | Yes |
| `Field1736` | `int` |  | Yes |
| `Field1737` | `int` |  | Yes |
| `Field1741` | `int` |  | Yes |
| `Field1742` | `int` |  | Yes |
| `Field1743` | `int` |  | Yes |
| `Field1744` | `int` |  | Yes |
| `Field1745` | `int` |  | Yes |
| `Field1746` | `int` |  | Yes |
| `Field1747` | `int` |  | Yes |

### `SchoolFinance`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field131` | `INTEGER` | 10 | Yes |
| `Field132` | `INTEGER` | 10 | Yes |
| `Field1331` | `int` |  | Yes |
| `Field1332` | `int` |  | Yes |
| `Field134` | `int` |  | Yes |
| `Field1351` | `int` |  | Yes |
| `Field1352` | `float` |  | Yes |
| `Field1353` | `float` |  | Yes |
| `Field1354` | `float` |  | Yes |
| `Field1355` | `float` |  | Yes |
| `Field1356` | `float` |  | Yes |
| `Field1357` | `float` |  | Yes |
| `Field1361` | `float` |  | Yes |
| `Field1362` | `float` |  | Yes |
| `Field1363` | `float` |  | Yes |
| `Field1364` | `float` |  | Yes |
| `Field1365` | `float` |  | Yes |
| `Field1366` | `float` |  | Yes |
| `Field1367` | `float` |  | Yes |
| `Field1368` | `float` |  | Yes |
| `Field1371` | `int` |  | Yes |
| `Field1372` | `int` |  | Yes |
| `Field1373` | `int` |  | Yes |
| `Field1374` | `int` |  | Yes |
| `Field138` | `int` |  | Yes |
| `Field139` | `int` |  | Yes |
| `Field1310` | `int` |  | Yes |

### `SchoolGovBodies`

- Estimated rows: `0`
- Heuristic primary key: `SGBID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SGBID` | `INTEGER` | 10 | No |
| `DateElected` | `TIMESTAMP` | 19 | Yes |
| `DateEnded` | `TIMESTAMP` | 19 | Yes |

### `SchoolGrades`

- Estimated rows: `31`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Name` | `str` |  | Yes |
| `SchoolGrade` | `str` |  | Yes |
| `ShortGradeName` | `str` |  | Yes |
| `Date_Deactivated` | `datetime.datetime` |  | Yes |
| `Deactivated` | `str` |  | Yes |
| `Active_Classes` | `str` |  | Yes |
| `Date_Active` | `str` |  | Yes |

### `SchoolInfo`

- Estimated rows: `0`
- Heuristic primary key: `SchoolName`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SchoolName` | `WVARCHAR` | 255 | Yes |
| `District` | `WVARCHAR` | 255 | Yes |
| `Circuit` | `WVARCHAR` | 255 | Yes |
| `EmisCode` | `WVARCHAR` | 255 | Yes |
| `TelNo` | `WVARCHAR` | 255 | Yes |
| `PrincipalName` | `WVARCHAR` | 255 | Yes |
| `Assessor` | `WVARCHAR` | 255 | Yes |

### `SchoolManagement`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field511` | `INTEGER` | 10 | Yes |
| `Field512` | `int` |  | Yes |
| `Field513` | `int` |  | Yes |
| `Field514` | `int` |  | Yes |
| `Field515` | `int` |  | Yes |
| `Field516` | `int` |  | Yes |
| `Field517` | `int` |  | Yes |
| `Field518` | `int` |  | Yes |
| `Field521` | `int` |  | Yes |
| `Field522` | `int` |  | Yes |
| `Field523` | `int` |  | Yes |
| `Field53` | `int` |  | Yes |
| `Field54` | `int` |  | Yes |
| `Field55` | `int` |  | Yes |
| `Field56` | `int` |  | Yes |
| `Field57` | `int` |  | Yes |
| `Field591` | `int` |  | Yes |
| `Field592` | `int` |  | Yes |
| `Field593` | `int` |  | Yes |
| `Field594` | `int` |  | Yes |
| `Field595` | `int` |  | Yes |
| `Field596` | `int` |  | Yes |
| `Field597` | `int` |  | Yes |
| `Field598` | `int` |  | Yes |
| `Field599` | `int` |  | Yes |
| `Field5910` | `int` |  | Yes |
| `Field5911` | `int` |  | Yes |
| `Field5912` | `int` |  | Yes |
| `Field5913` | `int` |  | Yes |
| `Field5914` | `int` |  | Yes |
| `Field5915` | `int` |  | Yes |
| `Field5916` | `int` |  | Yes |
| `Field5917` | `int` |  | Yes |
| `Field5101` | `int` |  | Yes |
| `Field5102` | `int` |  | Yes |
| `Field5103` | `int` |  | Yes |
| `Field5104` | `int` |  | Yes |
| `Field5105` | `int` |  | Yes |

### `SchoolProvincialSupport`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Field141` | `INTEGER` | 10 | Yes |
| `Field1421` | `INTEGER` | 10 | Yes |
| `Field1422` | `int` |  | Yes |
| `Field1423` | `int` |  | Yes |
| `Field1424` | `int` |  | Yes |
| `Field1425` | `int` |  | Yes |
| `Field1426` | `int` |  | Yes |
| `Field1427` | `int` |  | Yes |
| `Field1428` | `int` |  | Yes |
| `Field1429` | `int` |  | Yes |
| `Field14210` | `int` |  | Yes |
| `Field14211` | `int` |  | Yes |
| `Field14212` | `int` |  | Yes |
| `Field14213` | `int` |  | Yes |
| `Field14214` | `int` |  | Yes |
| `Field14215` | `int` |  | Yes |
| `Field14216` | `int` |  | Yes |
| `Field14217` | `int` |  | Yes |
| `Field14218` | `int` |  | Yes |
| `Field14219` | `int` |  | Yes |
| `Field14220` | `int` |  | Yes |
| `Field1431` | `int` |  | Yes |
| `Field1432` | `int` |  | Yes |
| `Field1433` | `int` |  | Yes |
| `Field1434` | `int` |  | Yes |
| `Field1435` | `int` |  | Yes |
| `Field1436` | `int` |  | Yes |
| `Field1437` | `int` |  | Yes |
| `Field1438` | `int` |  | Yes |
| `Field1439` | `int` |  | Yes |
| `Field14310` | `int` |  | Yes |
| `Field14311` | `int` |  | Yes |
| `Field14312` | `int` |  | Yes |
| `Field14313` | `int` |  | Yes |
| `Field14314` | `int` |  | Yes |
| `Field14315` | `int` |  | Yes |
| `Field14316` | `int` |  | Yes |
| `Field14317` | `int` |  | Yes |
| `Field14318` | `int` |  | Yes |

### `SchoolResources`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field1211` | `INTEGER` | 10 | Yes |
| `Field1212` | `int` |  | Yes |
| `Field1213` | `int` |  | Yes |
| `Field1214` | `int` |  | Yes |
| `Field1215` | `int` |  | Yes |
| `Field1216` | `int` |  | Yes |
| `Field1217` | `int` |  | Yes |
| `Field1218` | `int` |  | Yes |
| `Field1219` | `int` |  | Yes |
| `Field12110` | `int` |  | Yes |
| `Field12111` | `int` |  | Yes |
| `Field12112` | `int` |  | Yes |
| `Field12113` | `int` |  | Yes |
| `Field12114` | `int` |  | Yes |
| `Field12115` | `int` |  | Yes |
| `Field1221` | `int` |  | Yes |
| `Field1222` | `int` |  | Yes |
| `Field1223` | `int` |  | Yes |
| `Field1224` | `int` |  | Yes |
| `Field1225` | `int` |  | Yes |
| `Field123` | `int` |  | Yes |
| `Field124` | `int` |  | Yes |
| `Field125` | `int` |  | Yes |
| `Field1261` | `int` |  | Yes |
| `Field1262` | `int` |  | Yes |
| `Field1263` | `int` |  | Yes |
| `Field1264` | `int` |  | Yes |
| `Field1265` | `int` |  | Yes |
| `Other` | `str` |  | Yes |
| `Field127` | `int` |  | Yes |
| `Field128` | `int` |  | Yes |
| `Field1291` | `int` |  | Yes |
| `Field1292` | `int` |  | Yes |
| `Field1293` | `int` |  | Yes |
| `Field1294` | `int` |  | Yes |
| `Field1295` | `int` |  | Yes |
| `OtherAdmin` | `str` |  | Yes |
| `Field12101` | `int` |  | Yes |
| `Field12102` | `int` |  | Yes |
| `Field12103` | `int` |  | Yes |
| `Field12104` | `int` |  | Yes |
| `Field121100` | `int` |  | Yes |
| `Field121200` | `int` |  | Yes |

### `SchoolSafety`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Field111` | `INTEGER` | 10 | Yes |
| `Field112` | `INTEGER` | 10 | Yes |
| `Field113` | `INTEGER` | 10 | Yes |
| `Field114` | `INTEGER` | 10 | Yes |
| `Field1151` | `INTEGER` | 10 | Yes |
| `Field1152` | `INTEGER` | 10 | Yes |
| `Field1153` | `INTEGER` | 10 | Yes |
| `Field1154` | `INTEGER` | 10 | Yes |
| `Field1155` | `INTEGER` | 10 | Yes |
| `Field1156` | `INTEGER` | 10 | Yes |
| `Field116` | `INTEGER` | 10 | Yes |
| `Field1171` | `INTEGER` | 10 | Yes |
| `Field1172` | `INTEGER` | 10 | Yes |
| `Field1173` | `INTEGER` | 10 | Yes |
| `Field1174` | `INTEGER` | 10 | Yes |
| `Field1181` | `DOUBLE` | 53 | Yes |
| `Field1182` | `DOUBLE` | 53 | Yes |
| `Field119` | `INTEGER` | 10 | Yes |
| `Field11101` | `INTEGER` | 10 | Yes |
| `Field11102` | `INTEGER` | 10 | Yes |
| `Field11103` | `INTEGER` | 10 | Yes |
| `Field11104` | `INTEGER` | 10 | Yes |
| `Field11105` | `INTEGER` | 10 | Yes |
| `Field11106` | `INTEGER` | 10 | Yes |
| `Field11107` | `INTEGER` | 10 | Yes |
| `Field11108` | `INTEGER` | 10 | Yes |
| `Field11109` | `INTEGER` | 10 | Yes |
| `Field111010` | `INTEGER` | 10 | Yes |
| `Field111011` | `INTEGER` | 10 | Yes |
| `Field111012` | `INTEGER` | 10 | Yes |
| `Field111013` | `INTEGER` | 10 | Yes |
| `Field111014` | `INTEGER` | 10 | Yes |
| `Field111015` | `INTEGER` | 10 | Yes |
| `Field11111` | `INTEGER` | 10 | Yes |
| `Field11112` | `INTEGER` | 10 | Yes |
| `Field11113` | `INTEGER` | 10 | Yes |
| `Field11114` | `INTEGER` | 10 | Yes |
| `Field11115` | `INTEGER` | 10 | Yes |
| `Field11116` | `INTEGER` | 10 | Yes |
| `Field11117` | `INTEGER` | 10 | Yes |
| `Field11118` | `INTEGER` | 10 | Yes |
| `Field11119` | `INTEGER` | 10 | Yes |
| `Field111110` | `INTEGER` | 10 | Yes |

### `SchoolSubVenues`

- Estimated rows: `0`
- Heuristic primary key: `SubVenueId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SubVenueId` | `INTEGER` | 10 | No |
| `VenueId` | `INTEGER` | 10 | Yes |
| `Description` | `str` |  | Yes |
| `LastCounted` | `datetime.datetime` |  | Yes |
| `Type` | `int` |  | Yes |
| `Room` | `int` |  | Yes |

### `SchoolTerms`

- Estimated rows: `72`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Quater` | `str` |  | Yes |
| `StartDate` | `datetime.datetime` |  | Yes |
| `EndDate` | `datetime.datetime` |  | Yes |
| `CurrentYear` | `str` |  | Yes |
| `Term` | `int` |  | Yes |

### `SchoolUniform`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field181` | `INTEGER` | 10 | Yes |
| `Field182` | `INTEGER` | 10 | Yes |
| `Field1831` | `bool` |  | Yes |
| `Field1832` | `bool` |  | Yes |
| `Field1833` | `bool` |  | Yes |
| `Field1851M` | `decimal.Decimal` |  | Yes |
| `Field1851F` | `decimal.Decimal` |  | Yes |
| `Field1852M` | `decimal.Decimal` |  | Yes |
| `Field1852F` | `decimal.Decimal` |  | Yes |

### `SchoolUniformParts`

- Estimated rows: `0`
- Heuristic primary key: `DataYear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Question` | `str` |  | Yes |
| `Season` | `str` |  | Yes |
| `Gender` | `str` |  | Yes |

### `SchoolVenues`

- Estimated rows: `0`
- Heuristic primary key: `VenueId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `VenueId` | `INTEGER` | 10 | No |
| `Type` | `int` |  | Yes |
| `Description` | `str` |  | Yes |
| `Room` | `int` |  | Yes |
| `VenueRoom` | `str` |  | Yes |

### `SeriousIncidents`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `DataYear` | `WVARCHAR` | 50 | Yes |
| `IncDate` | `TIMESTAMP` | 19 | Yes |
| `IncType` | `TINYINT` | 3 | Yes |
| `CompType` | `TINYINT` | 3 | Yes |
| `CompGrade` | `TINYINT` | 3 | Yes |
| `CompLinkID` | `INTEGER` | 10 | Yes |
| `CompName` | `WVARCHAR` | 255 | Yes |
| `PerpType` | `TINYINT` | 3 | Yes |
| `PerpGrade` | `TINYINT` | 3 | Yes |
| `PerpLinkID` | `INTEGER` | 10 | Yes |
| `PerpName` | `WVARCHAR` | 255 | Yes |
| `RepToPDE` | `BIT` | 1 | No |
| `RepToSACE` | `BIT` | 1 | No |
| `RepToSAP` | `BIT` | 1 | No |
| `RepSAPStation` | `WVARCHAR` | 50 | Yes |
| `RepSAPCaseNo` | `WVARCHAR` | 50 | Yes |
| `StatusHearing` | `BIT` | 1 | No |
| `StatusSuspension` | `BIT` | 1 | No |
| `StatusWithdrawn` | `BIT` | 1 | No |
| `Comments` | `WLONGVARCHAR` | 1073741823 | Yes |
| `StatusCompleted` | `BIT` | 1 | No |

### `SeriousIncidentsTypes`

- Estimated rows: `32`
- Heuristic primary key: `IncType`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `IncType` | `INTEGER` | 10 | Yes |
| `IncTypeDesc` | `WVARCHAR` | 200 | Yes |

### `ServiceProvider`

- Estimated rows: `6`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Name` | `str` |  | Yes |

### `Settings`

- Estimated rows: `1`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `StatusI` | `WVARCHAR` | 5 | Yes |
| `Reports` | `WVARCHAR` | 10 | Yes |
| `StatusC` | `WVARCHAR` | 5 | Yes |
| `FontColour` | `DOUBLE` | 53 | Yes |
| `IPicture` | `LONGVARBINARY` | 1073741823 | Yes |
| `LearnerPhotographFolder` | `WLONGVARCHAR` | 1073741823 | Yes |
| `LearnerPhoto` | `WVARCHAR` | 200 | Yes |
| `EducatorPhotographFolder` | `WVARCHAR` | 200 | Yes |

### `SGBFunctionAverage`

- Estimated rows: `1`
- Heuristic primary key: `emisnumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `emisnumber` | `DOUBLE` | 53 | Yes |
| `dataYear` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Policy_ratings` | `INTEGER` | 10 | Yes |
| `Meeting_ratings` | `INTEGER` | 10 | Yes |
| `Assets_ratings` | `INTEGER` | 10 | Yes |
| `Finance_ratings` | `INTEGER` | 10 | Yes |
| `Curriculum_ratings` | `INTEGER` | 10 | Yes |

### `SGBFunctions`

- Estimated rows: `0`
- Heuristic primary key: `emisnumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `emisnumber` | `DOUBLE` | 53 | Yes |
| `dataYear` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field1` | `INTEGER` | 10 | Yes |
| `Field1Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field2` | `INTEGER` | 10 | Yes |
| `Field2Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field3` | `INTEGER` | 10 | Yes |
| `Field3Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field4` | `INTEGER` | 10 | Yes |
| `Field4Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field5` | `INTEGER` | 10 | Yes |
| `Field5Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field6` | `INTEGER` | 10 | Yes |
| `Field6Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field7` | `INTEGER` | 10 | Yes |
| `Field7Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field8` | `INTEGER` | 10 | Yes |
| `Field8Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field9` | `INTEGER` | 10 | Yes |
| `Field9Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field10` | `INTEGER` | 10 | Yes |
| `Field10Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field11` | `INTEGER` | 10 | Yes |
| `Field11Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field12` | `INTEGER` | 10 | Yes |
| `Field12Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field13` | `INTEGER` | 10 | Yes |
| `Field13Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field14` | `INTEGER` | 10 | Yes |
| `Field14Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field15` | `INTEGER` | 10 | Yes |
| `Field15Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field16` | `INTEGER` | 10 | Yes |
| `Field16Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field17` | `INTEGER` | 10 | Yes |
| `Field17Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field18` | `INTEGER` | 10 | Yes |
| `Field18Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field19` | `INTEGER` | 10 | Yes |
| `Field19Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field20` | `INTEGER` | 10 | Yes |
| `Field20Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field21` | `INTEGER` | 10 | Yes |
| `Field21Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field22` | `INTEGER` | 10 | Yes |
| `Field22Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field23` | `INTEGER` | 10 | Yes |
| `Field23Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field24` | `INTEGER` | 10 | Yes |
| `Field24Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field25` | `INTEGER` | 10 | Yes |
| `Field25Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field26` | `INTEGER` | 10 | Yes |
| `Field26Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field27` | `INTEGER` | 10 | Yes |
| `Field27Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field28` | `INTEGER` | 10 | Yes |
| `Field28Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field29` | `INTEGER` | 10 | Yes |
| `Field29Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field30` | `INTEGER` | 10 | Yes |
| `Field30Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field31` | `INTEGER` | 10 | Yes |
| `Field31Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field32` | `INTEGER` | 10 | Yes |
| `Field32Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field33` | `INTEGER` | 10 | Yes |
| `Field33Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field34` | `INTEGER` | 10 | Yes |
| `Field34Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field35` | `INTEGER` | 10 | Yes |
| `Field35Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field36` | `INTEGER` | 10 | Yes |
| `Field36Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field37` | `INTEGER` | 10 | Yes |
| `Field37Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field38` | `INTEGER` | 10 | Yes |
| `Field38Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field39` | `INTEGER` | 10 | Yes |
| `Field39Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field40` | `INTEGER` | 10 | Yes |
| `Field40Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field41` | `INTEGER` | 10 | Yes |
| `Field41Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field42` | `INTEGER` | 10 | Yes |
| `Field42Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field43` | `INTEGER` | 10 | Yes |
| `Field43Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Field44` | `INTEGER` | 10 | Yes |
| `Field44Comment` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SGBPolicy`

- Estimated rows: `0`
- Heuristic primary key: `EmisNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `EmisNumber` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `Field411` | `INTEGER` | 10 | Yes |
| `Field412` | `INTEGER` | 10 | Yes |
| `Field413` | `INTEGER` | 10 | Yes |
| `Field414` | `INTEGER` | 10 | Yes |
| `Field421` | `INTEGER` | 10 | Yes |
| `Field422` | `int` |  | Yes |
| `Field423` | `int` |  | Yes |
| `Field424` | `int` |  | Yes |
| `Field425` | `int` |  | Yes |
| `Field426` | `int` |  | Yes |
| `Field427` | `int` |  | Yes |
| `Field428` | `int` |  | Yes |
| `Field431` | `int` |  | Yes |
| `Field432` | `int` |  | Yes |
| `Field433` | `int` |  | Yes |
| `Field434` | `int` |  | Yes |
| `Field435` | `int` |  | Yes |
| `Field436` | `int` |  | Yes |
| `Field44` | `int` |  | Yes |
| `Field45` | `int` |  | Yes |
| `Field46` | `int` |  | Yes |
| `Field47` | `int` |  | Yes |
| `Field48` | `int` |  | Yes |
| `Field49` | `int` |  | Yes |
| `Field4100` | `int` |  | Yes |
| `Field4110` | `int` |  | Yes |
| `Field4121` | `int` |  | Yes |
| `Field4122` | `int` |  | Yes |
| `Field4123` | `int` |  | Yes |
| `Field4124` | `int` |  | Yes |
| `Field4125` | `int` |  | Yes |
| `Field4131` | `int` |  | Yes |
| `Field4132` | `int` |  | Yes |
| `Field4141` | `int` |  | Yes |
| `Field4142` | `int` |  | Yes |
| `Field4143` | `int` |  | Yes |
| `Field4144` | `int` |  | Yes |
| `Field4145` | `int` |  | Yes |
| `Field4146` | `int` |  | Yes |
| `Field4151` | `int` |  | Yes |
| `Field4152` | `int` |  | Yes |
| `Field4153` | `int` |  | Yes |
| `Field4154` | `int` |  | Yes |
| `Field4155` | `int` |  | Yes |
| `Field416` | `int` |  | Yes |
| `Field417` | `int` |  | Yes |
| `Field418` | `int` |  | Yes |
| `Field419` | `int` |  | Yes |
| `Field420` | `int` |  | Yes |

### `SGBSalaries`

- Estimated rows: `0`
- Heuristic primary key: `PaymentID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PaymentID` | `INTEGER` | 10 | No |
| `DataYear` | `str` |  | Yes |
| `Month` | `int` |  | Yes |
| `StaffCategory` | `str` |  | Yes |
| `StaffId` | `int` |  | Yes |
| `Sname` | `str` |  | Yes |
| `Fname` | `str` |  | Yes |
| `PayMeth` | `str` |  | Yes |
| `VoucherNo` | `int` |  | Yes |
| `CoaAccount` | `int` |  | Yes |
| `TransNumber` | `int` |  | Yes |
| `GSalary` | `decimal.Decimal` |  | Yes |
| `PAYE` | `decimal.Decimal` |  | Yes |
| `UIF` | `decimal.Decimal` |  | Yes |
| `Medical` | `decimal.Decimal` |  | Yes |
| `Pension` | `decimal.Decimal` |  | Yes |
| `Other` | `decimal.Decimal` |  | Yes |
| `SUIF` | `decimal.Decimal` |  | Yes |
| `SMedical` | `decimal.Decimal` |  | Yes |
| `SPension` | `decimal.Decimal` |  | Yes |
| `SOther` | `decimal.Decimal` |  | Yes |
| `SDL` | `decimal.Decimal` |  | Yes |

### `SIAS_AreaofFunctionalLimmitation`

- Estimated rows: `104`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `CategoryId` | `INTEGER` | 10 | Yes |
| `Name` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SIAS_Areas_Needing_Ongoing_support`

- Estimated rows: `0`
- Heuristic primary key: `LearnerID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerID` | `WVARCHAR` | 20 | Yes |
| `Month_Year` | `WVARCHAR` | 50 | Yes |
| `Grade` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Area_of_Need` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Nature_of_Support` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `Review_date` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SIAS_Areas_Of_Concern`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `AreaOfConcern` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DateDetected` | `WVARCHAR` | 50 | Yes |
| `HowDetected` | `WLONGVARCHAR` | 1073741823 | Yes |
| `How_is_Learner_Affected` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Diagnosed_Disability` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Health_care_Proffessional` | `WVARCHAR` | 255 | Yes |
| `Date_Of_Assessment` | `WVARCHAR` | 50 | Yes |
| `Summary_Result` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Consultation_Logs`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Consultation_Date` | `WVARCHAR` | 50 | Yes |
| `Consultation_Purpose` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Consultation_Outcome` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Consultation_Views_by_parent` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Signed_by_Name` | `WVARCHAR` | 255 | Yes |
| `Designation` | `WVARCHAR` | 255 | Yes |
| `Signature` | `BIT` | 1 | No |
| `Date_Signed` | `WVARCHAR` | 50 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Criteria_For_Selection`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Sub_Section` | `INTEGER` | 10 | Yes |
| `Disability` | `WLONGVARCHAR` | 1073741823 | Yes |
| `AreaOfFunctionalLimitation` | `WVARCHAR` | 255 | Yes |
| `Recomendation` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Curriculum_Intervention`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Intervention_Area` | `INTEGER` | 10 | Yes |
| `Challenges` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Successes` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `Additional_Support` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SIAS_Curriculum_Intervention_AdditionalSupport_And_Plan`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `AdditionalSupport` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_DBST_Checklist`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Support_Needed` | `WVARCHAR` | 50 | Yes |
| `Frequency` | `WVARCHAR` | 50 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `Source` | `WVARCHAR` | 50 | Yes |

### `SIAS_DBST_Review`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `DBSTDesagreeTI` | `INTEGER` | 10 | Yes |
| `DBSTAgreeTI` | `INTEGER` | 10 | Yes |
| `DBSTDesagreeTS` | `INTEGER` | 10 | Yes |
| `DBSTAgreeTS` | `INTEGER` | 10 | Yes |
| `Barrier_Identification_Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Intervention_Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_DBST_Support_Request`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Motivation_For_Support` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Support_Area` | `WLONGVARCHAR` | 1073741823 | Yes |
| `SBST_Name` | `WLONGVARCHAR` | 1073741823 | Yes |
| `SBST_Signature` | `BIT` | 1 | No |
| `SBST_Date_Signed` | `WVARCHAR` | 50 | Yes |
| `Does_Parents_Support_This_Request` | `BIT` | 1 | No |
| `Parent_Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_Name` | `WVARCHAR` | 50 | Yes |
| `Does_Principal_Support_Request` | `BIT` | 1 | No |
| `Reason_for_Decision` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Designation` | `WVARCHAR` | 50 | Yes |
| `Principal_Date_signed` | `WVARCHAR` | 50 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `Principal_Signature` | `BIT` | 1 | No |

### `SIAS_Disabilities_Categories`

- Estimated rows: `16`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SIAS_EarlyIntervention`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `vyear` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Berrier` | `WLONGVARCHAR` | 1073741823 | Yes |
| `serviceRendered` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Factors_Community`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Concern` | `WVARCHAR` | 255 | Yes |
| `Strength` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Frequency_Of_Provision`

- Estimated rows: `12`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SIAS_Health_Professional_Report`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Impairment_Type` | `WVARCHAR` | 50 | Yes |
| `Comments` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Medical_Record_Viewed` | `TINYINT` | 3 | Yes |
| `Medical_Record_Attached` | `TINYINT` | 3 | Yes |

### `SIAS_IndividualSupportPlan`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Area_Support_Needed` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Target_Tobe_Achived` | `WVARCHAR` | 255 | Yes |
| `Strategy_Of_Intervention` | `WVARCHAR` | 255 | Yes |
| `Time_Frame` | `WVARCHAR` | 255 | Yes |
| `Person_Responsible` | `WVARCHAR` | 255 | Yes |
| `Review_Date` | `WVARCHAR` | 30 | Yes |
| `Progress_Comments` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Learner_Action_Plan`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Support_area` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Support_level` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Support_Discription` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `Responsible_person` | `WVARCHAR` | 255 | Yes |
| `Parent_Aggree_With_action` | `INTEGER` | 10 | Yes |
| `Parent_Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_name` | `WVARCHAR` | 255 | Yes |
| `Parent_Signature` | `INTEGER` | 10 | Yes |
| `Parent_Date_signed` | `WVARCHAR` | 50 | Yes |

### `SIAS_Learner_Action_Plan_Signature`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_Aggree_With_action` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_name` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_Signature` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_Date_signed` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Learner_Background_Info`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Roadtoheath_Shown` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Growth_Progress` | `WLONGVARCHAR` | 1073741823 | Yes |
| `PreOrPost_Natal` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Immunisation_record` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Hospital_admissions` | `WLONGVARCHAR` | 1073741823 | Yes |
| `developmental_problems` | `WLONGVARCHAR` | 1073741823 | Yes |
| `chronic_condition` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Screening_result` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `Roadtoheath_Shown_Number` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Growth_Progress_remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `PreOrPost_Natal_remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Immunisation_record_remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Hospital_admissions_remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `developmental_problems_remarks` | `WLONGVARCHAR` | 1073741823 | Yes |
| `chronic_condition_remarks` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SIAS_Learner_Profile`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Problem1` | `BIT` | 1 | No |
| `Problem2` | `BIT` | 1 | No |
| `Problem3` | `BIT` | 1 | No |
| `Problem4` | `BIT` | 1 | No |
| `Problem5` | `BIT` | 1 | No |
| `Problem6` | `BIT` | 1 | No |
| `Problem7` | `BIT` | 1 | No |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Learner_Support_Needs`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Support_Area` | `INTEGER` | 10 | Yes |
| `School_Need` | `WLONGVARCHAR` | 1073741823 | Yes |
| `School_Available` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_LearnerDetails`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Patient_Number` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Name_Of_Provider` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Facility` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Assessment_Date` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Profesion` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Tel_number` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_SBST_Review`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `SBSTDesagreeTI` | `INTEGER` | 10 | Yes |
| `SBSTAgreeTI` | `INTEGER` | 10 | Yes |
| `SBSTDesagreeTS` | `INTEGER` | 10 | Yes |
| `SBSTAgreeTS` | `INTEGER` | 10 | Yes |
| `SummaryTSSupport` | `WLONGVARCHAR` | 1073741823 | Yes |
| `SummaryTISupport` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_School_Action_Plan`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Stregnth_Needs_Area` | `WVARCHAR` | 255 | Yes |

### `SIAS_Source`

- Estimated rows: `14`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SIAS_Strength_and_Need`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `LearnerID` | `WVARCHAR` | 50 | Yes |
| `Stregnth_Needs_Area` | `INTEGER` | 10 | Yes |
| `Needs` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Strengths` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Support_Needed` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Frequency` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Source` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |

### `SIAS_Strength_Needs_Areas`

- Estimated rows: `12`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Support_Area` | `WVARCHAR` | 255 | Yes |

### `SIAS_Suport_Needs`

- Estimated rows: `58`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `SupportNeed` | `WVARCHAR` | 50 | Yes |

### `SIAS_Support_Areas`

- Estimated rows: `10`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Support_Type` | `WVARCHAR` | 255 | Yes |

### `SNE_Action_Review`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Action` | `INTEGER` | 10 | Yes |
| `Name` | `WVARCHAR` | 255 | Yes |
| `Outcome` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Designation` | `WVARCHAR` | 255 | Yes |
| `Review_Date` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Assessment_Supp_Req`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `GridID` | `INTEGER` | 10 | Yes |
| `Support_Area` | `INTEGER` | 10 | Yes |
| `Level` | `WVARCHAR` | 20 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Assessment_Supp_Req_Rating`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Support_Area` | `INTEGER` | 10 | Yes |
| `Rating` | `INTEGER` | 10 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Criteria_For_Selection`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Sub_Section` | `INTEGER` | 10 | Yes |
| `Score` | `INTEGER` | 10 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Criteria_For_Selection_Other`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `None_Mild` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Moderate` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Severe` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Score` | `INTEGER` | 10 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_DBST_Review_ILST_Request`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `ISLT_Coord_Educ_Req_Made` | `BIT` | 1 | No |
| `Parent_Accept_Recom` | `BIT` | 1 | No |
| `Parent_Reason` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ISLT_Approved_Reason` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ISLT_Not_Approved_Reason` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DBST_Support_School_Site` | `INTEGER` | 10 | Yes |
| `Senior_Manager_Approval` | `WLONGVARCHAR` | 1073741823 | Yes |
| `School_Discussed_Parent` | `BIT` | 1 | No |
| `School_Discussed_Comment` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_DBST_Support_Strategy`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Support_Needed` | `WVARCHAR` | 255 | Yes |
| `Support_Area` | `INTEGER` | 10 | Yes |
| `Support_Level` | `WVARCHAR` | 1 | Yes |
| `School_Steps` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Learner_Steps` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Person_Responsible` | `WVARCHAR` | 255 | Yes |
| `Timeframe` | `WVARCHAR` | 255 | Yes |
| `Budget` | `WVARCHAR` | 100 | Yes |
| `School_Outcome` | `WVARCHAR` | 255 | Yes |
| `Learner_Outcome` | `WVARCHAR` | 255 | Yes |
| `Designation` | `WVARCHAR` | 255 | Yes |
| `Review_Date` | `TIMESTAMP` | 19 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Factors_Classroom`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Enabling_Factor` | `WVARCHAR` | 255 | Yes |
| `Barrier` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Factors_Community`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Positive_Influence` | `WVARCHAR` | 255 | Yes |
| `Barrier` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Factors_School`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Enabling_Factor` | `WVARCHAR` | 255 | Yes |
| `Barrier` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Health_Professional_Report`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Impairment_Type` | `WVARCHAR` | 4 | Yes |
| `Medical_Record_Viewed` | `BIT` | 1 | No |
| `Medical_Record_Attached` | `BIT` | 1 | No |
| `Comments` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_ILST_Intervention_Records`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Whole_School_Development` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Educator_Training` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Learner_Support` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Learner_Parent_Discussed` | `BIT` | 1 | No |
| `Learner_Parent_Response` | `WLONGVARCHAR` | 1073741823 | Yes |
| `ILST_Analysis_To_DBST` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Principal_Approve_Request_DBST` | `BIT` | 1 | No |
| `Principal_Reason` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Circuit_Manager_Endores` | `BIT` | 1 | No |
| `Circuit_Manager_Reason` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_ISP`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Action` | `INTEGER` | 10 | Yes |
| `Target` | `WVARCHAR` | 255 | Yes |
| `Strategy` | `WVARCHAR` | 255 | Yes |
| `Achievement_Criteria` | `WVARCHAR` | 255 | Yes |
| `Person_Responsible` | `WVARCHAR` | 255 | Yes |
| `Review_Date` | `WVARCHAR` | 30 | Yes |
| `Review_Comments` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Learner_Background_Info`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Nature_Of_Support_Received` | `WVARCHAR` | 255 | Yes |
| `Name_Of_Provider` | `WVARCHAR` | 255 | Yes |
| `Contact_Details` | `WVARCHAR` | 255 | Yes |
| `Disability` | `WVARCHAR` | 255 | Yes |
| `Family_Situation` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Parent_Understanding_Of_Child` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Learner_Impairment_Area`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Impairment_Area` | `INTEGER` | 10 | Yes |
| `Mild_Imp` | `WVARCHAR` | 255 | Yes |
| `Moderate_Imp` | `WVARCHAR` | 255 | Yes |
| `Severe_Imp` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Learner_Supp_Needs`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Disability_Descr` | `WVARCHAR` | 255 | Yes |
| `Psycho_Social_Support` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Learner_Support_Needs`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Support_Area` | `INTEGER` | 10 | Yes |
| `Low_Moderate_High` | `WVARCHAR` | 20 | Yes |
| `School_Need` | `WVARCHAR` | 255 | Yes |
| `School_Available` | `WVARCHAR` | 255 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_Learning_And_Development_Barriers`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `Learning` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Communication` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Behavioural_Social_Competence` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Health_Wellness_Personal_Care` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Physical_Access` | `WLONGVARCHAR` | 1073741823 | Yes |
| `Data_Year` | `INTEGER` | 10 | Yes |
| `LearnerID` | `INTEGER` | 10 | Yes |

### `SNE_lu_Activity_Domain_Limit_Desc`

- Estimated rows: `28`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `DescMild` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DescMod` | `WLONGVARCHAR` | 1073741823 | Yes |
| `DescSevere` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SNE_lu_Activity_Domain_Sub_Section`

- Estimated rows: `29`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Activity_Domain` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SNE_lu_AreaID_of_Support`

- Estimated rows: `89`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Area_of_Support` | `INTEGER` | 10 | Yes |
| `Support_Areas` | `INTEGER` | 10 | Yes |

### `SNE_lu_Assessment_Support_Area`

- Estimated rows: `6`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SNE_lu_Impairment_Area`

- Estimated rows: `8`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SNE_lu_ISP_Actions`

- Estimated rows: `5`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 100 | Yes |

### `SNE_lu_Sub_Support_Area`

- Estimated rows: `37`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Support_Description` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SNE_lu_Support_Area`

- Estimated rows: `5`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 50 | Yes |

### `SNE_Survey2008AssistiveDevice`

- Estimated rows: `0`
- Heuristic primary key: `AssistiveDevice`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AssistiveDevice` | `INTEGER` | 10 | Yes |
| `Needed` | `INTEGER` | 10 | Yes |
| `InUse` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008EducatorINSET`

- Estimated rows: `0`
- Heuristic primary key: `IDNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `IDNumber` | `WVARCHAR` | 13 | Yes |
| `Attended` | `INTEGER` | 10 | Yes |
| `Training` | `WVARCHAR` | 50 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008EducatorOtherSpecialisation`

- Estimated rows: `0`
- Heuristic primary key: `IDNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `IDNumber` | `WVARCHAR` | 13 | Yes |
| `Specialisation` | `WVARCHAR` | 50 | Yes |
| `Months` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008EducatorPhase`

- Estimated rows: `0`
- Heuristic primary key: `Phase`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Phase` | `INTEGER` | 10 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008EducatorSpecialisation`

- Estimated rows: `0`
- Heuristic primary key: `IDNumber`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `IDNumber` | `WVARCHAR` | 13 | Yes |
| `Specialisation` | `INTEGER` | 10 | Yes |
| `Months` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008ExtraMural`

- Estimated rows: `0`
- Heuristic primary key: `Phase`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Phase` | `WVARCHAR` | 15 | Yes |
| `Race` | `WVARCHAR` | 15 | Yes |
| `gender` | `WVARCHAR` | 6 | Yes |
| `Drama` | `INTEGER` | 10 | Yes |
| `Dance` | `INTEGER` | 10 | Yes |
| `Music` | `INTEGER` | 10 | Yes |
| `Choir` | `INTEGER` | 10 | Yes |
| `VisualArt` | `INTEGER` | 10 | Yes |
| `Athletics` | `INTEGER` | 10 | Yes |
| `Chess` | `INTEGER` | 10 | Yes |
| `Cricket` | `INTEGER` | 10 | Yes |
| `Hockey` | `INTEGER` | 10 | Yes |
| `Netball` | `INTEGER` | 10 | Yes |
| `Softball` | `INTEGER` | 10 | Yes |
| `Soccer` | `INTEGER` | 10 | Yes |
| `Rugby` | `INTEGER` | 10 | Yes |
| `Tennis` | `INTEGER` | 10 | Yes |
| `Volleyball` | `INTEGER` | 10 | Yes |
| `WaterSports` | `INTEGER` | 10 | Yes |
| `DebatingSociety` | `INTEGER` | 10 | Yes |
| `Boxing` | `INTEGER` | 10 | Yes |
| `Karate` | `INTEGER` | 10 | Yes |
| `drummajorettes` | `INTEGER` | 10 | Yes |
| `SpecialOlymipcs` | `INTEGER` | 10 | Yes |
| `ParaOlympics` | `INTEGER` | 10 | Yes |
| `Swimming` | `INTEGER` | 10 | Yes |
| `other` | `INTEGER` | 10 | Yes |
| `form` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008GradeByPregnant`

- Estimated rows: `0`
- Heuristic primary key: `Gradeid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Gradeid` | `INTEGER` | 10 | Yes |
| `total` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008HealthProfessional`

- Estimated rows: `0`
- Heuristic primary key: `APPOINTMENTNATURE`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `APPOINTMENTNATURE` | `INTEGER` | 10 | Yes |
| `staffcategory` | `INTEGER` | 10 | Yes |
| `duration` | `INTEGER` | 10 | Yes |
| `gender` | `WVARCHAR` | 1 | Yes |
| `Remuneration` | `INTEGER` | 10 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008LearnerAge`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `GradeID` | `INTEGER` | 10 | Yes |
| `Age` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 1 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008LearnerDeceasedParent`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DeceasedParent` | `INTEGER` | 10 | Yes |
| `GradeID` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 1 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008LearnerEnrollment`

- Estimated rows: `0`
- Heuristic primary key: `Gradeid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Gradeid` | `INTEGER` | 10 | Yes |
| `class` | `INTEGER` | 10 | Yes |
| `male` | `INTEGER` | 10 | Yes |
| `female` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008LearnerLanguage`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Language` | `INTEGER` | 10 | Yes |
| `Type` | `WVARCHAR` | 4 | Yes |
| `GradeID` | `INTEGER` | 10 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008LearnerTransfers`

- Estimated rows: `0`
- Heuristic primary key: `gradeid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `gradeid` | `INTEGER` | 10 | Yes |
| `Transfer_Type` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 1 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008Mortality`

- Estimated rows: `0`
- Heuristic primary key: `Date`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Date` | `TIMESTAMP` | 19 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `AgeRange` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 6 | Yes |
| `mortality` | `WVARCHAR` | 10 | Yes |
| `category` | `WVARCHAR` | 15 | Yes |

### `SNE_Survey2008OtherAssistiveDevice`

- Estimated rows: `0`
- Heuristic primary key: `AssistiveDevice`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AssistiveDevice` | `WVARCHAR` | 50 | Yes |
| `Needed` | `INTEGER` | 10 | Yes |
| `InUse` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008PopulationGroup`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `PopulationGroup` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 1 | Yes |
| `GradeID` | `INTEGER` | 10 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008Promotions`

- Estimated rows: `0`
- Heuristic primary key: `Grade`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Grade` | `INTEGER` | 10 | Yes |
| `Passed` | `INTEGER` | 10 | Yes |
| `Repeats` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 6 | Yes |
| `NotPromoted` | `INTEGER` | 10 | Yes |
| `DropOuts` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008SchoolFees`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `GradeID` | `INTEGER` | 10 | Yes |
| `Fee` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SNE_Survey2008SocialGrant`

- Estimated rows: `0`
- Heuristic primary key: `GradeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SGReceive` | `INTEGER` | 10 | Yes |
| `GradeID` | `INTEGER` | 10 | Yes |
| `Gender` | `WVARCHAR` | 1 | Yes |
| `total` | `INTEGER` | 10 | Yes |
| `DataYear` | `INTEGER` | 10 | Yes |

### `SportFields`

- Estimated rows: `55`
- Heuristic primary key: `Datayear`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Datayear` | `WVARCHAR` | 10 | Yes |
| `Sport` | `INTEGER` | 10 | Yes |
| `Standard` | `int` |  | Yes |
| `Nonstandard` | `int` |  | Yes |
| `Otherfields` | `int` |  | Yes |
| `Lawn` | `int` |  | Yes |
| `Gravel` | `int` |  | Yes |
| `Tar` | `int` |  | Yes |
| `Other` | `int` |  | Yes |

### `SSE_Functions`

- Estimated rows: `0`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TabID` | `INTEGER` | 10 | Yes |
| `InstID` | `WVARCHAR` | 15 | Yes |
| `field1` | `WVARCHAR` | 200 | Yes |
| `field2` | `WVARCHAR` | 200 | Yes |
| `field3` | `WVARCHAR` | 200 | Yes |
| `field4` | `WVARCHAR` | 200 | Yes |
| `field5` | `WVARCHAR` | 200 | Yes |
| `field6` | `WVARCHAR` | 200 | Yes |
| `field7` | `WVARCHAR` | 200 | Yes |
| `field8` | `WVARCHAR` | 200 | Yes |
| `field9` | `WVARCHAR` | 200 | Yes |
| `field10` | `WVARCHAR` | 200 | Yes |
| `field11` | `WVARCHAR` | 200 | Yes |
| `field12` | `WVARCHAR` | 200 | Yes |
| `iRow` | `INTEGER` | 10 | Yes |
| `field14` | `BIT` | 1 | No |
| `ID` | `INTEGER` | 10 | No |

### `SSE_Responsibility`

- Estimated rows: `0`
- Heuristic primary key: `TabID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TabNo` | `INTEGER` | 10 | Yes |
| `TabID` | `WVARCHAR` | 10 | Yes |
| `RID` | `INTEGER` | 10 | Yes |
| `Member_type` | `WVARCHAR` | 10 | Yes |
| `Title` | `WVARCHAR` | 20 | Yes |
| `FName` | `WVARCHAR` | 100 | Yes |
| `SName` | `WVARCHAR` | 200 | Yes |
| `Position` | `WVARCHAR` | 50 | Yes |
| `Status` | `WVARCHAR` | 10 | Yes |
| `SDate` | `TIMESTAMP` | 19 | Yes |
| `EDate` | `TIMESTAMP` | 19 | Yes |

### `Staff_CalendarTerms`

- Estimated rows: `72`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Quater` | `WVARCHAR` | 50 | Yes |
| `StartDate` | `TIMESTAMP` | 19 | Yes |
| `EndDate` | `TIMESTAMP` | 19 | Yes |
| `CurrentYear` | `WVARCHAR` | 50 | Yes |
| `Term` | `INTEGER` | 10 | Yes |

### `Staff_CalendarWeekSetup`

- Estimated rows: `124`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `WeekID` | `TIMESTAMP` | 19 | Yes |
| `Holiday` | `TIMESTAMP` | 19 | Yes |
| `TermId` | `INTEGER` | 10 | Yes |
| `Reason` | `WVARCHAR` | 100 | Yes |

### `StaffAbsentees`

- Estimated rows: `2282`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Staffid` | `int` |  | Yes |
| `DateAbsent` | `datetime.datetime` |  | Yes |
| `WeekId` | `datetime.datetime` |  | Yes |
| `Gender` | `str` |  | Yes |
| `Category` | `str` |  | Yes |

### `StaffAbsenteeStatistics`

- Estimated rows: `4068`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `WeekId` | `datetime.datetime` |  | Yes |
| `Gender` | `str` |  | Yes |
| `TotalAbsent` | `int` |  | Yes |
| `TotalAttended` | `int` |  | Yes |
| `PossAttended` | `int` |  | Yes |
| `Days` | `int` |  | Yes |
| `AveAttended` | `int` |  | Yes |
| `Quantity` | `int` |  | Yes |
| `Datayear` | `str` |  | Yes |
| `Category` | `str` |  | Yes |
| `Remuneration` | `int` |  | Yes |

### `StaffLeave`

- Estimated rows: `929`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `LinkId` | `INTEGER` | 10 | Yes |
| `DateStart` | `TIMESTAMP` | 19 | Yes |
| `DateEnd` | `TIMESTAMP` | 19 | Yes |
| `Type` | `str` |  | Yes |
| `Days` | `int` |  | Yes |
| `Comment` | `str` |  | Yes |
| `PersonnelCategory` | `str` |  | Yes |
| `Year` | `str` |  | Yes |
| `Replaced` | `str` |  | Yes |
| `Paid` | `str` |  | Yes |
| `Documentation` | `str` |  | Yes |
| `LeaveDocRequired` | `bool` |  | Yes |
| `WeekID` | `datetime.datetime` |  | Yes |
| `TmpField` | `str` |  | Yes |

### `StaffMembers`

- Estimated rows: `35`
- Heuristic primary key: `StaffID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `StaffID` | `INTEGER` | 10 | No |
| `FName` | `WVARCHAR` | 100 | Yes |
| `SName` | `str` |  | Yes |
| `Initials` | `str` |  | Yes |
| `Address1` | `str` |  | Yes |
| `Address2` | `str` |  | Yes |
| `Address3` | `str` |  | Yes |
| `Code` | `str` |  | Yes |
| `Tel1Code` | `str` |  | Yes |
| `Tel1` | `str` |  | Yes |
| `BirthDate` | `str` |  | Yes |
| `IDNumber` | `str` |  | Yes |
| `Gender` | `str` |  | Yes |
| `Race` | `str` |  | Yes |
| `HomeLanguage` | `str` |  | Yes |
| `Subsidies` | `str` |  | Yes |
| `MedName` | `str` |  | Yes |
| `MedNo` | `str` |  | Yes |
| `Spouse` | `str` |  | Yes |
| `ENumber` | `str` |  | Yes |
| `TaxNo` | `str` |  | Yes |
| `Skills` | `str` |  | Yes |
| `DateJoined` | `str` |  | Yes |
| `Tel2Code` | `str` |  | Yes |
| `Tel2` | `str` |  | Yes |
| `PersalNumber` | `str` |  | Yes |
| `Active` | `str` |  | Yes |
| `Capacity` | `str` |  | Yes |
| `TermEnds` | `datetime.datetime` |  | Yes |
| `Postal1` | `str` |  | Yes |
| `Postal2` | `str` |  | Yes |
| `Postal3` | `str` |  | Yes |
| `PostalCode` | `str` |  | Yes |
| `Title` | `str` |  | Yes |
| `Managementposition` | `str` |  | Yes |
| `Institution` | `str` |  | Yes |
| `Academic` | `str` |  | Yes |
| `Professional` | `str` |  | Yes |
| `PersonnelCategory` | `str` |  | Yes |
| `EmployType` | `str` |  | Yes |
| `Time` | `str` |  | Yes |
| `Remuneration` | `str` |  | Yes |
| `Status` | `str` |  | Yes |
| `EmailAddress` | `str` |  | Yes |
| `ICTSkill` | `str` |  | Yes |
| `TSTransactionCategory` | `int` |  | Yes |
| `TSStatusFlag` | `int` |  | Yes |
| `TSReportStatusFlag` | `int` |  | Yes |
| `TSReasonCode` | `int` |  | Yes |
| `LuritsIndicator` | `int` |  | Yes |
| `LuritsFlag` | `int` |  | Yes |
| `LuritsNumber` | `int` |  | Yes |
| `TSSentFileName` | `str` |  | Yes |
| `TSDateLastUpdate` | `datetime.datetime` |  | Yes |
| `TSLastUpdatedBy` | `str` |  | Yes |
| `Intermediate` | `str` |  | Yes |
| `LuritsStatus` | `str` |  | Yes |
| `SACitizen` | `int` |  | Yes |
| `Country` | `str` |  | Yes |
| `WorkPermit` | `int` |  | Yes |
| `WorkPermitNo` | `str` |  | Yes |
| `WorkPermitDate` | `str` |  | Yes |
| `ReasonForNoIDNo` | `int` |  | Yes |
| `DisabilityStatus` | `str` |  | Yes |
| `UnionName` | `str` |  | Yes |
| `UnionNo` | `str` |  | Yes |
| `UnionName2` | `str` |  | Yes |
| `UnionNo2` | `str` |  | Yes |
| `UnionNameX` | `str` |  | Yes |
| `UnionNoX` | `str` |  | Yes |

### `SubjectAverages`

- Estimated rows: `5262`
- Heuristic primary key: `AverageID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `AverageID` | `INTEGER` | 10 | No |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `ReportID` | `INTEGER` | 10 | Yes |
| `SubjectLevel` | `WVARCHAR` | 50 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `Average` | `DOUBLE` | 53 | Yes |
| `AveragePer` | `DOUBLE` | 53 | Yes |
| `DataYear` | `WVARCHAR` | 20 | Yes |
| `MarkUsed` | `WVARCHAR` | 200 | Yes |

### `SubjectCriteria`

- Estimated rows: `160578`
- Heuristic primary key: `Subjectid`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Subjectid` | `INTEGER` | 10 | Yes |
| `CriterionId` | `int` |  | Yes |
| `Description` | `str` |  | Yes |
| `Grade` | `int` |  | Yes |
| `Weighting` | `float` |  | Yes |
| `SubjectLevel` | `str` |  | Yes |
| `CriterionScore` | `int` |  | Yes |
| `DataYear` | `str` |  | Yes |
| `SubHeading` | `str` |  | Yes |
| `DateAdded` | `datetime.datetime` |  | Yes |
| `Type` | `str` |  | Yes |
| `Outcomes` | `str` |  | Yes |
| `Activities` | `str` |  | Yes |
| `Assessments` | `str` |  | Yes |
| `SectionId` | `int` |  | Yes |
| `UseActivities` | `bool` |  | Yes |
| `IncludeFFL` | `bool` |  | Yes |
| `IncludeExam` | `bool` |  | Yes |
| `Updated` | `str` |  | Yes |
| `QuarterlyTest` | `bool` |  | Yes |
| `FETCommonTest` | `bool` |  | Yes |
| `DescriptionAfr` | `str` |  | Yes |
| `DescriptionVern` | `str` |  | Yes |
| `TaskType` | `int` |  | Yes |
| `SBATask` | `bool` |  | Yes |
| `SBAWeight` | `float` |  | Yes |
| `FixedCriterionScore` | `int` |  | Yes |
| `FixedWeight` | `float` |  | Yes |
| `FixedSBAWeight` | `float` |  | Yes |
| `SubjSplitNo` | `int` |  | Yes |
| `OffSubjectID` | `int` |  | Yes |
| `OffCriterionId` | `int` |  | Yes |
| `RecLocked` | `bool` |  | Yes |
| `Status` | `int` |  | Yes |
| `Fixed0Weight` | `bool` |  | Yes |

### `SubjectCriteriaActivities`

- Estimated rows: `151048`
- Heuristic primary key: `ActivityID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ActivityID` | `INTEGER` | 10 | No |
| `Activity` | `WVARCHAR` | 200 | Yes |
| `RawMark` | `INTEGER` | 10 | Yes |
| `Weight` | `DOUBLE` | 53 | Yes |
| `ActivityDate` | `TIMESTAMP` | 19 | Yes |
| `CriterionID` | `INTEGER` | 10 | Yes |
| `ActivityAfr` | `WVARCHAR` | 200 | Yes |
| `ActivityVern` | `WVARCHAR` | 200 | Yes |
| `OffCriterionId` | `INTEGER` | 10 | Yes |
| `OffActivityID` | `INTEGER` | 10 | Yes |
| `RecLocked` | `BIT` | 1 | No |
| `GetFromOffCriterionId` | `INTEGER` | 10 | Yes |

### `SubjectCriteriaDeviations`

- Estimated rows: `6923`
- Heuristic primary key: `OffCriterionId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `OffCriterionId` | `INTEGER` | 10 | Yes |
| `ProvinceNo` | `INTEGER` | 10 | Yes |
| `CriterionScore` | `INTEGER` | 10 | Yes |
| `Weighting` | `DOUBLE` | 53 | Yes |
| `SBAWeight` | `DOUBLE` | 53 | Yes |
| `FixedCriterionScore` | `INTEGER` | 10 | Yes |
| `FixedWeight` | `DOUBLE` | 53 | Yes |
| `FixedSBAWeight` | `DOUBLE` | 53 | Yes |
| `Fixed0Weight` | `BIT` | 1 | No |

### `SubjectCriteriaTypes`

- Estimated rows: `169`
- Heuristic primary key: `TaskType`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TaskType` | `INTEGER` | 10 | No |
| `IsForLanguage` | `BIT` | 1 | No |
| `Desc_English` | `WVARCHAR` | 255 | Yes |
| `Desc_Afrikaans` | `WVARCHAR` | 255 | Yes |
| `Desc_IsiNdebele` | `WVARCHAR` | 255 | Yes |
| `Desc_IsiXhosa` | `WVARCHAR` | 255 | Yes |
| `Desc_IsiZulu` | `WVARCHAR` | 255 | Yes |
| `Desc_Sepedi` | `WVARCHAR` | 255 | Yes |
| `Desc_Sesotho` | `WVARCHAR` | 255 | Yes |
| `Desc_Setswana` | `WVARCHAR` | 255 | Yes |
| `Desc_SiSwati` | `WVARCHAR` | 255 | Yes |
| `Desc_Tshivenda` | `WVARCHAR` | 255 | Yes |
| `Desc_Xitsonga` | `WVARCHAR` | 255 | Yes |

### `SubjectDept_Info`

- Estimated rows: `0`
- Heuristic primary key: `SubjectDept`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SubjectDept` | `INTEGER` | 10 | No |
| `DeptName` | `WVARCHAR` | 100 | Yes |
| `DeptDesc` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SubjectMainTopics`

- Estimated rows: `2001`
- Heuristic primary key: `MainTopicID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `MainTopicID` | `INTEGER` | 10 | No |
| `MainPosition` | `INTEGER` | 10 | Yes |
| `Description` | `WVARCHAR` | 200 | Yes |
| `AfrDescription` | `WVARCHAR` | 200 | Yes |
| `VernDescription` | `WVARCHAR` | 200 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `OfficialSubjectID` | `INTEGER` | 10 | Yes |
| `RecLocked` | `BIT` | 1 | No |
| `PatchVer` | `WVARCHAR` | 25 | Yes |
| `GroupNo` | `INTEGER` | 10 | Yes |

### `SubjectOutcomes`

- Estimated rows: `9127`
- Heuristic primary key: `OutcomeID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `OutcomeID` | `INTEGER` | 10 | No |
| `SubjectID` | `int` |  | Yes |
| `OutcomePosition` | `int` |  | Yes |
| `Description` | `str` |  | Yes |
| `AfrDescription` | `str` |  | Yes |
| `VernDescription` | `str` |  | Yes |
| `MainTopicID` | `int` |  | Yes |
| `OfficialSubjectID` | `int` |  | Yes |
| `RecLocked` | `bool` |  | Yes |
| `PatchVer` | `str` |  | Yes |
| `MainPosition` | `int` |  | Yes |

### `Subjects`

- Estimated rows: `1995`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Name` | `WVARCHAR` | 200 | Yes |
| `Key` | `WVARCHAR` | 50 | Yes |
| `Code` | `str` |  | Yes |
| `Group` | `str` |  | Yes |
| `Selected` | `int` |  | Yes |
| `Phase` | `int` |  | Yes |
| `Afrname` | `str` |  | Yes |
| `PrintOrder` | `int` |  | Yes |
| `LuritsCode` | `str` |  | Yes |
| `CTAWeight` | `int` |  | Yes |
| `ExcludeSchedule` | `int` |  | Yes |
| `SubjectStatus` | `int` |  | Yes |
| `SubjectGrade` | `int` |  | Yes |
| `OfficialSubjectID` | `int` |  | Yes |
| `excludereport` | `float` |  | Yes |
| `ExcludeAve` | `bool` |  | Yes |

### `SubjectSets`

- Estimated rows: `70`
- Heuristic primary key: `SubjectID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Description` | `WVARCHAR` | 200 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `SubjectSetId` | `INTEGER` | 10 | Yes |
| `SubjectSetGrade` | `INTEGER` | 10 | Yes |

### `SubjectsMusicInstruments`

- Estimated rows: `63`
- Heuristic primary key: `InstrumentID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `InstrumentID` | `INTEGER` | 10 | Yes |
| `InstrumentDesc` | `WVARCHAR` | 255 | Yes |

### `SubjectsOfficial`

- Estimated rows: `1995`
- Heuristic primary key: `SubjID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SubjID` | `INTEGER` | 10 | No |
| `SubjName` | `WVARCHAR` | 200 | Yes |
| `SubjAfrName` | `WVARCHAR` | 200 | Yes |
| `SubjLuritsCode` | `WVARCHAR` | 50 | Yes |
| `SubjGrade` | `INTEGER` | 10 | Yes |
| `SubjGroup` | `WVARCHAR` | 10 | Yes |
| `SubjReportSplit` | `BIT` | 1 | No |
| `SubjOfficialLangNo` | `INTEGER` | 10 | Yes |
| `SubjOfficialLangDesc` | `WVARCHAR` | 255 | Yes |
| `SubjLocalID` | `INTEGER` | 10 | Yes |
| `Key` | `WVARCHAR` | 40 | Yes |
| `SubjGroupName` | `WVARCHAR` | 255 | Yes |
| `NscCode` | `WVARCHAR` | 10 | Yes |
| `NscCategory` | `WVARCHAR` | 255 | Yes |

### `SubjectsOfficial_OLD`

- Estimated rows: `1992`
- Heuristic primary key: `SubjID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SubjID` | `INTEGER` | 10 | No |
| `SubjName` | `WVARCHAR` | 200 | Yes |
| `SubjAfrName` | `WVARCHAR` | 200 | Yes |
| `SubjLuritsCode` | `WVARCHAR` | 50 | Yes |
| `SubjGrade` | `INTEGER` | 10 | Yes |
| `SubjGroup` | `WVARCHAR` | 10 | Yes |
| `SubjReportSplit` | `BIT` | 1 | No |
| `SubjOfficialLangNo` | `INTEGER` | 10 | Yes |
| `SubjOfficialLangDesc` | `WVARCHAR` | 255 | Yes |
| `SubjLocalID` | `INTEGER` | 10 | Yes |
| `Key` | `WVARCHAR` | 40 | Yes |
| `SubjGroupName` | `WVARCHAR` | 255 | Yes |
| `NscCode` | `WVARCHAR` | 10 | Yes |
| `NscCategory` | `WVARCHAR` | 255 | Yes |

### `SubjectsOfficialSettings`

- Estimated rows: `21337`
- Heuristic primary key: `OfficialSubjectID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `OfficialSubjectID` | `INTEGER` | 10 | Yes |
| `SubjNextOfficialSubjectID` | `INTEGER` | 10 | Yes |
| `SubjNextLuritsCode` | `WVARCHAR` | 50 | Yes |
| `SubjNextName` | `WVARCHAR` | 200 | Yes |
| `SBAWeight` | `DOUBLE` | 53 | Yes |
| `SBAMarks` | `INTEGER` | 10 | Yes |

### `SubjectSpecialisation`

- Estimated rows: `182`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Educatorid` | `int` |  | Yes |
| `Subjectid` | `int` |  | Yes |
| `TrainingYears` | `int` |  | Yes |
| `TeachingYears` | `int` |  | Yes |

### `SubjectsReportSplits`

- Estimated rows: `18861`
- Heuristic primary key: `SubjID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `SubjID` | `INTEGER` | 10 | Yes |
| `OfficialSubjectID` | `INTEGER` | 10 | Yes |
| `SubjSplitNo` | `INTEGER` | 10 | Yes |
| `SubjSplitName` | `WVARCHAR` | 50 | Yes |
| `SubjSplitNameAfr` | `WVARCHAR` | 50 | Yes |

### `SubjectsSettings`

- Estimated rows: `18052`
- Heuristic primary key: `SubjID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `SubjID` | `INTEGER` | 10 | Yes |
| `OfficialSubjectID` | `INTEGER` | 10 | Yes |
| `SBAWeight` | `DOUBLE` | 53 | Yes |
| `SBAMarks` | `INTEGER` | 10 | Yes |
| `SBALocked` | `BIT` | 1 | No |
| `SubjReportSplit` | `BIT` | 1 | No |
| `RecValidated` | `BIT` | 1 | No |

### `SubjMultiGetFrom`

- Estimated rows: `231`
- Heuristic primary key: `ID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `ID` | `INTEGER` | 10 | No |
| `FromOffSubjID` | `WVARCHAR` | 10 | Yes |
| `ToOffSubjID` | `WVARCHAR` | 10 | Yes |
| `To_OffActId` | `INTEGER` | 10 | Yes |
| `To_OffCritID` | `INTEGER` | 10 | Yes |
| `DataYear` | `WVARCHAR` | 10 | Yes |
| `GetFromOffCritID` | `WVARCHAR` | 25 | Yes |

### `SubstituteTT`

- Estimated rows: `0`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `AbsentEducator` | `WVARCHAR` | 50 | Yes |
| `SubEducator` | `WVARCHAR` | 50 | Yes |
| `Class` | `WVARCHAR` | 20 | Yes |
| `TTPeriod` | `INTEGER` | 10 | Yes |
| `TTDay` | `INTEGER` | 10 | Yes |
| `TTDate` | `WVARCHAR` | 50 | Yes |
| `Subject` | `WVARCHAR` | 200 | Yes |

### `SysLogs`

- Estimated rows: `360752`
- Heuristic primary key: `LogID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LogID` | `INTEGER` | 10 | No |
| `LogTypeNo` | `INTEGER` | 10 | Yes |
| `LogDateTime` | `TIMESTAMP` | 19 | Yes |
| `LogUserID` | `INTEGER` | 10 | Yes |
| `LogLinkID` | `INTEGER` | 10 | Yes |
| `LogLinkIDs` | `WVARCHAR` | 250 | Yes |
| `LogData` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SysSessions`

- Estimated rows: `2`
- Heuristic primary key: `SessionID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SessionID` | `INTEGER` | 10 | Yes |
| `SessionDateTime` | `TIMESTAMP` | 19 | Yes |
| `UserID` | `INTEGER` | 10 | Yes |
| `BusyDateTime` | `TIMESTAMP` | 19 | Yes |
| `BusyWith` | `WVARCHAR` | 255 | Yes |
| `ComputerInfo` | `WLONGVARCHAR` | 1073741823 | Yes |

### `SysSessionsLocks`

- Estimated rows: `1`
- Heuristic primary key: `SessionID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `SessionID` | `INTEGER` | 10 | Yes |
| `LockType` | `WVARCHAR` | 50 | Yes |
| `LockDateTime` | `TIMESTAMP` | 19 | Yes |
| `ScreenNo` | `WVARCHAR` | 50 | Yes |
| `Term` | `INTEGER` | 10 | Yes |
| `Grade` | `INTEGER` | 10 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `Class` | `INTEGER` | 10 | Yes |
| `EducatorGroupID` | `INTEGER` | 10 | Yes |

### `TaskOutcomes`

- Estimated rows: `300163`
- Heuristic primary key: `OutcomeId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `OutcomeId` | `INTEGER` | 10 | Yes |
| `TaskID` | `INTEGER` | 10 | Yes |
| `SubjectID` | `INTEGER` | 10 | Yes |
| `GradeID` | `INTEGER` | 10 | Yes |

### `TeachingLanguages`

- Estimated rows: `23`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Name` | `str` |  | Yes |

### `TempPromotions`

- Estimated rows: `5221`
- Heuristic primary key: `LearnerId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `LearnerId` | `INTEGER` | 10 | Yes |
| `AccNumber` | `WVARCHAR` | 50 | Yes |
| `Surname` | `WVARCHAR` | 200 | Yes |
| `Name` | `WVARCHAR` | 200 | Yes |
| `NewGrade` | `INTEGER` | 10 | Yes |
| `OldGrade` | `INTEGER` | 10 | Yes |
| `YearPromoted` | `WVARCHAR` | 50 | Yes |
| `Class` | `WVARCHAR` | 50 | Yes |
| `Gender` | `WVARCHAR` | 50 | Yes |
| `Status` | `WVARCHAR` | 50 | Yes |
| `StatusCalculated` | `WVARCHAR` | 50 | Yes |
| `TmpProgressed` | `BIT` | 1 | No |

### `TieClasses`

- Estimated rows: `0`
- Heuristic primary key: `TieID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TieID` | `INTEGER` | 10 | Yes |
| `Class` | `int` |  | Yes |

### `TieEducators`

- Estimated rows: `0`
- Heuristic primary key: `TieID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TieID` | `INTEGER` | 10 | Yes |
| `Educator` | `int` |  | Yes |
| `Subject` | `int` |  | Yes |

### `TieGroups`

- Estimated rows: `0`
- Heuristic primary key: `TieID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TieID` | `INTEGER` | 10 | Yes |
| `Description` | `str` |  | Yes |
| `Periods` | `int` |  | Yes |
| `Timetable` | `str` |  | Yes |

### `TieSubjects`

- Estimated rows: `0`
- Heuristic primary key: `TieId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TieId` | `INTEGER` | 10 | Yes |
| `Subject` | `int` |  | Yes |

### `TimetableInputs`

- Estimated rows: `0`
- Heuristic primary key: `InputID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Educator` | `INTEGER` | 10 | Yes |
| `Subject` | `INTEGER` | 10 | Yes |
| `Class` | `int` |  | Yes |
| `Periods` | `int` |  | Yes |
| `Timetable` | `str` |  | Yes |
| `InputID` | `int` |  | Yes |

### `TrainingAttended`

- Estimated rows: `2`
- Heuristic primary key: `id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `id` | `INTEGER` | 10 | No |
| `Course` | `str` |  | Yes |
| `Provider` | `str` |  | Yes |
| `Duration` | `int` |  | Yes |
| `Todate` | `datetime.datetime` |  | Yes |
| `Fromdate` | `datetime.datetime` |  | Yes |
| `ManualComp` | `str` |  | Yes |
| `Type` | `str` |  | Yes |
| `Category` | `str` |  | Yes |
| `Staffcategory` | `str` |  | Yes |
| `Staffmemberid` | `int` |  | Yes |
| `Funded` | `str` |  | Yes |
| `Method` | `str` |  | Yes |
| `SACEPoints` | `int` |  | Yes |

### `TransactionFiles`

- Estimated rows: `14`
- Heuristic primary key: `TransactionFileID`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TransactionFileID` | `INTEGER` | 10 | No |
| `TransactionFileCode` | `WVARCHAR` | 50 | Yes |
| `TransactionFileName` | `WVARCHAR` | 200 | Yes |
| `TransactionFileSeqNo` | `INTEGER` | 10 | Yes |

### `TransactionTypes`

- Estimated rows: `20`
- Heuristic primary key: `TransactionId`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `TransactionId` | `INTEGER` | 10 | Yes |
| `Description` | `str` |  | Yes |

### `VenueTypes`

- Estimated rows: `11`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Description` | `str` |  | Yes |

### `Weeksetup`

- Estimated rows: `157`
- Heuristic primary key: `Id`

| Column | Type | Size | Nullable |
|---|---|---:|---|
| `Id` | `INTEGER` | 10 | No |
| `Weekid` | `TIMESTAMP` | 19 | Yes |
| `Holiday` | `TIMESTAMP` | 19 | Yes |
| `TermId` | `INTEGER` | 10 | Yes |
| `Reason` | `WVARCHAR` | 100 | Yes |
