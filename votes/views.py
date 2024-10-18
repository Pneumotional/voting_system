from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Code, Category, Candidate, Vote
from django.db.models import Count
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from datetime import timedelta
import uuid

# Function to validate voting codes
def validate_code(request, code):
    try:
        voter_code = Code.objects.get(code=code)
        if voter_code.is_valid():
            return voter_code
        elif voter_code.is_used:
            messages.error(request, "This code has already been used.")
        else:
            messages.error(request, "This code has expired.")
    except Code.DoesNotExist:
        messages.error(request, "Code Doesn't Exist")
    return None

# View for entering the code to start the voting process
def vote_page(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        voter_code = validate_code(request, code)
        if voter_code:
            # Proceed to the voting form page if code is valid
            categories = Category.objects.all()
            return render(request, 'votes/vote.html', {'categories': categories, 'voter_code': voter_code})
    return render(request, 'votes/enter_code.html')

# View for submitting the vote
def submit_vote(request, code_id):
    if request.method == 'POST':
        voter_code = Code.objects.get(id=code_id)
        categories = Category.objects.all()

        # Check if the voter has already voted
        if Vote.objects.filter(voter_code=voter_code).exists():
            messages.error(request, "You have already voted.")
            return redirect('vote_page')

        # Collect votes
        votes = []
        for category in categories:
            candidate_id = request.POST.get(f'category_{category.id}')
            if candidate_id:
                candidate = Candidate.objects.get(id=candidate_id)
                votes.append(Vote(voter_code=voter_code, candidate=candidate))

        # Ensure a vote is cast in all categories
        if len(votes) == len(categories):
            Vote.objects.bulk_create(votes)
            voter_code.is_used = True
            voter_code.save()
            messages.success(request, "Vote submitted successfully.")
        else:
            messages.error(request, "You must vote in all categories.")
    
    return redirect('vote_page')

# View for generating voting codes
def generate_code(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            code_count = int(request.POST.get('code_count'))
            hours_until_expiry = int(request.POST.get('expiry_hours'))
            for _ in range(code_count):
                Code.objects.create(
                    code=str(uuid.uuid4())[:5],
                    expires_at=timezone.now() + timedelta(hours=hours_until_expiry)
                )
            messages.success(request, f'{code_count} codes generated successfully.')
        return render(request, 'votes/generate_code.html')
    else:
        return redirect('login')

# View for displaying voting results
def results_page(request):
    # Get all categories with their candidates
    categories = Category.objects.prefetch_related('candidates')

    # Prepare the data structure for results
    results = {}
    for category in categories:
        results[category.name] = {}
        for candidate in category.candidates.all():  # Use the correct related name here
            vote_count = Vote.objects.filter(candidate=candidate).count()  # Count votes for each candidate
            results[category.name][candidate.name] = vote_count
            
    # chart_data = []
    # for category in categories:
    #     candidates_data = {
    #         'category': category.name,
    #         'labels': [],
    #         'data': []
    #     }
    #     for candidate in category.candidates.all():
    #         vote_count = Vote.objects.filter(candidate=candidate).count()
    #         candidates_data['labels'].append(candidate.name)
    #         candidates_data['data'].append(vote_count)
    #     chart_data.append(candidates_data)


    context = {
        'results': results,
        # 'chart_data': chart_data,
    }
    return render(request, 'votes/results.html', context)

# View for user login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('generate_code')  # Redirect to a page after login
    else:
        form = AuthenticationForm()
    return render(request, 'votes/login.html', {'form': form})


##PDF amd Excel Export
import openpyxl
from django.http import HttpResponse

def export_to_excel(request):
    categories = Category.objects.prefetch_related('candidates')

    # Create a workbook and add a worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Voting Results"

    # Add headers
    ws.append(['Category', 'Candidate', 'Votes'])

    # Loop through each category and candidate, adding data to Excel
    for category in categories:
        for candidate in category.candidates.all():
            vote_count = Vote.objects.filter(candidate=candidate).count()
            ws.append([category.name, candidate.name, vote_count])

    # Prepare the response as an Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=voting_results.xlsx'
    
    # Save the workbook to the response
    wb.save(response)

    return response

def export_generated_codes_to_excel(request):
    codes = Code.objects.all()  # Adjust this to your actual model name

    # Create a workbook and add a worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Generated Codes"

    # Add headers
    ws.append(['Code', 'Expiry Time'])

    # Loop through each generated code and add data to Excel
    for code in codes:
        expiry_time = code.expires_at.replace(tzinfo=None) if code.expires_at else None
        ws.append([code.code, expiry_time]) 

    # Prepare the response as an Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=generated_codes.xlsx'
    
    # Save the workbook to the response
    wb.save(response)

    return response


from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_to_pdf(request):
    categories = Category.objects.prefetch_related('candidates')

    # Create a new PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="voting_results.pdf"'

    # Create a canvas for the PDF
    p = canvas.Canvas(response)

    # Set starting coordinates for the PDF
    x = 100
    y = 800

    p.setFont("Helvetica-Bold", 16)
    p.drawString(x, y, "Voting Results")
    y -= 30

    # Loop through each category and candidate, adding them to the PDF
    p.setFont("Helvetica", 12)
    for category in categories:
        p.drawString(x, y, f"Category: {category.name}")
        y -= 20

        for candidate in category.candidates.all():
            vote_count = Vote.objects.filter(candidate=candidate).count()
            p.drawString(x + 20, y, f"Candidate: {candidate.name} - Votes: {vote_count}")
            y -= 20

        y -= 10  # Extra space between categories

    # Save the PDF
    p.showPage()
    p.save()

    return response

def export_generated_codes_to_pdf(request):
    codes = Code.objects.all()  # Adjust this to your actual model name

    # Create a new PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="generated_codes.pdf"'

    # Create a canvas for the PDF
    p = canvas.Canvas(response)

    # Set starting coordinates for the PDF
    x = 100
    y = 800

    p.setFont("Helvetica-Bold", 16)
    p.drawString(x, y, "Generated Codes")
    y -= 30

    # Loop through each generated code, adding them to the PDF
    p.setFont("Helvetica", 12)
    for code in codes:
        p.drawString(x, y, f"Code: {code.code} - Expiry Time: {code.expires_at}")  # Adjust fields accordingly
        y -= 20

    # Save the PDF
    p.showPage()
    p.save()

    return response




