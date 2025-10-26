import csv
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


# class

class_order = ["JSS1", "JSS2", "JSS3", "SS1"]
students_data = {cls: {} for cls in class_order}



# CSV 

def calculate_scores(student):
    """Calculate Test Total and Total Grade"""
    test_total = (student["test1"] + student["test2"]) / 2
    total_grade = (test_total + student["exam"]) / 2
    student["test_total"] = test_total
    student["total_grade"] = total_grade
    return student


def save_results_to_csv(data, filename="student_results.csv"):
    """Save all student results to CSV file"""
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Class", "Subject", "Student Name",
            "Test1", "Test2", "Test Total",
            "Exam", "Total Grade", "Class Average"
        ])
        for cls, subjects in data.items():
            for subj, results in subjects.items():
                if not results:
                    continue
                grades = [calculate_scores(student)["total_grade"] for student in results]
                class_avg = sum(grades) / len(grades)
                for student in results:
                    writer.writerow([
                        cls, subj, student["name"],
                        student["test1"], student["test2"], f"{student['test_total']:.2f}",
                        student["exam"], f"{student['total_grade']:.2f}",
                        f"{class_avg:.2f}"
                    ])


def load_results_from_csv(filename="student_results.csv"):
    """Load results from CSV if file exists"""
    try:
        with open(filename, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    cls = row["Class"].strip()
                    subj = row["Subject"].strip().title()
                    name = row["Student Name"].strip().title()
                    test1 = float(row["Test1"])
                    test2 = float(row["Test2"])
                    exam = float(row["Exam"])

                    if cls in students_data:
                        students_data[cls].setdefault(subj, [])
                        students_data[cls][subj].append({
                            "name": name,
                            "test1": test1,
                            "test2": test2,
                            "exam": exam
                        })
                except (KeyError, ValueError):
                    # Skip bad rows silently
                    continue
    except FileNotFoundError:
        pass



# operation

def delete_student(cls, subj, name):
    """Delete student record by name"""
    if cls in students_data and subj in students_data[cls]:
        before = len(students_data[cls][subj])
        students_data[cls][subj] = [
            s for s in students_data[cls][subj] if s["name"].lower() != name.lower()
        ]
        after = len(students_data[cls][subj])
        if before != after:
            save_results_to_csv(students_data)
            return True
    return False


def update_student(cls, subj, name, test1, test2, exam):
    """Update an existing student record"""
    if cls in students_data and subj in students_data[cls]:
        for student in students_data[cls][subj]:
            if student["name"].lower() == name.lower():
                student["test1"] = test1
                student["test2"] = test2
                student["exam"] = exam
                save_results_to_csv(students_data)
                return True
    return False



# web_interface

class StudentHandler(BaseHTTPRequestHandler):
    def _send_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            self.show_students()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(length).decode("utf-8")
        data = parse_qs(post_data)

        if self.path == "/add":
            cls = data.get("class", [""])[0].strip()
            subj = data.get("subject", [""])[0].strip().title()
            name = data.get("name", [""])[0].strip().title()

            # Ensure numeric inputs are valid
            try:
                test1 = float(data.get("test1", [0])[0])
                test2 = float(data.get("test2", [0])[0])
                exam = float(data.get("exam", [0])[0])
            except ValueError:
                self.send_error(400, "Invalid numeric input")
                return

            if cls in class_order and subj:
                students_data[cls].setdefault(subj, [])
                students_data[cls][subj].append({
                    "name": name,
                    "test1": test1,
                    "test2": test2,
                    "exam": exam
                })
                save_results_to_csv(students_data)

        elif self.path == "/delete":
            cls = data.get("class", [""])[0]
            subj = data.get("subject", [""])[0]
            name = data.get("name", [""])[0]
            delete_student(cls, subj, name)

        elif self.path == "/update":
            cls = data.get("class", [""])[0]
            subj = data.get("subject", [""])[0]
            name = data.get("name", [""])[0]
            try:
                test1 = float(data.get("test1", [0])[0])
                test2 = float(data.get("test2", [0])[0])
                exam = float(data.get("exam", [0])[0])
            except ValueError:
                self.send_error(400, "Invalid numeric input")
                return
            update_student(cls, subj, name, test1, test2, exam)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def show_students(self):
        html = """
        <html>
        <head>
        <title>Student Results</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background: #333; color: #fff; }
            form { margin: 5px 0; }
            input, select { margin: 3px; padding: 5px; }
            .delete-btn { color: red; }
            .update-btn { color: green; }
        </style>
        </head><body>
        <h2>Student Records</h2>
        """

        for cls in class_order:
            if not students_data[cls]:
                continue
            for subj, results in students_data[cls].items():
                if results:
                    grades = [calculate_scores(student)["total_grade"] for student in results]
                    class_avg = sum(grades) / len(grades)

                    html += f"<h3>{cls} - {subj} (Class Avg: {class_avg:.2f})</h3>"
                    html += "<table><tr><th>Name</th><th>Test1</th><th>Test2</th><th>Test Total</th><th>Exam</th><th>Total Grade</th><th>Actions</th></tr>"
                    for student in results:
                        html += f"""
                        <tr>
                            <td>{student['name']}</td>
                            <td>{student['test1']}</td>
                            <td>{student['test2']}</td>
                            <td>{student['test_total']:.2f}</td>
                            <td>{student['exam']}</td>
                            <td>{student['total_grade']:.2f}</td>
                            <td>
                                <form method="POST" action="/delete" style="display:inline;">
                                    <input type="hidden" name="class" value="{cls}">
                                    <input type="hidden" name="subject" value="{subj}">
                                    <input type="hidden" name="name" value="{student['name']}">
                                    <input type="submit" value="Delete" class="delete-btn">
                                </form>
                                <form method="POST" action="/update" style="display:inline;">
                                    <input type="hidden" name="class" value="{cls}">
                                    <input type="hidden" name="subject" value="{subj}">
                                    <input type="hidden" name="name" value="{student['name']}">
                                    <input type="number" step="any" name="test1" value="{student['test1']}" required>
                                    <input type="number" step="any" name="test2" value="{student['test2']}" required>
                                    <input type="number" step="any" name="exam" value="{student['exam']}" required>
                                    <input type="submit" value="Update" class="update-btn">
                                </form>
                            </td>
                        </tr>
                        """
                    html += "</table>"

        # Add Student Form
        html += """
        <h2>Add Student</h2>
        <form method="POST" action="/add">
            <select name="class">
        """
        for cls in class_order:
            html += f"<option>{cls}</option>"
        html += "</select>"

        # Text input for subject
        html += """
            <input type="text" name="subject" placeholder="Enter Subject" required>
            <input type="text" name="name" placeholder="Student Name" required>
            <input type="number" step="any" name="test1" placeholder="Test1" required>
            <input type="number" step="any" name="test2" placeholder="Test2" required>
            <input type="number" step="any" name="exam" placeholder="Exam" required>
            <input type="submit" value="Add Student">
        </form>
        </body></html>
        """

        self._send_html(html)



#  SERVER

if __name__ == "__main__":
    load_results_from_csv()
    print("Server running at: http://localhost:8000")
    server = HTTPServer(("localhost", 8000), StudentHandler)
    server.serve_forever()
