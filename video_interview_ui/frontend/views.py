from django.urls import reverse
import requests
from django.shortcuts import render, redirect
from django.conf import settings

BACKEND_API_URL = "http://127.0.0.1:8000/api"

def index(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        position_id = request.POST.get("position")

        if not fullname or not email or not position_id:
            return render(request, "frontend/index.html", {"error": "All fields are required!"})

        # Step 1: Check if applicant already exists
        existing_applicants = requests.get(f"{BACKEND_API_URL}/applicants/?email={email}&position={position_id}").json()

        if existing_applicants:
            # If an applicant exists, use their ID
            applicant_id = existing_applicants[0].get("id")
            return redirect(reverse("video_interview", kwargs={"applicant_id": applicant_id}))

        # Step 2: Create a new applicant if they don't exist
        response = requests.post(
            f"{BACKEND_API_URL}/applicants/",
            json={"fullname": fullname, "email": email, "position": position_id},
        )

        if response.status_code == 201:
            applicant_data = response.json()
            applicant_id = applicant_data.get("id")

            if applicant_id:
                return redirect(reverse("video_interview", kwargs={"applicant_id": applicant_id}))

    # Fetch positions from backend API
    positions = requests.get(f"{BACKEND_API_URL}/positions/").json()
    return render(request, "frontend/index.html", {"positions": positions})

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