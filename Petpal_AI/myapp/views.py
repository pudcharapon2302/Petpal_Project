# myapp/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import NoReverseMatch
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Animal, User , Profile, Pet , Post, Foundation , AdoptionRequest, ChatMessage
from .forms import CustomUserCreationForm ,LoginForm, PetForm, RegisterForm , VaccineFormSet, AllergyFormSet , PublicPostForm,PublicPostEditForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .rag_service import rag_service


User = get_user_model()

def get_active_posts():
    return Post.objects.filter(is_active=True)

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
    logout(request)
    messages.success(request, "ออกจากระบบแล้ว")
    return redirect(settings.LOGOUT_REDIRECT_URL)

@login_required
def profile_page(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    pets = Pet.objects.filter(owner=request.user, status='OWNED').order_by("-id")
    animals = Animal.objects.all().order_by("species", "breed")
    adoption_notifications = AdoptionRequest.objects.filter(post__user=request.user).select_related('requester', 'post', 'post__pet')
    return render(request, "myapp/profile.html", {
        "profile": profile, 
        "pets": pets, 
        "animals": animals,
        "adoption_notifications": adoption_notifications # <-- ส่งไปหน้าเว็บ
    })

@require_POST
@login_required
def account_delete(request):
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

@login_required
def adoption_list_view(request):
    
    cat_posts = Post.objects.filter(
        post_type='ADOPTION', 
        is_active=True,
        pet__animal__species__iexact='CAT'
    ).select_related('pet', 'pet__animal').order_by('-created_at')

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

@login_required
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
                        status=post_type.upper()
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
    return render(request, "myapp/pet_report_select.html")

@login_required
def foundation_list_view(request):
    foundations = Foundation.objects.filter(is_active=True).order_by('name')
    context = {
        'foundations': foundations,
        'page_title': 'ติดต่อหน่วยงาน/มูลนิธิ'
    }
    return render(request, 'myapp/contact_list.html', context)

def cat_list_view(request):
    
    posts = Post.objects.filter(
        post_type='ADOPTION', 
        is_active=True,
        pet__animal__species__iexact='CAT'
    ).select_related('pet', 'pet__animal').order_by('-created_at')
    
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

@login_required
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

@login_required
def send_adoption_request(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # ห้ามเจ้าของกดรับเลี้ยงโพสต์ตัวเอง
    if post.user == request.user:
        messages.warning(request, "คุณไม่สามารถกดรับเลี้ยงสัตว์ของตัวเองได้")
        return redirect('post_detail', pk=pk)

    # ตรวจสอบว่าเคยกดไปหรือยัง
    existing_request = AdoptionRequest.objects.filter(post=post, requester=request.user).exists()
    
    if existing_request:
        messages.info(request, "คุณได้ส่งคำขอรับเลี้ยงน้องตัวนี้ไปแล้ว")
    else:
        AdoptionRequest.objects.create(post=post, requester=request.user)
        messages.success(request, f"ส่งคำขอรับเลี้ยงน้อง {post.pet.name} แล้ว! เจ้าของจะได้รับการแจ้งเตือน")
        
    return redirect('post_detail', pk=pk)

@login_required
def adoption_requests_list(request):
    received_requests = AdoptionRequest.objects.filter(post__user=request.user)\
        .select_related('requester', 'post', 'post__pet')\
        .order_by('-created_at')
    
    sent_requests = AdoptionRequest.objects.filter(requester=request.user)\
        .select_related('post__user', 'post', 'post__pet')\
        .order_by('-created_at')
    
    return render(request, 'myapp/adoption_requests_list.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })

@login_required
def chat_room(request, request_id):
    req = get_object_or_404(AdoptionRequest, pk=request_id)

    if request.user != req.requester and request.user != req.post.user:
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงห้องแชทนี้")
        return redirect('landing')

    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        if content:
            ChatMessage.objects.create(
                request=req,
                sender=request.user,
                content=content
            )
            return redirect('chat_room', request_id=request_id)

    chat_messages = req.messages.all().order_by('timestamp')

    return render(request, 'myapp/chat_room.html', {
        'adoption_req': req,
        'chat_messages': chat_messages
    })

@login_required
def update_adoption_status(request, request_id, action):
    req = get_object_or_404(AdoptionRequest, pk=request_id)

    # ความปลอดภัย: ต้องเป็น "เจ้าของโพสต์" เท่านั้นถึงจะมีสิทธิ์อนุมัติ
    if request.user != req.post.user:
        messages.error(request, "คุณไม่มีสิทธิ์ดำเนินการนี้")
        return redirect('chat_room', request_id=request_id)

    if action == 'approve':
        req.status = AdoptionRequest.Status.APPROVED
        req.save()
        
        req.post.adopted_at = timezone.now()
        req.post.is_active = False 
        req.post.save()
        
        messages.success(request, f"อนุมัติให้ {req.requester.username} รับเลี้ยงแล้ว!")
        
    elif action == 'reject':
        req.status = AdoptionRequest.Status.REJECTED
        req.save()
        messages.warning(request, "คุณได้ปฏิเสธคำขอนี้")

    return redirect('chat_room', request_id=request_id)

@login_required
def my_posts_list(request):
    """ แสดงรายการโพสต์ทั้งหมดของผู้ใช้ปัจจุบัน """
    posts = Post.objects.filter(user=request.user)\
        .select_related('pet', 'pet__animal')\
        .order_by('-created_at')
    
    return render(request, 'myapp/my_posts_list.html', {'posts': posts})

@login_required
def toggle_post_status(request, pk):
    """ สลับสถานะ เปิด/ปิด โพสต์ """
    post = get_object_or_404(Post, pk=pk, user=request.user) # ต้องเป็นเจ้าของเท่านั้น
    
    if post.is_active:
        post.is_active = False
        messages.warning(request, f"ปิดโพสต์ '{post.pet.name}' แล้ว")
    else:
        post.is_active = True
        messages.success(request, f"เปิดโพสต์ '{post.pet.name}' อีกครั้ง")
    
    post.save()
    return redirect('my_posts_list')

@login_required
def delete_post(request, pk):
    """ ลบโพสต์ถาวร """
    post = get_object_or_404(Post, pk=pk, user=request.user)
    
    if request.method == "POST":
        pet_name = post.pet.name
        post.delete()
        messages.success(request, f"ลบประกาศ '{pet_name}' เรียบร้อยแล้ว")
        
    return redirect('my_posts_list')

@login_required
def pet_report_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    pet = post.pet
    
    if request.method == "POST":
        form = PublicPostEditForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                with transaction.atomic():
                    pet.name = cleaned_data.get('pet_name')
                    pet.animal = cleaned_data.get('animal')
                    pet.gender = cleaned_data.get('gender')
                    pet.birth_date = cleaned_data.get('birth_date')
                    if cleaned_data.get('image'): # อัปเดตรูปเฉพาะถ้ามีการอัปโหลดใหม่
                        pet.image = cleaned_data.get('image')
                    pet.save()

                    #
                    post.description = cleaned_data.get('description')
                    post.lost_date = cleaned_data.get('lost_date')
                    post.lost_location = cleaned_data.get('lost_location')
                    post.contact_phone = cleaned_data.get('contact_phone')
                    post.contact_social = cleaned_data.get('contact_social')
                    # (หมายเหตุ: เราไม่เปิดให้แก้ post_type เพราะมันจะยุ่งยากเรื่อง Logic)
                    post.save()

                messages.success(request, f"อัปเดตประกาศ '{pet.name}' เรียบร้อยแล้ว")
                return redirect('my_posts_list')

            except Exception as e:
                messages.error(request, f"เกิดข้อผิดพลาด: {e}")
    else:
        initial_data = {
            'post_type': post.post_type,
            'description': post.description,
            'lost_date': post.lost_date,
            'lost_location': post.lost_location,
            'contact_phone': post.contact_phone,
            'contact_social': post.contact_social,
            'pet_name': pet.name,
            'animal': pet.animal,
            'gender': pet.gender,
            'birth_date': pet.birth_date,
            'image': pet.image
        }
        form = PublicPostEditForm(initial=initial_data)

    return render(request, "myapp/pet_report_create.html", {
        'form': form,
        'post_type': post.post_type, # ส่งไปเพื่อคุมการแสดงผล
        'page_title': f"แก้ไขประกาศ: {pet.name}",
        'is_edit': True
    })

def ai_chat_page(request):
    return render(request, 'myapp/ai_chat_full.html')

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            ai_response = rag_service.ask_ai(user_message)
            
            return JsonResponse({'response': ai_response})
        
        except Exception as e:
            print("Chat API error:", e)
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
def train_ai_basic(request):
    if not request.user.is_superuser:
        return redirect('landing')
    rag_service.clear_knowledge()
    
    active_posts = Post.objects.filter(is_active=True)
    
    print(f" กำลังเริ่ม Train ข้อมูล {active_posts.count()} รายการ...")
    
    count = 0
    for post in active_posts:
        rag_service.add_post_to_rag(post)
        count += 1
        
    messages.success(request, f" AI เรียนรู้ข้อมูลใหม่ครบ {count} รายการแล้ว!")
    return redirect('landing')