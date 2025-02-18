from django.urls import reverse
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .decorators import login_required_custom

BACKEND_API_URL = "http://127.0.0.1:8000/api"

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "frontend/register.html", {"error": "Username already exists."})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect(reverse("login"))

    return render(request, "frontend/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse("dashboard"))
        else:
            return render(request, "frontend/login.html", {"error": "Invalid username or password."})

    return render(request, "frontend/login.html")

def logout_view(request):
    logout(request)
    return redirect(reverse("index"))

@login_required_custom
def dashboard(request):
    user_email = request.user.email
    response = requests.get(f"{BACKEND_API_URL}/applicants/?email={user_email}")

    if response.status_code == 200:
        applicants = response.json()
    else:
        applicants = []

    return render(request, "frontend/dashboard.html", {"applicants": applicants})

@login_required_custom
def interviews(request):
    user_email = request.user.email
    response = requests.get(f"{BACKEND_API_URL}/applicants/?email={user_email}")

    if response.status_code == 200:
        applicants = response.json()
    else:
        applicants = []

    return render(request, "frontend/interviews.html", {"applicants": applicants})

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