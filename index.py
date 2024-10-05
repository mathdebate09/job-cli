import argparse
import queue
import json
import os
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv

class JobScheduler:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.candidates = queue.Queue()
        self.settings = self.load_settings()
        self.configure_gemini()

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

    def add_candidate(self, name):
        if self.candidates.qsize() < self.settings['max_candidates']:
            self.candidates.put(name)
            print(f"Added {name} to the queue.")
        else:
            print("Queue is full. Cannot add more candidates.")

    def process_next_candidate(self):
        if not self.candidates.empty():
            candidate = self.candidates.get()
            print(f"Processing candidate: {candidate}")
            
            prompt = f"Generate 5 bullet points summarizing the key qualities of a job candidate named {candidate}."
            response = self.model.generate_content(prompt)
            bullet_points = response.text
            
            hireability_score = len(bullet_points) / 100  # Simplified scoring
            
            print("\nCandidate Summary:")
            print(bullet_points)
            print(f"\nHireability Score: {hireability_score:.2f}")
            
            if hireability_score >= self.settings['hireability_threshold']:
                print("Recommendation: Consider hiring")
            else:
                print("Recommendation: May need further evaluation")
        else:
            print("No more candidates in the queue.")

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

def main():
    parser = argparse.ArgumentParser(description="Job Scheduler Terminal Tool")
    parser.add_argument("action", choices=["add", "process", "settings"], help="Action to perform")
    parser.add_argument("--name", help="Candidate name (required for 'add' action)")
    parser.add_argument("--setting", help="Setting to change (required for 'settings' action)")
    parser.add_argument("--value", help="New value for setting (required for 'settings' action)")
    
    args = parser.parse_args()
    
    scheduler = JobScheduler()
    
    if args.action == "add":
        if args.name:
            scheduler.add_candidate(args.name)
        else:
            print("Error: --name is required for 'add' action")
    elif args.action == "process":
        scheduler.process_next_candidate()
    elif args.action == "settings":
        if args.setting and args.value:
            scheduler.change_setting(args.setting, args.value)
        elif args.setting == "show":
            scheduler.show_settings()
        else:
            print("Error: --setting and --value are required for 'settings' action")

if __name__ == "__main__":
    main()