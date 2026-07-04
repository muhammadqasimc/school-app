import pyodbc
import os

mdb_path = "KISMET SECONDARY 2026  JAN (1).mdb"
abs_path = os.path.abspath(mdb_path)
password = "Sit@dbe"

conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + abs_path + ';'
    r'PWD=' + password + ';'
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

learner_id = 1043

print("=" * 80)
print(f"COMPREHENSIVE FILTER TEST FOR LEARNER {learner_id}")
print("=" * 80)

# Test 1: Get available years
print("\n1. TESTING YEAR FILTER")
print("-" * 80)
years_query = """
    SELECT DISTINCT rm.Datayear
    FROM ReportMarks rm
    WHERE rm.LearnerID = ? AND rm.Datayear IS NOT NULL
    ORDER BY rm.Datayear DESC
"""
years_result = cursor.execute(years_query, (learner_id,)).fetchall()
years = [str(row[0]) for row in years_result]
print(f"Available Years: {years}")
if not years:
    print("ERROR: No years found for this learner!")
    conn.close()
    exit(1)

# Test 2: Get available grades from LearnerPromotion
print("\n2. TESTING GRADE FILTER")
print("-" * 80)
grades_query = """
    SELECT lp.Grade 
    FROM LearnerPromotion lp
    WHERE lp.LearnerId = ? AND lp.Grade IS NOT NULL
    GROUP BY lp.Grade
    ORDER BY lp.Grade DESC
"""
grades_result = cursor.execute(grades_query, (learner_id,)).fetchall()
grades = [str(row[0]) for row in grades_result]
print(f"Available Grades: {grades}")
if not grades:
    print("WARNING: No grades found in LearnerPromotion!")

# Test 3: Get available terms
print("\n3. TESTING TERM FILTER")
print("-" * 80)
terms_query = """
    SELECT rc.CycleId, rc.Name, rc.CycleNo, rc.Term, rc.Datayear
    FROM ReportCycles rc, ReportMarks rm
    WHERE rc.CycleId = rm.ReportId AND rm.LearnerID = ?
    GROUP BY rc.CycleId, rc.Name, rc.CycleNo, rc.Term, rc.Datayear
    ORDER BY rc.Datayear DESC, rc.Term ASC
"""
terms_result = cursor.execute(terms_query, (learner_id,)).fetchall()
terms = []
seen_term_nums = set()
for row in terms_result:
    cycle_id, name, cycle_no, term_num, year = row
    if term_num and term_num not in seen_term_nums and len(terms) < 4:
        seen_term_nums.add(term_num)
        terms.append({
            'cycleId': cycle_id,
            'name': name,
            'term': term_num,
            'year': str(year) if year else None
        })
terms.sort(key=lambda x: x['term'])
print(f"Available Terms: {terms}")

# Test 4: Get available subjects
print("\n4. TESTING SUBJECT FILTER")
print("-" * 80)
subjects_query = """
    SELECT s.Name
    FROM ReportMarks rm, Subjects s
    WHERE rm.SubjectId = s.Id AND rm.LearnerID = ?
    GROUP BY s.Name
    ORDER BY s.Name
"""
subjects_result = cursor.execute(subjects_query, (learner_id,)).fetchall()
import re
subjects = []
seen_subjects = set()
for row in subjects_result:
    subject_name = row[0]
    cleaned = re.sub(r'\s*\(Gr\s+\d+\)\s*$', '', subject_name).strip()
    if cleaned and cleaned not in seen_subjects:
        seen_subjects.add(cleaned)
        subjects.append({'original': subject_name, 'cleaned': cleaned})
print(f"Available Subjects ({len(subjects)}):")
for subj in subjects[:10]:  # Show first 10
    print(f"  - {subj['cleaned']} (original: {subj['original']})")

