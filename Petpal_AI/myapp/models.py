from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

class User(AbstractUser):
    USER_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
    ]
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]

    user_status = models.CharField(max_length=10, choices=USER_STATUS_CHOICES, default='ACTIVE')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.email})"
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)  # รูปโปรไฟล์
    # หมายเหตุ: phone/address อยู่ใน User อยู่แล้ว ใช้ของเดิม

    def __str__(self):
        return f"Profile<{self.user.username}>"

class Animal(models.Model):
    SPECIES_CHOICES = [
        ("DOG", "Dog"),
        ("CAT", "Cat"),
    ]
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_species_display()} - {self.breed}" if self.breed else self.get_species_display()

    
class Pet(models.Model):

    class StatusChoices(models.TextChoices): # สถานะสัตว์เลี้ยง
        ADOPTION = "ADOPTION", "รอหาบ้าน"
        LOST = "LOST", "กำลังตามหา"
        OWNED = "OWNED", "มีเจ้าของแล้ว"

    class GenderChoices(models.TextChoices):
        MALE = 'MALE','ตัวผู้'
        FEMALE = 'FEMALE', 'ตัวเมีย'
        UNKNOWN = 'UNKNOWN', 'ไม่ระบุเพศ'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pets")
    animal = models.ForeignKey('Animal', on_delete=models.SET_NULL, null=True, blank=True, related_name="pets")
    name = models.CharField(max_length=120)

    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.OWNED, #ตั้งค่าเริ่มต้นเป็น มีเจ้าของแล้ว
        db_index=True # เพิ่ม index เพราะเราจะค้นหาจากฟิลด์นี้บ่อยๆ
    )

    gender = models.CharField(
        max_length = 10,
        choices = GenderChoices.choices,
        default = GenderChoices.UNKNOWN
    )

    description = models.TextField(
        blank=True, null=True, 
        verbose_name="ลักษณะ/ตำหนิ"
    )

    lost_date = models.DateField(
        blank=True, null=True, 
        verbose_name="วันที่หาย"
    )

    lost_location = models.CharField(
        max_length=255, blank=True, 
        verbose_name="หายจาก (สถานที่)"
    )

    # เบอร์ติดต่อสำหรับโพสต์นี้ (แยกจากเบอร์ของ User)
    contact_phone = models.CharField(
        max_length=50, blank=True, 
        verbose_name="เบอร์ติดต่อฉุกเฉิน"
    )

    # รวม Social (FB, IG, Line)
    contact_social = models.TextField(
        blank=True, 
        verbose_name="ข้อมูลติดต่อ (Facebook, Line, IG)"
    )

    birth_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to="pets/", blank=True, null=True)
    cover_image = models.ImageField(upload_to="pets/covers/", blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class VaccineRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE,
                            related_name="vaccine_records")  # 1:N
    vaccine_name  = models.CharField(max_length=120)
    vaccinated_on = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    hospital_name = models.CharField(max_length=255, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

class PetAllergy(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "LOW"
        MEDIUM = "MEDIUM", "MEDIUM"
        HIGH = "HIGH", "HIGH"
        CRITICAL = "CRITICAL", "CRITICAL"

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE,
                            related_name="allergies")         # 1:N
    allergy_name = models.CharField(max_length=120)
    severity     = models.CharField(max_length=8,
                                    choices=Severity.choices,
                                    default=Severity.LOW)
    noted_on     = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

class Post(models.Model):
    class PostType(models.TextChoices):
        ADOPTION = "ADOPTION","ประกาศหาบ้าน"
        LOST = "LOST","ประกาศตามหา"

    post_type = models.CharField(max_length=10, choices=PostType.choices, db_index = True)

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    description = models.TextField(blank=True, null=True)
    lost_date = models.DateField(blank=True, null=True)
    lost_location = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_social = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # เอาไว้ปิดโพสต์

class Foundation(models.Model):
    """
    Model สำหรับเก็บข้อมูลมูลนิธิ หรือ องค์กรช่วยเหลือสัตว์
    (สำหรับหน้า 'ติดต่อ' ที่เป็น Directory)
    """
    name = models.CharField(
        max_length=255, 
        verbose_name="ชื่อมูลนิธิ/องค์กร"
    )
    logo = models.ImageField(
        upload_to="foundations/logos/", 
        blank=True, null=True, 
        verbose_name="โลโก้"
    )
    description = models.TextField(
        blank=True, 
        verbose_name="คำอธิบายสั้นๆ"
    )
    address = models.TextField(
        blank=True, 
        verbose_name="ที่อยู่"
    )
    phone = models.CharField(
        max_length=100, blank=True, 
        verbose_name="เบอร์โทรศัพท์"
    )
    email = models.EmailField(
        blank=True, 
        verbose_name="อีเมลติดต่อ"
    )
    website_url = models.URLField(
        max_length=500, blank=True, 
        verbose_name="เว็บไซต์"
    )
    facebook_url = models.URLField(
        max_length=500, blank=True, 
        verbose_name="Facebook URL"
    )
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name="แสดงในระบบ"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foundation / Org"
        verbose_name_plural = "Foundations / Orgs"
        ordering = ['name'] # เรียงตามชื่อ

    def __str__(self):
        return self.name