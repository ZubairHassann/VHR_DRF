from django.db import models

class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Applicant(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="applicants")

    def __str__(self):
        return self.fullname

class Question(models.Model):
    text = models.TextField()
    positions = models.ManyToManyField(Position, related_name="questions")

    def __str__(self):
        return self.text[:50]

class ApplicantResponse(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="responses")
    video_response = models.FileField(upload_to="videos/")
    submission_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.applicant.fullname} - {self.question.text[:30]}"
