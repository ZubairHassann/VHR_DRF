from django.contrib import admin
from .models import Interview, Applicant, Position, Question, ApplicantResponse
from django.utils.html import format_html

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_applicants_count', 'get_active_interviews')
    search_fields = ('name',)

    def get_applicants_count(self, obj):
        return obj.applicants.count()
    get_applicants_count.short_description = 'Total Applicants'

    def get_active_interviews(self, obj):
        return obj.applicants.filter(status='Pending').count()
    get_active_interviews.short_description = 'Active Interviews'


class InterviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'scheduled_date')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('title', 'description')
    actions = ['accept_interview', 'reject_interview']

    def accept_interview(self, request, queryset):
        queryset.update(status='accepted')
    accept_interview.short_description = "Accept selected interviews"

    def reject_interview(self, request, queryset):
        queryset.update(status='rejected')
    reject_interview.short_description = "Reject selected interviews"

class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'email', 'status')
    list_filter = ('status',)
    search_fields = ('fullname', 'email')
    actions = ['accept_applicant', 'reject_applicant']

    def accept_applicant(self, request, queryset):
        queryset.update(status='accepted')
    accept_applicant.short_description = "Accept selected applicants"

    def reject_applicant(self, request, queryset):
        queryset.update(status='rejected')
    reject_applicant.short_description = "Reject selected applicants"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'time_limit', 'get_positions')
    filter_horizontal = ('positions',)
    search_fields = ('text',)

    def get_positions(self, obj):
        return ", ".join([p.name for p in obj.positions.all()])
    get_positions.short_description = 'Positions'

@admin.register(ApplicantResponse)
class ApplicantResponseAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'question', 'submission_time', 'score', 'get_video_player')
    list_filter = ('score', 'submission_time', 'applicant__position')
    search_fields = ('applicant__fullname', 'applicant__email')
    actions = ['mark_accepted', 'mark_rejected']

    def get_video_player(self, obj):
        if obj.video_response:
            return format_html(
                '<video width="200" controls><source src="{}" type="video/webm">Your browser does not support the video tag.</video>',
                obj.video_response.url
            )
        return "No video uploaded"
    get_video_player.short_description = 'Video Response'

    def mark_accepted(self, request, queryset):
        queryset.update(score=10)  # Example of marking as accepted with a score of 10
    mark_accepted.short_description = "Mark selected responses as Accepted"

    def mark_rejected(self, request, queryset):
        queryset.update(score=0)  # Example of marking as rejected with a score of 0
    mark_rejected.short_description = "Mark selected responses as Rejected"

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
        
admin.site.register(Interview, InterviewAdmin)
admin.site.register(Applicant, ApplicantAdmin)