# Test 5: Test each year individually
print("\n5. TESTING EACH YEAR INDIVIDUALLY")
print("-" * 80)
for year in years:
    print(f"\n  Testing Year: {year}")
    query = """
        SELECT 
            rm.Datayear,
            COUNT(*) as RecordCount
        FROM ReportMarks rm, Subjects s, ReportCycles rc
        WHERE rm.SubjectId = s.Id 
            AND rm.ReportId = rc.CycleId
            AND rm.LearnerID = ?
            AND rm.Datayear = ?
        GROUP BY rm.Datayear
    """
    # Get distinct counts separately
    term_count_query = """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT rm.ReportId
            FROM ReportMarks rm
            WHERE rm.LearnerID = ? AND rm.Datayear = ?
        )
    """
    subject_count_query = """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT rm.SubjectId
            FROM ReportMarks rm
            WHERE rm.LearnerID = ? AND rm.Datayear = ?
        )
    """
    result = cursor.execute(query, (learner_id, year)).fetchone()
    term_count = 0
    subject_count = 0
    try:
        term_result = cursor.execute(term_count_query, (learner_id, year)).fetchone()
        term_count = term_result[0] if term_result else 0
    except:
        pass
    try:
        subject_result = cursor.execute(subject_count_query, (learner_id, year)).fetchone()
        subject_count = subject_result[0] if subject_result else 0
    except:
        pass
    
    if result:
        print(f"    Records: {result[1]}, Terms: {term_count}, Subjects: {subject_count}")
    else:
        print(f"    ERROR: No data found for year {year}")

# Test 6: Test each grade individually
print("\n6. TESTING EACH GRADE INDIVIDUALLY")
print("-" * 80)
if grades:
    for grade in grades:
        print(f"\n  Testing Grade: {grade}")
        query = """
            SELECT COUNT(*) as RecordCount
            FROM ReportMarks rm, Subjects s, ReportCycles rc
            WHERE rm.SubjectId = s.Id 
                AND rm.ReportId = rc.CycleId
                AND rm.LearnerID = ?
                AND EXISTS (SELECT 1 FROM LearnerPromotion lp WHERE lp.LearnerId = ? AND lp.Grade = ? AND lp.Datayear = rm.Datayear)
        """
        result = cursor.execute(query, (learner_id, learner_id, grade)).fetchone()
        # Get distinct counts separately
        year_count_query = """
            SELECT COUNT(*) FROM (
                SELECT DISTINCT rm.Datayear
                FROM ReportMarks rm
                WHERE rm.LearnerID = ?
                    AND EXISTS (SELECT 1 FROM LearnerPromotion lp WHERE lp.LearnerId = ? AND lp.Grade = ? AND lp.Datayear = rm.Datayear)
            )
        """
        term_count_query = """
            SELECT COUNT(*) FROM (
                SELECT DISTINCT rm.ReportId
                FROM ReportMarks rm
                WHERE rm.LearnerID = ?
                    AND EXISTS (SELECT 1 FROM LearnerPromotion lp WHERE lp.LearnerId = ? AND lp.Grade = ? AND lp.Datayear = rm.Datayear)
            )
        """
        year_count = 0
        term_count = 0
        try:
            year_result = cursor.execute(year_count_query, (learner_id, learner_id, grade)).fetchone()
            year_count = year_result[0] if year_result else 0
        except:
            pass
        try:
            term_result = cursor.execute(term_count_query, (learner_id, learner_id, grade)).fetchone()
            term_count = term_result[0] if term_result else 0
        except:
            pass
        
        if result:
            print(f"    Records: {result[0]}, Years: {year_count}, Terms: {term_count}")
        else:
            print(f"    WARNING: No data found for grade {grade}")
else:
    print("  SKIPPED: No grades found in LearnerSubjects")

# Test 7: Test each term individually
print("\n7. TESTING EACH TERM INDIVIDUALLY")
print("-" * 80)
for term_info in terms:
    cycle_id = term_info['cycleId']
    term_num = term_info['term']
    print(f"\n  Testing Term {term_num} (CycleId: {cycle_id})")
    query = """
        SELECT COUNT(*) as RecordCount, rm.Datayear
        FROM ReportMarks rm, Subjects s, ReportCycles rc
        WHERE rm.SubjectId = s.Id 
            AND rm.ReportId = rc.CycleId
            AND rm.LearnerID = ?
            AND rm.ReportId = ?
        GROUP BY rm.Datayear
    """
    result = cursor.execute(query, (learner_id, cycle_id)).fetchone()
    subject_count_query = """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT rm.SubjectId
            FROM ReportMarks rm
            WHERE rm.LearnerID = ? AND rm.ReportId = ?
        )
    """
    subject_count = 0
    try:
        subj_result = cursor.execute(subject_count_query, (learner_id, cycle_id)).fetchone()
        subject_count = subj_result[0] if subj_result else 0
    except:
        pass
    
    if result:
        print(f"    Records: {result[0]}, Subjects: {subject_count}, Year: {result[1]}")
    else:
        print(f"    ERROR: No data found for term {term_num}")

