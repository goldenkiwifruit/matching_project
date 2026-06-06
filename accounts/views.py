from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile
from .forms import SignupForm
from .models import ProfileImage
from django.contrib import messages

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            role = request.POST.get("role")
            user.profile.role = role
            user.profile.save()

            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})

@login_required
def edit_profile(request):
    profile = request.user.profile

    images = profile.images.filter(
        image__isnull=False
    ).exclude(image="").order_by("order")

    images_count = images.count()
    index = int(request.GET.get("i", 0))

    if images_count > 0:
        index = index % images_count
        current_img = images[index]
    else:
        current_img = None

    # フォーム
    form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "form": form,
        "images": images,
        "current_img": current_img,
        "index": index,
        "images_count": images_count,
    })

@login_required
def manage_profile_images(request):
    profile = request.user.profile
    MAX_IMAGES = 5

    if request.method == "POST" and request.FILES.get("image"):
        if profile.images.count() >= MAX_IMAGES:
            messages.error(request, "画像は最大5枚までです")
            return redirect("manage_profile_images")

        ProfileImage.objects.create(
            profile=profile,
            image=request.FILES["image"]
        )
        return redirect("manage_profile_images")

    images = list(profile.images.order_by("id"))
    slots = images + [None] * (MAX_IMAGES - len(images))

    return render(request, "accounts/manage_images.html", {
        "slots": slots,
    })

@login_required
def delete_profile_image(request, image_id):
    img = get_object_or_404(
        ProfileImage,
        id=image_id,
        profile=request.user.profile  # ← セキュリティ
    )
    img.delete()
    return redirect("manage_profile_images")

@login_required
def home(request):
    if request.user.profile.role == "company":
        return redirect("user_list")
    else:
        return redirect("job_list")