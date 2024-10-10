import sys
import os
import argparse
import csv
import json
import random
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import PyPDF2

class JobScheduler:
    def __init__(self):
        load_dotenv()
        self.settings = self.load_settings()
        self.configure_gemini()
        self.candidates = self.load_candidates()
        self.current_index = 0

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                return json.load(f)
        return {
            "gemini_api_key": os.getenv('GEMINI_API_KEY', ''),
            "max_candidates": int(os.getenv('MAX_CANDIDATES', 10)),
            "hireability_threshold": float(os.getenv('HIREABILITY_THRESHOLD', 0.7))
        }

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=2)

    def configure_gemini(self):
        configure(api_key=self.settings['gemini_api_key'])
        self.model = GenerativeModel('gemini-pro')

    def load_candidates(self):
        candidates = []
        if os.path.exists('candidates.csv'):
            with open('candidates.csv', 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'resume_path' in row:
                        row['resume'] = self.extract_text_from_pdf(row['resume_path'])
                    else:
                        row['resume'] = ''
                        row['resume_path'] = ''
                    candidates.append(row)
        return candidates

    def save_candidates(self):
        with open('candidates.csv', 'w', newline='') as f:
            fieldnames = ['name', 'age', 'resume_path', 'hireability_score', 'other_roles']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for candidate in self.candidates:
                row = {k: v for k, v in candidate.items() if k in fieldnames}
                if 'resume_path' not in row:
                    row['resume_path'] = ''
                writer.writerow(row)

    def add_candidate(self, name, age, resume_path):
        resume_text = self.extract_text_from_pdf(resume_path)
        self.candidates.append({
            'name': name,
            'age': age,
            'resume': resume_text,
            'resume_path': resume_path,
            'hireability_score': '',
            'other_roles': ''
        })
        self.save_candidates()
        print(f"Added {name} to the candidates list.")

    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file, strict=False)
                text = ""
                for page in reader.pages:
                    try:
                        text += page.extract_text() + "\n"
                    except Exception as e:
                        print(f"Warning: Could not extract text from a page in {pdf_path}: {e}")
                return text.strip()
        except Exception as e:
            print(f"Warning: Could not read PDF file {pdf_path}: {e}")
            return f"[Error reading PDF: {pdf_path}]"

    def process_next_candidate(self):
        if self.current_index < len(self.candidates):
            candidate = self.candidates[self.current_index]
            
            prompt = f"""
            Analyze the following candidate information:
            Name: {candidate['name']}
            Age: {candidate['age']}
            Resume: {candidate['resume']}

            Please provide:
            1. A summary of the candidate's key qualities (5 bullet points)
            2. A hireability score on a scale of 1-10 (as a single number)
            3. Three other potential roles this candidate might be suitable for (comma-separated)
            
            Format your response as follows:
            Key Qualities:
            • Quality 1
            • Quality 2
            • Quality 3
            • Quality 4
            • Quality 5

            Hireability Score: X

            Other Potential Roles: Role 1, Role 2, Role 3
            """
            
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            # Extract hireability score and other roles from the analysis
            hireability_score = None
            other_roles = []
            
            for line in analysis.split('\n'):
                if line.startswith("Hireability Score:"):
                    try:
                        hireability_score = float(line.split(":")[1].strip())
                    except ValueError:
                        hireability_score = 0
                elif line.startswith("Other Potential Roles:"):
                    other_roles = [role.strip() for role in line.split(":")[1].split(",")]
            
            if not other_roles:
                other_roles = ['N/A']
            
            candidate['hireability_score'] = hireability_score
            candidate['other_roles'] = ', '.join(other_roles)
            
            self.current_index += 1
            return candidate, analysis
        else:
            return None, "No more candidates to process."

    def shortlist_candidate(self, candidate):
        if candidate:
            shortlist_file = 'shortlisted.csv'
            file_exists = os.path.isfile(shortlist_file)
            
            with open(shortlist_file, 'a', newline='') as f:
                fieldnames = ['name', 'age', 'resume_path', 'hireability_score', 'other_roles']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                row = {k: v for k, v in candidate.items() if k in fieldnames}
                writer.writerow(row)
            
            return f"Candidate {candidate['name']} has been shortlisted."
        return "No candidate to shortlist."

    def skip_candidate(self):
        if self.current_index > 0:
            del self.candidates[self.current_index - 1]
            self.current_index -= 1
            self.save_candidates()
            return 'Moved to next candidate.'
        return 'No candidate to skip.'

    def fill_dummy_data(self, num_candidates=10):
        dummy_names = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Lee", "Ethan Hunt", 
                       "Fiona Green", "George White", "Hannah Black", "Ian Gray", "Julia Red"]
        dummy_resume_paths = [
            "resumes/software_engineering.pdf",
            "resumes/marketing_specialist.pdf",
            "resumes/financial_analyst.pdf",
            "resumes/hr_professional.pdf",
            "resumes/project_manager.pdf",
        ]

        self.candidates = []
        for i in range(num_candidates):
            resume_path = random.choice(dummy_resume_paths)
            self.candidates.append({
                'name': random.choice(dummy_names),
                'age': random.randint(22, 55),
                'resume': self.extract_text_from_pdf(resume_path),
                'resume_path': resume_path,
                'hireability_score': '',
                'other_roles': ''
            })
        
        self.save_candidates()
        print(f"Added {num_candidates} dummy candidates to the CSV file.")

    def show_settings(self):
        print("\nCurrent Settings:")
        for key, value in self.settings.items():
            print(f"{key}: {value}")

def main():
    parser = argparse.ArgumentParser(description="Job Scheduler CLI")
    parser.add_argument('action', choices=['process', 'add', 'fill_dummy', 'show_settings'], help='Action to perform')
    parser.add_argument('--name', help='Candidate name (for add action)')
    parser.add_argument('--age', type=int, help='Candidate age (for add action)')
    parser.add_argument('--resume', help='Path to resume PDF (for add action)')
    parser.add_argument('--num', type=int, default=10, help='Number of dummy candidates to add (for fill_dummy action)')

    args = parser.parse_args()

    scheduler = JobScheduler()

    if args.action == 'process':
        while True:
            candidate, analysis = scheduler.process_next_candidate()
            if not candidate:
                print("No more candidates to process.")
                break
            
            print(f"\nCandidate: {candidate['name']}, Age: {candidate['age']}")
            print(f"Analysis:\n{analysis}")
            
            choice = input("Enter 's' to shortlist, 'n' for next, or 'q' to quit: ").lower()
            if choice == 's':
                print(scheduler.shortlist_candidate(candidate))
            elif choice == 'q':
                break
            # 'n' or any other input will move to the next candidate

    elif args.action == 'add':
        if args.name and args.age and args.resume:
            scheduler.add_candidate(args.name, args.age, args.resume)
        else:
            print("Error: Name, age, and resume path are required for adding a candidate.")

    elif args.action == 'fill_dummy':
        scheduler.fill_dummy_data(args.num)

    elif args.action == 'show_settings':
        scheduler.show_settings()

if __name__ == "__main__":
    main()