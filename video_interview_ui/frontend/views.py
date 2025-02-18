from django.urls import reverse
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required # For admin access control
from django.urls import reverse
import requests
from django.shortcuts import render, redirect
from django.conf import settings

BACKEND_API_URL = "http://127.0.0.1:8000/api"

def index(request):
    error_message = None  # Initialize error message

    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        position_id = request.POST.get("position")

        if not fullname or not email or not position_id:
            error_message = "All fields are required!" # Set error message
            positions = requests.get(f"{BACKEND_API_URL}/positions/").json()
            return render(request, "frontend/index.html", {"positions": positions, "error": error_message}) # Pass error

        # Step 1: Check if applicant already exists (for the SAME email and position)
        existing_applicants = requests.get(f"{BACKEND_API_URL}/applicants/?email={email}&position={position_id}").json()

        if existing_applicants:
            error_message = "You have already applied for this position." # Set specific error message
            positions = requests.get(f"{BACKEND_API_URL}/positions/").json()
            return render(request, "frontend/index.html", {"positions": positions, "error": error_message}) # Pass error

        # Step 2: Create a new applicant if they don't exist (or if no existing applicant found for SAME email AND position)
        response = requests.post(
            f"{BACKEND_API_URL}/applicants/",
            json={"fullname": fullname, "email": email, "position": position_id},
        )

        if response.status_code == 201:
            applicant_data = response.json()
            applicant_id = applicant_data.get("id")

            if applicant_id:
                return redirect(reverse("video_interview", kwargs={"applicant_id": applicant_id}))
        else:
            # Handle backend errors
            error_detail = response.json() if response.headers['content-type'] == 'application/json' else response.text
            print(f"Backend API Error creating applicant. Status Code: {response.status_code}, Detail: {error_detail}")
            error_message = f"Failed to create application. Please try again. (Error: {response.status_code})" # Generic error for user

    # Fetch positions from backend API (for GET request and for POST failures to re-render form)
    positions = requests.get(f"{BACKEND_API_URL}/positions/").json()
    return render(request, "frontend/index.html", {"positions": positions, "error": error_message}) # Pass error (can be None)

def video_interview(request, applicant_id):
    # Fetch applicant details from backend
    applicant_response = requests.get(f"{BACKEND_API_URL}/applicants/{applicant_id}/")
    
    if applicant_response.status_code != 200:
        return redirect(reverse("index"))  # Redirect if applicant not found

    applicant = applicant_response.json()
    position_id = applicant.get("position")

    # Fetch questions based on position
    questions_response = requests.get(f"{BACKEND_API_URL}/questions/?position={position_id}")
    questions = questions_response.json() if questions_response.status_code == 200 else []

    return render(request, "frontend/video_interview.html", {
        "applicant_id": applicant_id,
        "applicant_name": applicant.get("fullname"),
        "applicant_email": applicant.get("email"),
        "questions": questions,
    })