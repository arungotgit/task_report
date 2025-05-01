from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.timezone import now
from .models import Task, UploadedFile
from datetime import datetime

def card_list(request):
    # Get only non-archived cards
    cards = Task.objects.filter(is_archived=False).order_by('-created_at')

    # Implement search filter logic
    query = request.GET.get('q', '')  # Text search for title
    post_type = request.GET.get('post_type', '')  # Filter by post type
    start_date = request.GET.get('start_date', '')  # Filter by start date
    end_date = request.GET.get('end_date', '')  # Filter by end date

    # Apply filters
    if query:
        cards = cards.filter(title__icontains=query)
    if post_type:   
        cards = cards.filter(post_type__iexact=post_type)
    if start_date and end_date:
        cards = cards.filter(created_at__range=[start_date, end_date])

    # Add pagination
    paginator = Paginator(cards, 6)  # Show 6 cards per page
    page = request.GET.get('page')
    try:
        paginated_cards = paginator.page(page)
    except PageNotAnInteger:
        paginated_cards = paginator.page(1)  # Deliver first page if page is not an integer
    except EmptyPage:
        paginated_cards = paginator.page(paginator.num_pages)  # Deliver last page if out of range

    context = {
        'cards': paginated_cards,
        'query': query,
        'post_type': post_type,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'card_list.html', context)


def archive_list(request):
    # Get only archived cards
    archived_cards = Task.objects.filter(is_archived=True).order_by('-created_at')

    # Add pagination
    paginator = Paginator(archived_cards, 6)  # Show 6 cards per page
    page = request.GET.get('page')
    try:
        paginated_cards = paginator.page(page)
    except PageNotAnInteger:
        paginated_cards = paginator.page(1)
    except EmptyPage:
        paginated_cards = paginator.page(paginator.num_pages)

    context = {'cards': paginated_cards}
    return render(request, 'archive_list.html', context)

@login_required
def add_card(request):
    if request.method == "POST":
        serial_number = Task.objects.count() + 1  # Auto-assign serial number
        post_type = request.POST.get("post_type")
        title = request.POST.get("title")
        status = request.POST.get("status")
        last_date = request.POST.get("last_date")
        file = request.FILES.get("file")  # File from the form

        # Validate required fields
        if post_type and title and status:
            task = Task.objects.create(
                serial_number=serial_number,
                post_type=post_type,
                title=title,
                status=status,
                last_date=last_date,
                author=request.user
            )

            # Save the uploaded file to UploadedFile model
            if file:
                UploadedFile.objects.create(
                    task=task,  # Link to the Task object
                    file=file
                )
            messages.success(request, 'Card added successfully!')
            return redirect('card_list')
            
        

    return render(request, 'add_card.html')



@login_required
def edit_card(request, card_id):
    card = get_object_or_404(Task, id=card_id, author=request.user)
    if request.method == 'POST':
        # Update basic fields
        card.title = request.POST.get('title')
        card.post_type = request.POST.get('post_type')
        card.status = request.POST.get('status')
        last_date = request.POST.get('last_date')
        card.last_date = datetime.strptime(last_date, '%Y-%m-%d').date() if last_date else None

        # Delete selected files
        delete_files = request.POST.getlist('delete_files')  # Get IDs of files to delete
        if delete_files:
            UploadedFile.objects.filter(id__in=delete_files).delete()  # Remove files

        # Upload new files
        new_files = request.FILES.getlist('new_files')  # Handle multiple new files
        for new_file in new_files:
            UploadedFile.objects.create(task=card, file=new_file)

        card.save()  # Save all changes
        messages.success(request, 'Card updated successfully!')
        return redirect('card_list') if not card.is_archived else redirect('archive')
    return render(request, 'edit_card.html', {'card': card})


@login_required
def delete_card(request, card_id):
    card = get_object_or_404(Task, id=card_id, author=request.user)
    if request.method == 'POST':
        card.delete()
        messages.success(request, 'Card deleted successfully!')
        return redirect('card_list') if not card.is_archived else redirect('archive_list')
    return render(request, 'confirm_delete.html', {'card': card})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'card_list')  # Get next parameter or default
            return redirect(next_url)
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('card_list')