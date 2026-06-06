from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import ProfileImage
from .models import Message, Job, Application, Contract, Review
from django.db.models import Count, Q, F, Avg
from django.contrib import messages

# Create your views here.
@login_required
def user_list(request):
    users = User.objects.filter(profile__role="worker").exclude(id=request.user.id)
    for user in users:
        user.avg_rating = Review.objects.filter(
            reviewee=user
        ).aggregate(
            Avg("rating")
        )["rating__avg"]

    return render(request, "matching/list.html",{"users": users})

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    from_page = request.GET.get("from")
    job_id = request.GET.get("job_id")

    # 実ファイルがある画像だけ取得
    images = ProfileImage.objects.filter(
        profile=profile,
        image__isnull=False
    ).exclude(image="")

    images_count = images.count()

    index = int(request.GET.get("i", 0))

    if images_count > 0:
        index = index % images_count
        img = images[index]
    else:
        img = None

    reviews = Review.objects.filter(
        reviewee=user
    ).order_by("-created_at")

    avg_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    review_count = reviews.count()

    return render(request, "matching/user_detail.html", {
        "target": user,
        "img": img,
        "index": index,
        "images_count": images_count,
        "from_page": from_page,
        "job_id": job_id,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "review_count": review_count
    })

@login_required
def job_list(request):
    status = request.GET.get("status", "open")

    jobs = Job.objects.annotate(
                application_count=Count("application"),
                accepted_count=Count("application",filter=Q(application__status="accepted"))
            )\
        .order_by("-created_at")
    
    if request.user.profile.role == "company":
        jobs = jobs.filter(client=request.user)
    
    open_jobs = jobs.filter(accepted_count__lt=F("max_workers"))
    closed_jobs = jobs.filter(accepted_count__gte=F("max_workers"))

    open_count = open_jobs.count()
    closed_count = closed_jobs.count()
    
    if status == "closed":
        jobs = closed_jobs
    else:
        jobs = open_jobs
    
    if request.user.profile.role == "worker":
        applied_jobs = Application.objects.filter(user=request.user)
        applied_job_ids = list(applied_jobs.values_list("job_id", flat=True))
    else:
        applied_job_ids = []
        
    return render(request, "matching/job_list.html", {
        "jobs": jobs,
        "status": status,
        "applied_job_ids": applied_job_ids,
        "open_count": open_count,
        "closed_count": closed_count,
    })

@login_required
def create_job(request):
    if request.user.profile.role != "company":
        return redirect("job_list")
    
    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        reward = request.POST.get("reward")


        if title and description and reward:
            Job.objects.create(
                title=title,
                description=description,
                reward=reward,
                max_workers=request.POST.get("max_workers", 1),
                client=request.user
            )
            return redirect("job_list")

    return render(request, "matching/create_job.html")

@login_required
def apply_job(request, job_id):
    if request.user.profile.role != "worker":
        print("role:", request.user.profile.role)
        return redirect("job_list")
    
    job = get_object_or_404(Job, id=job_id)

    Application.objects.get_or_create(
        job=job,
        user=request.user
    )
    return redirect("job_detail", job_id=job.id)

@login_required
def accept_application(request, app_id):
    app = get_object_or_404(Application, id=app_id)

    if request.user != app.job.client:
        return redirect("job_list")
    
    accepted_count = Application.objects.filter(
        job=app.job,
        status="accepted"
    ).count()

    if accepted_count >= app.job.max_workers:
        messages.error(request, "採用上限に達しています")
        return redirect("job_applications", job_id=app.job.id)
    
    app.status = "accepted"
    app.save()

    Contract.objects.create(
        job=app.job,
        worker=app.user,
        client=app.job.client,
        status="active"
    )

    return redirect("job_applications", job_id=app.job.id)

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    from_page = request.GET.get("from")

    #応募済みチェック
    is_applied = Application.objects.filter(
        job=job,
        user=request.user
    ).exists()

    return render(request, "matching/job_detail.html",{
        "job": job,
        "is_applied": is_applied,
        "from_page": from_page
    })

@login_required
def my_applications(request):
    applications = Application.objects.filter(
        user=request.user
    ).select_related("job").order_by("-id")

    return render(request, "matching/my_applications.html", {
        "applications": applications
    })

@login_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.user != job.client:
        return redirect("job_list")
    
    applications = Application.objects.filter(job=job)

    contracts = Contract.objects.filter(job=job)

    return render(request, "matching/job_applications.html", {
        "job": job,
        "applications": applications,
        "contracts": contracts
    })

@login_required
def contract_list(request):
    contracts = Contract.objects.filter(
        Q(worker=request.user) | Q(client=request.user)
    ).annotate(
        unread_count=Count(
            "message",
            filter=Q(message__is_read=False) & ~Q(message__sender=request.user)
        )
    )

    for contract in contracts:

        contract.review_exists = Review.objects.filter(
            contract=contract,
            reviewer=request.user
        ).exists()
    
    return render(request, "matching/contract_list.html", {
        "contracts": contracts
    })

@login_required
def contract_chat(request,contract_id):
    contract = get_object_or_404(Contract, id=contract_id)

    if request.user not in [contract.worker, contract.client]:
        return redirect("contract_list")
    
    if request.method == "POST":

        if contract.status != "active":
            return redirect(
                "contract_chat",
                contract_id=contract.id
            )
        
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                contract=contract,
                sender=request.user,
                content=content
            )
    
    messages = Message.objects.filter(
        contract=contract,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    messages = Message.objects.filter(contract=contract).order_by('created_at')

    return render(request, "matching/contract_chat.html", {
        "contract": contract,
        "messages": messages
    })

@login_required
def contract_complete(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)

    if request.user != contract.client:
        return redirect("cotract_list")
    
    contract.status = "completed"
    contract.save()

    return redirect("contract_list")

@login_required
def create_review(request, contract_id):

    contract = get_object_or_404(
        Contract,
        id=contract_id
    )
    
    if contract.status != "completed":
        return redirect("contract_list")
    
    if Review.objects.filter(
        contract=contract,
        reviewer=request.user
        ).exists():
        return redirect("contract_list")
    
    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if request.user == contract.client:
            reviewee = contract.worker
        else:
            reviewee = contract.client

        Review.objects.create(
            contract=contract,
            reviewer=request.user,
            reviewee=reviewee,
            rating=rating,
            comment=comment
        )

        return redirect("contract_list")
    
    return render(
        request,
        "matching/create_review.html",
        {"contract": contract}
    )

@login_required
def review_list(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    reviews = Review.objects.filter(
        reviewee=user
    ).order_by("-created_at")

    return render(
        request,
        "matching/review_list.html",
        {
            "target": user,
            "reviews": reviews
        }
    )