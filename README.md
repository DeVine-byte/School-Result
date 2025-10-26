# Student Results Management Web App

A simple web-based application to manage student test and exam results. This application allows you to **add, update, delete, and view student results** for multiple classes and subjects. All data is stored in a CSV file for persistence.

---

## Features

- Add new student records with test and exam scores.
- Update existing student scores.
- Delete student records.
- View all student results organized by class and subject.
- Calculate **Test Total** and **Total Grade** for each student.
- Automatically calculate and display **Class Average** for each subject.
- Persistent storage in a CSV file (`student_results.csv`).

---

## Classes Supported

- JSS1
- JSS2
- JSS3
- SS1

---

## How It Works

1. **Data Structure**:  
   - `students_data` dictionary stores student records per class and subject.
   - Each student record contains:
     - Name
     - Test1 score
     - Test2 score
     - Exam score
     - Test Total (calculated)
     - Total Grade (calculated)

2. **CSV Storage**:
   - The results are saved to `student_results.csv`.
   - Existing CSV data is loaded automatically when the app starts.

3. **Web Interface**:
   - Accessible at `http://localhost:8000`.
   - Provides a table view of students with forms to:
     - Add a student
     - Update student scores
     - Delete a student

4. **Score Calculation**:
   ```text
   Test Total = (Test1 + Test2) / 2
   Total Grade = (Test Total + Exam) / 2
   Class Average = Average of Total Grades for the class and subject
