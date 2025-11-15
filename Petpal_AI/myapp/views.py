# myapp/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import NoReverseMatch
from django.views.decorators.http import require_POST
from .models import Animal, User , Profile, Pet , Post, Foundation
from .forms import CustomUserCreationForm ,LoginForm, PetForm, RegisterForm , VaccineFormSet, AllergyFormSet , PublicPostForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction



User = get_user_model()

# Create your views here.
def Landing_Page(request):
    # ... (โค้ด Landing_Page ... ถูกต้องแล้ว) ...
    posts_for_adoption = Post.objects.filter(post_type='ADOPTION', is_active = True)\
        .select_related('pet', 'pet__animal')\
        .order_by('-created_at')[:3]
    
    lost_posts = Post.objects.filter(post_type = "LOST", is_active = True)\
        .select_related('pet', 'pet__animal', 'user')\
        .order_by('-created_at')[:3]

    latest_cat_posts = Post.objects.filter(
        post_type='ADOPTION',
        is_active=True,
        pet__animal__species__iexact='CAT' 
    ).select_related('pet', 'pet__animal').order_by('-created_at')[:3]

    latest_dog_posts = Post.objects.filter(
        post_type='ADOPTION',
        is_active=True,
        pet__animal__species__iexact='DOG' 
    ).select_related('pet', 'pet__animal').order_by('-created_at')[:3]

    context = {
        'posts_for_adoption': posts_for_adoption, 
        'lost_posts': lost_posts,
        'latest_cat_posts': latest_cat_posts,     
        'latest_dog_posts': latest_dog_posts,           
    }
    return render(request, 'myapp/landing.html', context)


def register(request):
    # ... (โค้ด register ... ถูกต้องแล้ว) ...
    if request.user.is_authenticated:
        return redirect("landing")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "สมัครสมาชิกสำเร็จ!")
            return redirect("landing")
    else:
        form = RegisterForm()
    return render(request, "myapp/registration/register.html", {"form": form})

def login_view(request):
    # ... (โค้ด login_view ... ถูกต้องแล้ว) ...
    next_url = request.GET.get("next") or request.POST.get("next") or settings.LOGIN_REDIRECT_URL
    if request.user.is_authenticated:
        return redirect(next_url)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"].strip()
            password = form.cleaned_data["password"]
            remember  = form.cleaned_data["remember"]
            user = None
            user_obj = User.objects.filter(username=identifier).first()
            if not user_obj:
                user_obj = User.objects.filter(email__iexact=identifier).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(60 * 60 * 24 * 14)
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, "ข้อมูลเข้าสู่ระบบไม่ถูกต้อง")
    else:
        form = LoginForm()
    return render(request, "auth/login.html", {"form": form, "next": next_url})

def logout_view(request):
    # ... (โค้ด logout_view ... ถูกต้องแล้ว) ...
    logout(request)
    messages.success(request, "ออกจากระบบแล้ว")
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def profile_page(request):
    # ... (โค้ด profile_page ... ถูกต้องแล้ว) ...
    profile, _ = Profile.objects.get_or_create(user=request.user)
    pets = Pet.objects.filter(owner=request.user).order_by("-id")
    animals = Animal.objects.all().order_by("species", "breed")
    return render(request, "myapp/profile.html", {"profile": profile, "pets": pets, "animals": animals})

@require_POST
@login_required
def account_delete(request):
    # ... (โค้ด account_delete ... ถูกต้องแล้ว) ...
    if request.user.is_superuser:
        return redirect("profile")
    confirm = request.POST.get("confirm", "")
    if confirm != request.user.username:
        messages.error(request, "ชื่อผู้ใช้ไม่ตรงกัน")
        return redirect("profile")
    uid = request.user.id
    list(messages.get_messages(request))
    logout(request)
    with transaction.atomic():
        User.objects.filter(id=uid).delete()
    try:
        return redirect("login")
    except NoReverseMatch:
        return HttpResponseRedirect("accounts/login/")

@login_required
def profile_update(request):
    # ... (โค้ด profile_update ... ถูกต้องแล้ว) ...
    if request.method == "POST":
        profile, _ = Profile.objects.get_or_create(user=request.user)
        request.user.first_name = request.POST.get("full_name", "").strip()
        request.user.phone = request.POST.get("phone", "").strip()
        request.user.address = request.POST.get("address", "").strip()
        request.user.save()
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
        profile.save()
    return redirect("profile")

@login_required
def pet_create(request):
    # ... (โค้ด pet_create ... ถูกต้องแล้ว) ...
    if request.method == "POST":
        animal = None
        aid = request.POST.get("animal")
        if aid:
            from django.shortcuts import get_object_or_404
            animal = get_object_or_404(Animal, id=aid)
        Pet.objects.create(
            owner=request.user,
            animal=animal,
            name=request.POST.get("name", "").strip(),
            birth_date=request.POST.get("birth_date") or None,
            image=request.FILES.get("image"),
        )
    return redirect("profile")

