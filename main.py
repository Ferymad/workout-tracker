import requests
import datetime
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, simpledialog

# Load environment variables from .env file
load_dotenv()

# Set environment variables if not already set
os.environ.setdefault("APP_ID", "e88f2635")
os.environ.setdefault("API_KEY", "6e0dc579a4f0a52546f533cdad2bc00a")
os.environ.setdefault("SHEETY_AUTH_TOKEN", "e79bfdfd87c65c72868")

# Get environment variables
APP_ID = os.environ.get("APP_ID")
API_KEY = os.environ.get("API_KEY")
SHEETY_AUTH_TOKEN = os.environ.get("SHEETY_AUTH_TOKEN")

# Constants for user information
GENDER = "male"  # or "female"
WEIGHT_KG = 82
HEIGHT_CM = 178
AGE = 27

class ExerciseTrackerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Exercise Tracker")

        self.label = tk.Label(master, text="What have you done as an exercise?")
        self.label.pack()

        self.exercise_entry = tk.Entry(master)
        self.exercise_entry.pack()

        self.is_weightlifting_var = tk.BooleanVar()
        self.weightlifting_check = tk.Checkbutton(master, text="Is this a weightlifting exercise?", variable=self.is_weightlifting_var)
        self.weightlifting_check.pack()

        self.submit_button = tk.Button(master, text="Submit", command=self.submit_exercise)
        self.submit_button.pack()

    def submit_exercise(self):
        user_input = self.exercise_entry.get()
        is_weightlifting = self.is_weightlifting_var.get()

        sets = reps = 0
        if is_weightlifting:
            sets = simpledialog.askinteger("Input", "How many sets did you do?", parent=self.master)
            reps = simpledialog.askinteger("Input", "How many reps per set?", parent=self.master)

        # Make API request to Nutritionix
        try:
            my_request = requests.post(
                "https://trackapi.nutritionix.com/v2/natural/exercise",
                headers={
                    "x-app-id": APP_ID,
                    "x-app-key": API_KEY
                },
                json={
                    "query": user_input,
                    "gender": GENDER,
                    "weight_kg": WEIGHT_KG,
                    "height_cm": HEIGHT_CM,
                    "age": AGE
                }
            )
            my_request.raise_for_status()  # Raise an exception for bad status codes
            response_data = my_request.json()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Error making request to Nutritionix API: {e}")
            return

        # Process the API response
        for exercise in response_data.get('exercises', []):
            exercise_name = exercise.get('name', 'Unknown').title()
            duration = exercise.get('duration_min', 0)
            calories = exercise.get('nf_calories', 0)

            # Sheety API
            sheety_post_endpoint = "https://api.sheety.co/c01075e79bfdfd87c65c728685dc04f2/selman`sWorkouts/sheet1"

            sheety_headers = {
                "Authorization": f"Bearer {SHEETY_AUTH_TOKEN}"
            }

            sheety_params = {
                "sheet1": {
                    "date": datetime.datetime.now().strftime("%d/%m/%Y"),
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "exercise": exercise_name,
                    "duration": duration,
                    "calories": calories,
                    "sets": sets if is_weightlifting else None,
                    "reps": reps if is_weightlifting else None
                }
            }

            # Make request to Sheety API
            try:
                sheety_post_response = requests.post(
                    sheety_post_endpoint,
                    json=sheety_params,
                    headers=sheety_headers
                )
                sheety_post_response.raise_for_status()  # Raise an exception for bad status codes
                messagebox.showinfo("Success", f"Successfully added exercise to the sheet:\n\nExercise: {exercise_name}\nDuration: {duration} minutes\nCalories burned: {calories}")
            except requests.RequestException as e:
                messagebox.showerror("Error", f"Error making request to Sheety API: {e}")

# Create and run the GUI
root = tk.Tk()
app = ExerciseTrackerGUI(root)
root.mainloop()
