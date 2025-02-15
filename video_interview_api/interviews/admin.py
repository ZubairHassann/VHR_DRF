from django.contrib import admin
from .models import Applicant, Position, Question, ApplicantResponse

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ("fullname", "email", "position")

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text",)

@admin.register(ApplicantResponse)
class ApplicantResponseAdmin(admin.ModelAdmin):
    list_display = ("applicant", "question", "status")
    list_filter = ("status",)
    actions = ["mark_accepted", "mark_rejected"]

    def mark_accepted(self, request, queryset):
        queryset.update(status="Accepted")
    mark_accepted.short_description = "Mark selected responses as Accepted"

    def mark_rejected(self, request, queryset):
        queryset.update(status="Rejected")
    mark_rejected.short_description = "Mark selected responses as Rejected"