# Test 8: Test each subject individually
print("\n8. TESTING EACH SUBJECT INDIVIDUALLY")
print("-" * 80)
for subj in subjects[:5]:  # Test first 5 subjects
    cleaned_subj = subj['cleaned']
    print(f"\n  Testing Subject: {cleaned_subj}")
    query = """
        SELECT COUNT(*) as RecordCount
        FROM ReportMarks rm, Subjects s
        WHERE rm.SubjectId = s.Id 
            AND rm.LearnerID = ?
            AND (s.Name = ? OR s.Name LIKE ?)
    """
    result = cursor.execute(query, (learner_id, cleaned_subj, f"{cleaned_subj}%")).fetchone()
    # Get distinct counts separately
    year_count_query = """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT rm.Datayear
            FROM ReportMarks rm, Subjects s
            WHERE rm.SubjectId = s.Id 
                AND rm.LearnerID = ? AND (s.Name = ? OR s.Name LIKE ?)
        )
    """
    term_count_query = """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT rm.ReportId
            FROM ReportMarks rm, Subjects s
            WHERE rm.SubjectId = s.Id 
                AND rm.LearnerID = ? AND (s.Name = ? OR s.Name LIKE ?)
        )
    """
    year_count = 0
    term_count = 0
    try:
        year_result = cursor.execute(year_count_query, (learner_id, cleaned_subj, f"{cleaned_subj}%")).fetchone()
        year_count = year_result[0] if year_result else 0
    except:
        pass
    try:
        term_result = cursor.execute(term_count_query, (learner_id, cleaned_subj, f"{cleaned_subj}%")).fetchone()
        term_count = term_result[0] if term_result else 0
    except:
        pass
    
    if result:
        print(f"    Records: {result[0]}, Years: {year_count}, Terms: {term_count}")
    else:
        print(f"    ERROR: No data found for subject {cleaned_subj}")

# Test 9: Test year + grade combination
print("\n9. TESTING YEAR + GRADE COMBINATIONS")
print("-" * 80)
for year in years[:3]:  # Test first 3 years
    # Get grade for this year from LearnerPromotion
    grade_query = """
        SELECT TOP 1 lp.Grade
        FROM LearnerPromotion lp
        WHERE lp.LearnerId = ? AND lp.Datayear = ? AND lp.Grade IS NOT NULL
        ORDER BY lp.Grade DESC
    """
    grade_result = cursor.execute(grade_query, (learner_id, year)).fetchone()
    if grade_result and grades:
        grade = grade_result[0]
        print(f"\n  Testing Year: {year}, Grade: {grade}")
        query = """
            SELECT COUNT(*) as RecordCount
            FROM ReportMarks rm, Subjects s, ReportCycles rc
            WHERE rm.SubjectId = s.Id 
                AND rm.ReportId = rc.CycleId
                AND rm.LearnerID = ?
                AND rm.Datayear = ?
                AND EXISTS (SELECT 1 FROM LearnerPromotion lp WHERE lp.LearnerId = ? AND lp.Grade = ? AND lp.Datayear = rm.Datayear)
        """
        result = cursor.execute(query, (learner_id, year, learner_id, grade)).fetchone()
        if result:
            print(f"    Records: {result[0]}")
        else:
            print(f"    WARNING: No data found")

