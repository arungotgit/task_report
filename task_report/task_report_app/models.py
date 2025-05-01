from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import datetime

class PostType(models.TextChoices):
    Advertisement = 'Advertisement'
    Circular = 'Circular'
    Result = 'Result'
    Other = 'Other'

class Status(models.TextChoices):
    Active = 'Active', 'Active'
    Inactive = 'Inactive', 'Inactive'

class Task(models.Model):
    serial_number = models.IntegerField(unique=True, blank=True, null=True)
    title = models.CharField(max_length=250)
    post_type = models.CharField(max_length=50, choices=PostType.choices, default=PostType.Advertisement)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.Active)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    last_date = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def save(self, *args, **kwargs):
        # Convert last_date to a datetime.date object, if necessary
        if isinstance(self.last_date, str):  # If last_date is a string
            self.last_date = datetime.strptime(self.last_date, '%Y-%m-%d').date()

        # Dynamically update archive status
        if self.last_date and self.last_date < now().date():
            self.is_archived = True
        else:
            self.is_archived = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.serial_number} - {self.title}"


class UploadedFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.file.name

# Signals to handle serial number adjustment
@receiver(pre_save, sender=Task)
def set_serial_number(sender, instance, **kwargs):
    if instance.serial_number is None:  # Assign serial number only if it's not set
        last_task = Task.objects.order_by('-serial_number').first()
        instance.serial_number = last_task.serial_number + 1 if last_task else 1

@receiver(post_delete, sender=Task)
def adjust_serial_numbers(sender, instance, **kwargs):
    tasks = Task.objects.order_by('serial_number')  # Order by serial number
    for index, task in enumerate(tasks, start=1):
        task.serial_number = index  # Reassign correct order
        task.save()