@login_required
def pet_add(request):
    # ... (โค้ด pet_add ... ถูกต้องแล้ว) ...
    if request.method == "POST":
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            vaccines  = VaccineFormSet(request.POST, instance=pet, prefix="vaccines")
            allergies = AllergyFormSet(request.POST, instance=pet, prefix="allergies")
            if vaccines.is_valid() and allergies.is_valid():
                vaccines.save()
                allergies.save()
                messages.success(request, "บันทึกข้อมูลสัตว์เลี้ยงเรียบร้อย")
                return redirect("pet_detail", pk=pet.pk)
            pet.delete()
    else:
        form = PetForm()
        vaccines  = VaccineFormSet(prefix="vaccines")
        allergies = AllergyFormSet(prefix="allergies")
    return render(request, "myapp/pets/add.html", {
        "form": form, "vaccines": vaccines, "allergies": allergies
    })

@login_required
def pet_detail(request, pk: int):
    # ... (โค้ด pet_detail ... ถูกต้องแล้ว) ...
    pet = get_object_or_404(
        Pet.objects.select_related("animal"),
        pk=pk, owner=request.user
    )
    try:
        vaccines_qs = pet.vaccine_records.all()
    except AttributeError:
        vaccines_qs = pet.vaccine_record_set.all()
    try:
        allergies_qs = pet.allergies.all()
    except AttributeError:
        allergies_qs = pet.pet_allergy_set.all()
    context = {
        "pet": pet,
        "vaccines": vaccines_qs.order_by("-vaccinated_on", "-created_at"),
        "allergies": allergies_qs.order_by("-noted_on", "-created_at"),
    }
    return render(request, "myapp/pets/detail.html", context)

@login_required
def pet_edit(request, pk):
    # ... (โค้ด pet_edit ... ถูกต้องแล้ว) ...
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == "POST":
        form = PetForm(request.POST, request.FILES, instance=pet)
        vaccines  = VaccineFormSet(request.POST, instance=pet, prefix="vaccines")
        allergies = AllergyFormSet(request.POST, instance=pet, prefix="allergies")
        if form.is_valid() and vaccines.is_valid() and allergies.is_valid():
            form.save(); vaccines.save(); allergies.save()
            messages.success(request, "อัปเดตข้อมูลเรียบร้อย")
            return redirect("pet_detail", pk=pet.pk)
    else:
        form = PetForm(instance=pet)
        vaccines  = VaccineFormSet(instance=pet, prefix="vaccines")
        allergies = AllergyFormSet(instance=pet, prefix="allergies")
    return render(request, "myapp/pets/edit.html", {
        "form": form, "vaccines": vaccines, "allergies": allergies, "pet": pet
    })

@login_required
def pet_delete(request, pk: int):
    # ... (โค้ด pet_delete ... ถูกต้องแล้ว) ...
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    if request.method == "POST":
        name = pet.name
        pet.delete()
        messages.success(request, f"ลบ {name} เรียบร้อยแล้ว")
        return redirect("profile")
    messages.error(request, "วิธีลบที่ถูกต้องคือกดปุ่ม Delete")
    return redirect("pet_detail", pk=pk)

def adoption_list_view(request):
    
    # ⬇️ ⬇️ ⬇️ ✅ เพิ่ม DEBUG PRINT ⬇️ ⬇️ ⬇️
    print("\n--- 1. DEBUG: กำลังรัน [adoption_list_view] (หน้ารวม 'หาบ้าน') ---")
    
    cat_posts = Post.objects.filter(
        post_type='ADOPTION', 
        is_active=True,
        pet__animal__species__iexact='CAT'
    ).select_related('pet', 'pet__animal').order_by('-created_at')

    # ⬇️ ⬇️ ⬇️ ✅ เพิ่ม DEBUG PRINT ⬇️ ⬇️ ⬇️
    print(f"--- 2. DEBUG: ผลลัพธ์ 'cat_posts': {list(cat_posts)} ---")

    dog_posts = Post.objects.filter(
        post_type='ADOPTION', 
        is_active=True,
        pet__animal__species__iexact='DOG'
    ).select_related('pet', 'pet__animal').order_by('-created_at')
    
    context = {
        'cat_posts': cat_posts,
        'dog_posts': dog_posts,
        'page_type': 'adoption_all',
        'page_title': 'น้องๆที่อยากได้บ้านใหม่',
    }
    return render(request, 'myapp/pet_list.html', context)

def lost_list_view(request):
    # ... (โค้ด lost_list_view ... ถูกต้องแล้ว) ...
    cat_posts = Post.objects.filter(
        post_type='LOST', 
        is_active=True,
        pet__animal__species__iexact='CAT'
    ).select_related('pet', 'pet__animal', 'user').order_by('-created_at')

    dog_posts = Post.objects.filter(
        post_type='LOST', 
        is_active=True,
        pet__animal__species__iexact='DOG'
    ).select_related('pet', 'pet__animal', 'user').order_by('-created_at')
    
    context = {
        'cat_posts': cat_posts,   
        'dog_posts': dog_posts,   
        'page_title': 'สัตว์เลี้ยงหาย',
        'page_type': 'lost_all'
    }
    return render(request, 'myapp/pet_list.html', context)

