from django.contrib import admin
from .models import Task, UploadedFile

class UploadedFileInline(admin.TabularInline):
    model = UploadedFile
    extra = 1  # Number of empty file input fields to display

class TaskAdmin(admin.ModelAdmin):
    inlines = [UploadedFileInline]

admin.site.register(Task, TaskAdmin)