# Test 10: Test year + term combination
print("\n10. TESTING YEAR + TERM COMBINATIONS")
print("-" * 80)
for year in years[:2]:  # Test first 2 years
    # Get terms for this year
    year_terms = [t for t in terms if t['year'] == year]
    if year_terms:
        for term_info in year_terms[:2]:  # Test first 2 terms per year
            cycle_id = term_info['cycleId']
            term_num = term_info['term']
            print(f"\n  Testing Year: {year}, Term: {term_num}")
            query = """
                SELECT COUNT(*) as RecordCount
                FROM ReportMarks rm, Subjects s, ReportCycles rc
                WHERE rm.SubjectId = s.Id 
                    AND rm.ReportId = rc.CycleId
                    AND rm.LearnerID = ?
                    AND rm.Datayear = ?
                    AND rm.ReportId = ?
            """
            result = cursor.execute(query, (learner_id, year, cycle_id)).fetchone()
            if result:
                print(f"    Records: {result[0]}")
            else:
                print(f"    ERROR: No data found")

# Test 11: Test all filters combined
print("\n11. TESTING ALL FILTERS COMBINED")
print("-" * 80)
if years and terms and subjects:
    year = years[0]
    term_info = terms[0]
    subject = subjects[0]['cleaned']
    cycle_id = term_info['cycleId']
    
    # Get grade for year
    grade_query = """
        SELECT TOP 1 ls.Grade
        FROM LearnerSubjects ls
        WHERE ls.LearnerId = ? AND ls.Grade IS NOT NULL
        ORDER BY ls.ID DESC
    """
    grade_result = cursor.execute(grade_query, (learner_id,)).fetchone()
    grade = grade_result[0] if grade_result else None
    
    print(f"\n  Testing ALL FILTERS:")
    print(f"    Year: {year}")
    print(f"    Grade: {grade}")
    print(f"    Term: {term_info['term']} (CycleId: {cycle_id})")
    print(f"    Subject: {subject}")
    
    if grade:
        query = """
            SELECT 
                rm.Mark,
                rm.TotalMark,
                s.Name AS Subject,
                rm.Datayear,
                rc.Term
            FROM ReportMarks rm, Subjects s, ReportCycles rc
            WHERE rm.SubjectId = s.Id 
                AND rm.ReportId = rc.CycleId
                AND rm.LearnerID = ?
                AND rm.Datayear = ?
                AND EXISTS (SELECT 1 FROM LearnerPromotion lp WHERE lp.LearnerId = ? AND lp.Grade = ? AND lp.Datayear = rm.Datayear)
                AND rm.ReportId = ?
                AND (s.Name = ? OR s.Name LIKE ?)
        """
        result = cursor.execute(query, (learner_id, year, learner_id, grade, cycle_id, subject, f"{subject}%")).fetchall()
        print(f"    Records Found: {len(result)}")
        if result:
            for row in result[:3]:  # Show first 3
                print(f"      - {row[2]}: {row[0]}/{row[1]} ({row[4]})")
        else:
            print(f"    ERROR: No data found with all filters")
    else:
        print(f"    SKIPPED: No grade available")

# Test 12: Verify year-grade linking
print("\n12. VERIFYING YEAR-GRADE LINKING")
print("-" * 80)
for year in years:
    # Try to get grade for this specific year from LearnerPromotion
    year_grade_query = """
        SELECT DISTINCT lp.Grade, lp.Datayear
        FROM LearnerPromotion lp
        WHERE lp.LearnerId = ? AND lp.Datayear = ? AND lp.Grade IS NOT NULL
    """
    year_grade_result = cursor.execute(year_grade_query, (learner_id, year)).fetchall()
    if year_grade_result:
        print(f"  Year {year}: Grades found: {[str(r[0]) for r in year_grade_result]}")
    else:
        print(f"  Year {year}: No grade found in LearnerPromotion with Datayear")
        # Fallback: get latest grade
        fallback_query = """
            SELECT TOP 1 lp.Grade
            FROM LearnerPromotion lp
            WHERE lp.LearnerId = ? AND lp.Grade IS NOT NULL
            ORDER BY lp.Datayear DESC, lp.Grade DESC
        """
        fallback_result = cursor.execute(fallback_query, (learner_id,)).fetchone()
        if fallback_result:
            print(f"    Fallback grade: {fallback_result[0]}")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Years available: {len(years)}")
print(f"Grades available: {len(grades)}")
print(f"Terms available: {len(terms)}")
print(f"Subjects available: {len(subjects)}")
print("\nAll tests completed!")

conn.close()
