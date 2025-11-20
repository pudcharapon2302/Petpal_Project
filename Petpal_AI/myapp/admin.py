# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

# ปรับให้ตรงกับ models ของโปรเจกต์คุณ
from .models import (
    AdoptionRequest,
    ChatMessage,
    User,
    Profile,
    Animal,
    Pet,
    VaccineRecord,
    PetAllergy,
    Post,
    Foundation
)

# -------------------- User --------------------
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # ... (โค้ด UserAdmin ของคุณ ... ถูกต้องแล้ว) ...
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Extra info", {"fields": ("phone", "address", "user_status", "role")}),
    )
    list_display = (
        "username", "email", "phone", "address",
        "is_active", "is_staff",
    )
    list_filter = ("is_active", "is_staff", "role", "user_status")
    search_fields = ("username", "email", "phone")


# -------------------- Profile --------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # ... (โค้ด ProfileAdmin ของคุณ ... ถูกต้องแล้ว) ...
    list_display = ("user", "avatar_thumb")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("avatar_thumb",)

    def avatar_thumb(self, obj):
        # ... (โค้ด avatar_thumb) ...
        if getattr(obj, "avatar", None):
            try:
                return format_html(
                    '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:50%;">',
                    obj.avatar.url,
                )
            except Exception:
                pass
        return "—"
    avatar_thumb.short_description = "Avatar"


# -------------------- Animal --------------------
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    # ... (โค้ด AnimalAdmin ของคุณ ... ถูกต้องแล้ว) ...
    list_display = ("animal_name", "species", "breed", "description_short")
    list_filter = ("species", "breed")
    search_fields = ("breed", "name")

    def animal_name(self, obj):
        # ... (โค้ด animal_name) ...
        return getattr(obj, "name", "—")
    animal_name.short_description = "Name"

    def description_short(self, obj):
        # ... (โค้ด description_short) ...
        desc = getattr(obj, "description", "")
        if not desc:
            return "—"
        return (desc[:50] + "…") if len(desc) > 50 else desc
    description_short.short_description = "Description"


# -------------------- Inlines (ของ Pet) --------------------
class VaccineInline(admin.TabularInline):
    # ... (โค้ด VaccineInline ของคุณ ... ถูกต้องแล้ว) ...
    model = VaccineRecord
    extra = 0
    fields = ("vaccine_name", "vaccinated_on", "next_due_date", "hospital_name")
    show_change_link = True
    classes = ("collapse",)

class AllergyInline(admin.TabularInline):
    # ... (โค้ด AllergyInline ของคุณ ... ถูกต้องแล้ว) ...
    model = PetAllergy
    extra = 0
    fields = ("allergy_name", "severity", "noted_on")
    show_change_link = True
    classes = ("collapse",)


# -------------------- Pet --------------------
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    # ... (โค้ด PetAdmin ของคุณ ... ถูกต้องแล้ว) ...
    list_display = (
        "name", "owner",
        "species", "breed",
        "weight", "birth_date",
        "vaccine_count", "allergy_count",
        "thumbnail", "cover_thumb",
        "created_at",
    )
    list_filter = ("animal__species", "animal__breed", "birth_date", "created_at")
    search_fields = ("name", "owner__username", "owner__email", "animal__breed", "animal__name")
    list_select_related = ("owner", "animal")
    date_hierarchy = "birth_date"
    ordering = ("-created_at",)
    list_per_page = 25
    autocomplete_fields = ("animal", "owner")
    readonly_fields = ("thumbnail", "cover_thumb")
    fieldsets = (
        ("Basic info", {
            "fields": ("owner", "animal", "name", "birth_date", "weight")
        }),
        ("Images", {
            "fields": ("image", "thumbnail", "cover_image", "cover_thumb")
        }),
    )
    inlines = [VaccineInline, AllergyInline]

    # ----- helper cols -----
    def species(self, obj):
        return getattr(obj.animal, "species", "—")
    species.admin_order_field = "animal__species"
    # ... (โค้ด helper cols อื่นๆ ของคุณ ... ถูกต้องแล้ว) ...
    def breed(self, obj):
        return getattr(obj.animal, "breed", "—")
    breed.admin_order_field = "animal__breed"

    def vaccine_count(self, obj):
        rel = getattr(obj, "vaccinerecord_set", None)
        if hasattr(obj, "vaccine_records"):
            return obj.vaccine_records.count()
        return rel.count() if rel is not None else 0
    vaccine_count.short_description = "Vaccines"

    def allergy_count(self, obj):
        rel = getattr(obj, "petallergy_set", None)
        if hasattr(obj, "allergies"):
            return obj.allergies.count()
        return rel.count() if rel is not None else 0
    allergy_count.short_description = "Allergies"

    def thumbnail(self, obj):
        if getattr(obj, "image", None):
            try:
                return format_html(
                    '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:50%;">',
                    obj.image.url,
                )
            except Exception:
                pass
        return "—"
    thumbnail.short_description = "Avatar"

    def cover_thumb(self, obj):
        if hasattr(obj, "cover_image") and getattr(obj, "cover_image", None):
            try:
                return format_html(
                    '<img src="{}" style="height:40px;width:70px;object-fit:cover;border-radius:6px;">',
                    obj.cover_image.url,
                )
            except Exception:
                pass
        return "—"
    cover_thumb.short_description = "Cover"

