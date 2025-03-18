import requests
from django.urls import reverse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .decorators import login_required_custom
from django.contrib.auth.decorators import login_required
from requests.exceptions import RequestException
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from config import settings

BACKEND_API_URL = "http://vhr-backend-bff6bd-546829-65-108-245-140.traefik.me/api"
# BACKEND_API_URL = "http://127.0.0.1:8000/api"

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
            return redirect(reverse("interviews"))
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


@login_required
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


@login_required
def video_interview(request, applicant_id=None):
    email = request.GET.get('email')
    position = request.GET.get('position')
    name = request.GET.get('name')

    if applicant_id:
        # Fetch applicant details from backend
        applicant_response = requests.get(f"{BACKEND_API_URL}/applicants/{applicant_id}/")
        
        if applicant_response.status_code != 200:
            return redirect(reverse("index"))  # Redirect if applicant not found

        applicant = applicant_response.json()
        position_id = applicant.get("position")
    else:
        if not email or not position or not name:
            return redirect(reverse("index"))

        # Check if applicant already exists (for the SAME email and position)
        existing_applicants_response = requests.get(f"{BACKEND_API_URL}/applicants/?email={email}&position={position}")
        existing_applicants_response.raise_for_status()
        existing_applicants = existing_applicants_response.json()

        if existing_applicants:
            applicant_id = existing_applicants[0]['id']
        else:
            # Create a new applicant if they don't exist
            response = requests.post(
                f"{BACKEND_API_URL}/applicants/",
                json={"fullname": name, "email": email, "position": position},
            )
            response.raise_for_status()
            applicant_data = response.json()
            applicant_id = applicant_data.get("id")

        applicant = {
            "fullname": name,
            "email": email,
            "position": position,
        }
        position_id = position

    # Fetch questions based on position
    questions_response = requests.get(f"{BACKEND_API_URL}/questions/?position={position_id}")
    questions = questions_response.json() if questions_response.status_code == 200 else []

    return render(request, "frontend/video_interview.html", {
        "applicant_id": applicant_id,
        "applicant_name": applicant.get("fullname"),
        "applicant_email": applicant.get("email"),
        "questions": questions,
    })

@login_required
def interviews(request):
    user_email = request.user.email
    try:
        # Fetch applicants
        applicants_response = requests.get(f"{BACKEND_API_URL}/applicants/")
        applicants_response.raise_for_status()
        applicants = applicants_response.json()

        # Fetch positions
        positions_response = requests.get(f"{BACKEND_API_URL}/positions/")
        positions_response.raise_for_status()
        positions = positions_response.json()

        # Fetch responses
        responses_response = requests.get(f"{BACKEND_API_URL}/applicant-responses/")
        responses_response.raise_for_status()
        responses = responses_response.json()

        # Filter applicants based on the current user's email
        user_applicants = [applicant for applicant in applicants if applicant['email'] == user_email]

        # Calculate counts
        selected_count = len([a for a in user_applicants if a['status'] == 'Selected'])
        pending_count = len([a for a in user_applicants if a['status'] == 'Pending'])
        rejected_count = len([a for a in user_applicants if a['status'] == 'Rejected'])
        total_count = len(user_applicants)

        # Add position details and response details to each applicant
        for applicant in user_applicants:
            applicant['total_questions'] = applicant.get('total_questions', 0)
            applicant['total_score'] = sum(response['score'] if response['score'] is not None else 0 
                                         for response in responses 
                                         if response['applicant'] == applicant['id'])
            applicant['response_date'] = next((response.get('created_at') 
                                             for response in responses 
                                             if response['applicant'] == applicant['id']), None)
            applicant['position_id'] = applicant.get('position', None)
            applicant['position_details'] = next((position for position in positions 
                                                if position['id'] == applicant['position']), None)

        context = {
            "applicants": user_applicants,
            "user_email": user_email,
            "user_fullname": request.user.get_full_name(),
            "selected_count": selected_count,
            "pending_count": pending_count,
            "rejected_count": rejected_count,
            "total_count": total_count
        }

    except RequestException as e:
        print(f"Network error: {e}")
        context = {
            "applicants": [],
            "user_email": user_email,
            "user_fullname": request.user.get_full_name(),
            "selected_count": 0,
            "pending_count": 0,
            "total_count": 0,
            "error": "Network error occurred while fetching data."
        }
    except ValueError as e:
        print(f"JSON decode error: {e}")
        context = {
            "applicants": [],
            "user_email": user_email,
            "user_fullname": request.user.get_full_name(),
            "selected_count": 0,
            "pending_count": 0,
            "total_count": 0,
            "error": "Error processing data from server."
        }

    return render(request, "frontend/interviews.html", context)



