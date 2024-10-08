import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import csv
import json
import random
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import PySimpleGUI as sg

class JobScheduler:
    def __init__(self):
        load_dotenv()
        self.settings = self.load_settings()
        self.configure_gemini()
        self.candidates = self.load_candidates()
        self.current_index = 0
        self.current_candidate = None
        self.current_analysis = None

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
                candidates = list(reader)
        return candidates

    def save_candidates(self):
        with open('candidates.csv', 'w', newline='') as f:
            fieldnames = ['name', 'age', 'resume', 'hireability_score', 'other_roles']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.candidates)

    def add_candidate(self, name, age, resume):
        self.candidates.append({
            'name': name,
            'age': age,
            'resume': resume,
            'hireability_score': '',
            'other_roles': ''
        })
        self.save_candidates()
        print(f"Added {name} to the candidates list.")

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
            
            self.current_candidate = candidate
            self.current_analysis = analysis
            self.current_index += 1
            return candidate, analysis
        else:
            self.current_candidate = None
            self.current_analysis = None
            return None, "No more candidates to process."

    def shortlist_candidate(self):
        if self.current_candidate:
            shortlist_file = 'shortlisted.csv'
            file_exists = os.path.isfile(shortlist_file)
            
            with open(shortlist_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'age', 'resume', 'hireability_score', 'other_roles'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow(self.current_candidate)
            
            return f"Candidate {self.current_candidate['name']} has been shortlisted."
        return "No candidate to shortlist."

    def skip_candidate(self):
        if self.current_index > 0:
            del self.candidates[self.current_index - 1]
            self.current_index -= 1
            self.save_candidates()
            return 'Moved to next candidate.'
        return 'No candidate to skip.'

    def change_setting(self, setting, value):
        if setting in self.settings:
            self.settings[setting] = value
            self.save_settings()
            self.configure_gemini()
            print(f"Updated {setting} to {value}")
        else:
            print(f"Invalid setting: {setting}")

    def show_settings(self):
        print("\nCurrent Settings:")
        for key, value in self.settings.items():
            print(f"{key}: {value}")

    def fill_dummy_data(self, num_candidates=10):
        dummy_names = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Lee", "Ethan Hunt", 
                       "Fiona Green", "George White", "Hannah Black", "Ian Gray", "Julia Red"]
        dummy_resumes = [
            "Experienced software engineer with expertise in Python and machine learning.",
            "Marketing specialist with a track record of successful digital campaigns.",
            "Financial analyst with strong skills in data analysis and forecasting.",
            "Human resources professional specializing in talent acquisition and development.",
            "Project manager with PMP certification and agile methodology experience.",
            "Graphic designer proficient in Adobe Creative Suite and UI/UX design.",
            "Sales representative with a history of exceeding quotas in B2B sales.",
            "Data scientist with expertise in statistical analysis and predictive modeling.",
            "Operations manager skilled in process improvement and team leadership.",
            "Content writer with a background in SEO and digital content strategy."
        ]

        self.candidates = []
        for i in range(num_candidates):
            self.candidates.append({
                'name': random.choice(dummy_names),
                'age': random.randint(22, 55),
                'resume': random.choice(dummy_resumes),
                'hireability_score': '',
                'other_roles': ''
            })
        
        self.save_candidates()
        print(f"Added {num_candidates} dummy candidates to the CSV file.")