@login_required
def pet_report_create(request, post_type):
    # ... (โค้ด pet_report_create ... ถูกต้องแล้ว) ...
    if post_type.upper() not in [Post.PostType.ADOPTION, Post.PostType.LOST]:
        messages.error(request, "ประเภทโพสต์ไม่ถูกต้อง")
        return redirect('report_select_category')
    page_title = "ประกาศตามหา" if post_type.upper() == Post.PostType.LOST else "ประกาศหาบ้าน"
    if request.method == "POST":
        form = PublicPostForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                with transaction.atomic(): 
                    new_pet = Pet.objects.create(
                        owner=request.user,
                        animal=cleaned_data.get('animal'),
                        name=cleaned_data.get('pet_name'),
                        gender=cleaned_data.get('gender'),
                        birth_date=cleaned_data.get('birth_date'),
                        image=cleaned_data.get('image'),
                        status=Pet.StatusChoices.OWNED
                    )
                    new_post = Post.objects.create(
                        user=request.user,
                        pet=new_pet,
                        post_type=post_type.upper(),
                        description=cleaned_data.get('description'),
                        lost_date=cleaned_data.get('lost_date'),
                        lost_location=cleaned_data.get('lost_location'),
                        contact_phone=cleaned_data.get('contact_phone'),
                        contact_social=cleaned_data.get('contact_social'),
                        is_active=True
                    )
                messages.success(request, f"บันทึกประกาศ '{new_pet.name}' เรียบร้อยแล้ว")
                if new_post.post_type == Post.PostType.LOST:
                    return redirect('lost_list')
                else:
                    return redirect('adoption_list')
            except Exception as e:
                messages.error(request, "เกิดข้อผิดพลาดในการบันทึกข้อมูล")
    else:
        form = PublicPostForm()
    return render(request, "myapp/pet_report_create.html", {
        'form': form,
        'post_type': post_type.upper(), 
        'page_title': page_title
    })

@login_required
def report_select_category(request):
    # ... (โค้ด report_select_category ... ถูกต้องแล้ว) ...
    return render(request, "myapp/pet_report_select.html")

def foundation_list_view(request):
    # ... (โค้ด foundation_list_view ... ถูกต้องแล้ว) ...
    foundations = Foundation.objects.filter(is_active=True).order_by('name')
    context = {
        'foundations': foundations,
        'page_title': 'ติดต่อหน่วยงาน/มูลนิธิ'
    }
    return render(request, 'myapp/contact_list.html', context)

def cat_list_view(request):
    
    # ⬇️ ⬇️ ⬇️ ✅ เพิ่ม DEBUG PRINT ⬇️ ⬇️ ⬇️
    print("\n--- 1. DEBUG: กำลังรัน [cat_list_view] (หน้า 'แมวเท่านั้น') ---")
    
    posts = Post.objects.filter(
        post_type='ADOPTION', 
        is_active=True,
        pet__animal__species__iexact='CAT'
    ).select_related('pet', 'pet__animal').order_by('-created_at')

    # ⬇️ ⬇️ ⬇️ ✅ เพิ่ม DEBUG PRINT ⬇️ ⬇️ ⬇️
    print(f"--- 2. DEBUG: ผลลัพธ์ 'cat_posts': {list(posts)} ---")
    
    context = {
        'cat_posts': posts,
        'dog_posts': [],
        'page_title': 'น้องแมวหาบ้าน',
        'page_type': 'cats_only'
    }
    return render(request, 'myapp/pet_list.html', context)

def dog_list_view(request):
    # ... (โค้ด dog_list_view ... ถูกต้องแล้ว) ...
    posts = Post.objects.filter(
        post_type='ADOPTION', 
        is_active=True,
        pet__animal__species__iexact='DOG'
    ).select_related('pet', 'pet__animal').order_by('-created_at')
    
    context = {
        'dog_posts': posts,
        'cat_posts': [],
        'page_title': 'น้องหมาหาบ้าน',
        'page_type': 'dogs_only'
    }
    return render(request, 'myapp/pet_list.html', context)

def post_detail_view(request, pk):
    # ดึง Post 1 ชิ้น โดยใช้ pk (ID) จาก URL
    #    เราใช้ select_related เพื่อดึงข้อมูล Pet, Animal, User มาพร้อมกันใน Query เดียว
    post = get_object_or_404(
        Post.objects.select_related('pet', 'pet__animal', 'user'), 
        pk=pk, 
        is_active=True
    )
    
    # สร้าง context เพื่อส่ง 'post' ไปให้ template ใหม่
    context = {
        'post': post
    }
    
    # Render template ใหม่ (ที่เรากำลังจะสร้างในขั้นตอนที่ 3)
    return render(request, 'myapp/post_detail.html', context)