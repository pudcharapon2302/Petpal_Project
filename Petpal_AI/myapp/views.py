from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import User , Profile, Pet
from .forms import CustomUserCreationForm ,LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.decorators import login_required


User = get_user_model()

# Create your views here.
def Landing_Page(request):
    return render(request, 'myapp/landing.html')


def register(request):
    if request.user.is_authenticated:
        return redirect("landing")  # หน้า home

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)                 # ✅ ล็อกอินทันที
            messages.success(request, "สมัครสมาชิกสำเร็จ!")
            return redirect("landing")           # ✅ กลับหน้า home
    else:
        form = RegisterForm()

    return render(request, "myapp/registration/register.html", {"form": form})

def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or settings.LOGIN_REDIRECT_URL
    if request.user.is_authenticated:
        return redirect(next_url)

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"].strip()
            password = form.cleaned_data["password"]
            remember  = form.cleaned_data["remember"]

            # ลองด้วย username ก่อน
            user = None
            user_obj = User.objects.filter(username=identifier).first()
            if not user_obj:
                # ถ้าไม่ใช่ username ลองหาอีเมล
                user_obj = User.objects.filter(email__iexact=identifier).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                # จำฉันไว้: ไม่ติ๊ก = session หมดอายุเมื่อปิดเบราเซอร์
                if not remember:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(60 * 60 * 24 * 14)  # 14 วัน

                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, "ข้อมูลเข้าสู่ระบบไม่ถูกต้อง")
    else:
        form = LoginForm()

    return render(request, "auth/login.html", {"form": form, "next": next_url})

def logout_view(request):
    logout(request)
    messages.success(request, "ออกจากระบบแล้ว")
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def profile_page(request):
    profile = Profile.objects.get(user=request.user)
    pets = Pet.objects.filter(owner=request.user).order_by("-id")
    return render(request, "myapp/profile.html", {"profile": profile, "pets": pets})

@login_required
def profile_update(request):
    if request.method == "POST":
        p = Profile.objects.get(user=request.user)
        request.user.first_name, *rest = (request.POST.get("full_name",""),)
        request.user.save()
        p.phone   = request.POST.get("phone","")
        p.address = request.POST.get("address","")
        # ถ้าใช้ dataURL อาจต้อง decode เก็บไฟล์จริง; 
        # ถ้ามี input ชื่อ avatar จริง ๆ ให้ใช้ request.FILES["avatar"]
        p.save()
    return redirect("profile")

@login_required
def pet_create(request):
    if request.method == "POST":
        Pet.objects.create(
            owner=request.user,
            name=request.POST["name"],
            birth_date=request.POST["birth_date"],
            image=request.FILES.get("image"),  # สมมติ field เป็น ImageField
        )
    return redirect("profile")