def create_main_window(scheduler):
    sg.theme('DarkTeal9')  # Set a professional-looking theme

    # Define custom colors
    background_color = sg.theme_background_color()
    text_color = sg.theme_text_color()
    button_color = ('white', '#007A7A')
    
    # Candidate Info Section
    candidate_info = [
        [sg.Text('Candidate Information', font=('Helvetica', 16), justification='center', expand_x=True)],
        [sg.Text('Name:', size=(10, 1)), sg.Text('', size=(30, 1), key='-NAME-')],
        [sg.Text('Age:', size=(10, 1)), sg.Text('', size=(30, 1), key='-AGE-')],
        [sg.Text('Resume:', size=(10, 1))],
        [sg.Multiline('', size=(60, 5), key='-RESUME-', disabled=True)]
    ]

    # Analysis Section
    analysis_section = [
        [sg.Text('AI Analysis', font=('Helvetica', 16), justification='center', expand_x=True)],
        [sg.Multiline('', size=(60, 15), key='-ANALYSIS-', disabled=True)]
    ]

    # Action Buttons
    action_buttons = [
        [sg.Button('Process Next', size=(15, 1), button_color=button_color),
         sg.Button('Shortlist', size=(15, 1), button_color=button_color),
         sg.Button('Skip', size=(15, 1), button_color=button_color)]
    ]

    # Main Layout
    layout = [
        [sg.Text('Job Scheduler', font=('Helvetica', 24), justification='center', expand_x=True)],
        [sg.Column(candidate_info, background_color=background_color)],
        [sg.Column(analysis_section, background_color=background_color)],
        [sg.Column(action_buttons, justification='center', expand_x=True, background_color=background_color)],
        [sg.Button('Add Candidate', size=(15, 1), button_color=button_color),
         sg.Button('Fill Dummy Data', size=(15, 1), button_color=button_color),
         sg.Button('Exit', size=(15, 1), button_color=('white', '#B22222'))]
    ]

    return sg.Window('Job Scheduler', layout, finalize=True)

def create_add_candidate_window():
    sg.theme('DarkTeal9')

    layout = [
        [sg.Text('Add New Candidate', font=('Helvetica', 16), justification='center', expand_x=True)],
        [sg.Text('Name:', size=(10, 1)), sg.Input(key='-NEW-NAME-', size=(30, 1))],
        [sg.Text('Age:', size=(10, 1)), sg.Input(key='-NEW-AGE-', size=(30, 1))],
        [sg.Text('Resume:', size=(10, 1))],
        [sg.Multiline(key='-NEW-RESUME-', size=(50, 5))],
        [sg.Button('Add', size=(10, 1)), sg.Button('Cancel', size=(10, 1))]
    ]

    return sg.Window('Add Candidate', layout, modal=True)

def main():
    scheduler = JobScheduler()
    main_window = create_main_window(scheduler)
    add_candidate_window = None

    # Process the first candidate immediately
    update_main_window(main_window, *scheduler.process_next_candidate())

    while True:
        window, event, values = sg.read_all_windows()
        
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            if window == add_candidate_window:
                add_candidate_window.close()
                add_candidate_window = None
            else:
                break

        if window == main_window:
            if event == 'Process Next':
                update_main_window(main_window, *scheduler.process_next_candidate())

            elif event == 'Shortlist':
                message = scheduler.shortlist_candidate()
                sg.popup_ok(message)
                update_main_window(main_window, *scheduler.process_next_candidate())

            elif event == 'Skip':
                message = scheduler.skip_candidate()
                sg.popup_ok(message)
                update_main_window(main_window, *scheduler.process_next_candidate())

            elif event == 'Add Candidate':
                add_candidate_window = create_add_candidate_window()

            elif event == 'Fill Dummy Data':
                scheduler.fill_dummy_data()
                sg.popup_ok('Dummy data added.')

        if window == add_candidate_window:
            if event == 'Add':
                name = values['-NEW-NAME-']
                age = values['-NEW-AGE-']
                resume = values['-NEW-RESUME-']
                if name and age and resume:
                    scheduler.add_candidate(name, age, resume)
                    sg.popup_ok(f'Added {name} to the candidates list.')
                    add_candidate_window.close()
                    add_candidate_window = None
                else:
                    sg.popup_error('Please fill in all fields.')

            elif event == 'Cancel':
                add_candidate_window.close()
                add_candidate_window = None

    if add_candidate_window:
        add_candidate_window.close()
    main_window.close()

def update_main_window(window, candidate, analysis):
    if candidate:
        window['-NAME-'].update(candidate['name'])
        window['-AGE-'].update(candidate['age'])
        window['-RESUME-'].update(candidate['resume'])
        window['-ANALYSIS-'].update(analysis)
    else:
        window['-NAME-'].update('')
        window['-AGE-'].update('')
        window['-RESUME-'].update('')
        window['-ANALYSIS-'].update('No more candidates to process.')

if __name__ == "__main__":
    main()