# -------------------- VaccineRecord --------------------
@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    # ... (โค้ด VaccineRecordAdmin ของคุณ ... ถูกต้องแล้ว) ...
    list_display = ("vaccine_name", "pet", "vaccinated_on", "next_due_date", "hospital_name", "created_at")
    list_filter = ("vaccinated_on", "next_due_date")
    search_fields = ("vaccine_name", "pet__name", "hospital_name")
    autocomplete_fields = ("pet",)
    date_hierarchy = "vaccinated_on"
    ordering = ("-vaccinated_on",)

# -------------------- PetAllergy --------------------
@admin.register(PetAllergy)
class PetAllergyAdmin(admin.ModelAdmin):
    # ... (โค้ด PetAllergyAdmin ของคุณ ... ถูกต้องแล้ว) ...
    list_display = ("allergy_name", "pet", "severity", "noted_on", "created_at")
    list_filter = ("severity", "noted_on")
    search_fields = ("allergy_name", "pet__name")
    autocomplete_fields = ("pet",)
    date_hierarchy = "noted_on"
    ordering = ("-noted_on",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_type', 'pet_name', 'user_username', 'created_at', 'is_active')
    list_filter = ('post_type', 'is_active', 'created_at')
    search_fields = ('pet__name', 'user__username')
    autocomplete_fields = ('pet', 'user') # ทำให้ค้นหา pet/user ง่ายขึ้น
    list_select_related = ('pet', 'user')
    date_hierarchy = 'created_at'

    # สร้าง helper methods เพื่อให้แสดงชื่อได้สวยๆ
    def pet_name(self, obj):
        if obj.pet:
            return obj.pet.name
        return "—"
    pet_name.short_description = "Pet"
    pet_name.admin_order_field = "pet__name"

    def user_username(self, obj):
        if obj.user:
            return obj.user.username
        return "—"
    user_username.short_description = "User"
    user_username.admin_order_field = "user__username"

@admin.register(Foundation)
class FoundationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'website_url', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'phone', 'email')
    
    # กำหนด fieldset เพื่อจัดระเบียบหน้า admin
    fieldsets = (
        (None, {
            'fields': ('name', 'logo', 'description', 'is_active')
        }),
        ('Contact Info', {
            'fields': ('address', 'phone', 'email', 'website_url', 'facebook_url')
        }),
    )

@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'post', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'post__pet__name')
    autocomplete_fields = ('requester', 'post')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'short_content', 'request', 'timestamp')
    
    # ตัวกรอง: ดูตามวันที่
    list_filter = ('timestamp',)
    
    # 🔎 ช่องค้นหา: พิมพ์คำที่ต้องการตรวจสอบตรงนี้ (สำคัญมาก!)
    search_fields = ('content', 'sender__username', 'sender__email')
    
    readonly_fields = ('timestamp',) # ห้ามแก้เวลา

    # ฟังก์ชันย่อข้อความ (ถ้าข้อความยาวเกินไป ให้ตัดเหลือแค่สั้นๆ ในหน้า list)
    def short_content(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    short_content.short_description = "ข้อความ"