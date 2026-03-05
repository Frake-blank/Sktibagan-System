from django.contrib import admin
from .models import Resident, Project, SKMember, Announcement, Suggestion, ProjectReaction 


# ---------------------
# RESIDENT
# ---------------------
@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('firstname', 'lastname', 'email')


# ---------------------
# PROJECT
# ---------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'date_started', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')


# ---------------------
# SK MEMBER
# ---------------------
@admin.register(SKMember)
class SKMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('role', 'order')
    ordering = ('order',)


# ---------------------
# ANNOUNCEMENT
# ---------------------
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'content')


# ---------------------
# FEEDBACK & SUGGESTIONS
# ---------------------
@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'short_message',
        'status',
        'is_important',
        'created_at',
    )

    list_filter = ('status', 'is_important', 'created_at')
    search_fields = ('user__username', 'message')
    list_editable = ('status', 'is_important')
    ordering = ('-created_at',)

    def short_message(self, obj):
        return obj.message[:50]

    short_message.short_description = "Message"

# ---------------------
# PROJECT REACTION
# ---------------------
@admin.register(ProjectReaction)
class ProjectReactionAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'reaction')
    list_filter = ('reaction',)
    search_fields = ('project__title', 'user__username')