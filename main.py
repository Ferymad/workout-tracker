import requests
import datetime
import os
from dotenv import load_dotenv

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

# Print environment variables to verify they are loaded correctly
print(f"APP_ID: {APP_ID}")
print(f"API_KEY: {API_KEY}")
print(f"SHEETY_AUTH_TOKEN: {SHEETY_AUTH_TOKEN}")

# Constants for user information
GENDER = "male"  # or "female"
WEIGHT_KG = 82
HEIGHT_CM = 178
AGE = 27

# Function to get valid user input
def get_user_input(prompt, input_type=str):
    while True:
        try:
            user_input = input_type(input(prompt))
            return user_input
        except ValueError:
            print("Invalid input. Please try again.")

# Ask user for input
user_input = get_user_input("What have you done as an exercise? ")

# For weightlifting, ask for sets and reps
is_weightlifting = get_user_input("Is this a weightlifting exercise? (yes/no): ").lower() == 'yes'
sets = reps = 0
if is_weightlifting:
    sets = get_user_input("How many sets did you do? ", int)
    reps = get_user_input("How many reps per set? ", int)

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
    print(f"Error making request to Nutritionix API: {e}")
    exit(1)

# Print the API response
print("API Response:")
for exercise in response_data.get('exercises', []):
    print(f"Exercise: {exercise.get('name', 'Unknown').title()}")
    print(f"Duration: {exercise.get('duration_min', 0)} minutes")
    print(f"Calories burned: {exercise.get('nf_calories', 0)}")
    if is_weightlifting:
        print(f"Sets: {sets}")
        print(f"Reps per set: {reps}")
    print("---")

    # Sheety API
    sheety_post_endpoint = "https://api.sheety.co/c01075e79bfdfd87c65c728685dc04f2/selman`sWorkouts/sheet1"

    sheety_headers = {
        "Authorization": f"Bearer {SHEETY_AUTH_TOKEN}"
    }

    sheety_params = {
        "sheet1": {
            "date": datetime.datetime.now().strftime("%d/%m/%Y"),
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "exercise": exercise.get('name', 'Unknown').title(),
            "duration": exercise.get('duration_min', 0),
            "calories": exercise.get('nf_calories', 0),
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
        print("Successfully added exercise to the sheet.")
        print(sheety_post_response.text)
    except requests.RequestException as e:
        print(f"Error making request to Sheety API: {e}")