@login_required
def view_applicant_responses(request, email, position_id):
    try:
        # Fetch applicant responses
        responses_response = requests.get(f"{BACKEND_API_URL}/applicant-responses/?email={email}&position={position_id}")
        responses_response.raise_for_status()
        responses = responses_response.json()

        # Fetch questions for the specific position
        questions_response = requests.get(f"{BACKEND_API_URL}/questions/?position={position_id}")
        questions_response.raise_for_status()
        questions = questions_response.json()

        # Add question details to each response and filter out responses without questions
        for response in responses:
            response['question_details'] = next((question for question in questions if question['id'] == response['question']), None)

        # Filter out responses without question details
        responses = [response for response in responses if response['question_details']]

        # Sort responses by question order (if available)
        responses.sort(key=lambda x: x['question_details'].get('order', 0))

        # Calculate total score and total questions
        total_score = sum(response['score'] if response['score'] is not None else 0 for response in responses)
        total_questions = len(questions)

    except RequestException as e:
        print(f"Network error: {e}")
        responses = []
        total_score = 0
        total_questions = 0
    except ValueError as e:
        print(f"JSON decode error: {e}")
        responses = []
        total_score = 0
        total_questions = 0

    return render(request, "frontend/view_applicant_responses.html", {
        "responses": responses,
        "position_id": position_id,
        "total_score": total_score,
        "total_questions": total_questions
    })


@login_required
def interview_from_link(request):
    email = request.GET.get('email')
    position = request.GET.get('position')
    name = request.GET.get('name')

    if not email or not position or not name:
        return redirect(reverse("index"))

    try:
        # Check if applicant already exists (for the SAME email and position)
        existing_applicants_response = requests.get(f"{BACKEND_API_URL}/applicants/?email={email}&position={position}")
        existing_applicants_response.raise_for_status()
        existing_applicants = existing_applicants_response.json()

        if existing_applicants:
            applicant_id = existing_applicants[0]['id']
        else:
            # Create a new applicant if they don't exist
            response = requests.post(
                f"{BACKEND_API_URL}/applicants/",
                json={"fullname": name, "email": email, "position": position},
            )
            response.raise_for_status()
            applicant_data = response.json()
            applicant_id = applicant_data.get("id")

        return redirect(reverse("video_interview", kwargs={"applicant_id": applicant_id}))

    except RequestException as e:
        print(f"Network error: {e}")
        return redirect(reverse("index"))
    except ValueError as e:
        print(f"JSON decode error: {e}")
        return redirect(reverse("index"))


@login_required
def available_jobs(request):
    response = requests.get(f"{BACKEND_API_URL}/positions/")
    if response.status_code == 200:
        positions = response.json()
    else:
        positions = []
    return render(request, 'frontend/available_jobs.html', {'positions': positions})

@require_http_methods(["POST"])
@login_required
def apply_job(request, position_id):
    response = requests.post(
        f"{BACKEND_API_URL}/positions/{position_id}/apply/",
        headers={'Authorization': f'Token {request.user.auth_token.key}'}
    )
    if response.status_code == 201:
        messages.success(request, 'You have successfully applied for the job')
    else:
        messages.error(request, 'Failed to apply for the job')
    return redirect('available_jobs')