# forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import inlineformset_factory
from .models import Pet, User , VaccineRecord, PetAllergy , Animal ,Post

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone", "address")

    def save(self, commit=True):
        user = super().save(commit=False)  # จะได้ username + (password จะ set โดย UserCreationForm)
        # กำหนดฟิลด์เสริมให้ชัดเจน
        user.email = self.cleaned_data.get("email", "")
        user.phone = self.cleaned_data.get("phone", "")
        user.address = self.cleaned_data.get("address", "")
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={"placeholder": "Username or Email"})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    remember = forms.BooleanField(
        label="จดจำฉัน", required=False
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"})
    )
    address = forms.CharField(
        label="Address", required=False,
        widget=forms.TextInput(attrs={"placeholder": "Address"})
    )
    phone = forms.CharField(
        label="Phone", required=False,
        widget=forms.TextInput(attrs={"placeholder": "Phone"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "password1", "password2", "address", "phone"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้ไปแล้ว")
        return email

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ["animal", "name", "birth_date", "weight", "image", "cover_image"]
        widgets = {
            "animal": forms.Select(attrs={"class":"mt-1 w-full rounded-xl border border-gray-300 px-3 py-2"}),
            "name": forms.TextInput(attrs={"class":"mt-1 w-full rounded-xl border border-gray-300 px-3 py-2","placeholder":"เช่น Topfy"}),
            "birth_date": forms.DateInput(attrs={"type":"date","class":"mt-1 w-full rounded-xl border border-gray-300 px-3 py-2"}),
            "weight": forms.NumberInput(attrs={"step":"0.01","class":"mt-1 w-full rounded-xl border border-gray-300 px-3 py-2","placeholder":"เช่น 4.2"}),
            "image": forms.ClearableFileInput(attrs={"id":"id_avatar_image","accept":"image/*","class":"hidden"}),
            "cover_image": forms.ClearableFileInput(attrs={"id":"id_cover_image","accept":"image/*","class":"hidden"}),
        }

# วัคซีน: ว่างได้ (extra=1 มีฟอร์มเปล่าให้ 1 แถว), ลบแถวได้ (can_delete=True)
VaccineFormSet = inlineformset_factory(
    Pet, VaccineRecord,
    fields=["vaccine_name", "vaccinated_on", "next_due_date", "hospital_name"],
    widgets={
        "vaccine_name":  forms.TextInput(attrs={"class":"w-full rounded-xl border border-gray-300 px-3 py-2","placeholder":"เช่น FVRCP"}),
        "vaccinated_on": forms.DateInput(attrs={"type":"date","class":"w-full rounded-xl border border-gray-300 px-3 py-2"}),
        "next_due_date": forms.DateInput(attrs={"type":"date","class":"w-full rounded-xl border border-gray-300 px-3 py-2"}),
        "hospital_name": forms.TextInput(attrs={"class":"w-full rounded-xl border border-gray-300 px-3 py-2","placeholder":"คลินิก/รพ."}),
    },
    extra=1, can_delete=True
)

# แพ้: ว่างได้
AllergyFormSet = inlineformset_factory(
    Pet, PetAllergy,
    fields=["allergy_name", "severity", "noted_on"],
    widgets={
        "allergy_name": forms.TextInput(attrs={"class":"w-full rounded-xl border border-gray-300 px-3 py-2","placeholder":"เช่น Chicken"}),
        "severity":     forms.Select(attrs={"class":"w-full rounded-xl border border-gray-300 px-3 py-2"}),
        "noted_on":     forms.DateInput(attrs={"type":"date","class":"w-full rounded-xl border border-gray-300 px-3 py-2"}),
    },
    extra=1, can_delete=True
)

#Form สำหรับประกาศหาบ้าน และ หาสัตว์หาย
class PublicPostForm(forms.Form):

    # === 1. Fields for Post model ===
    description = forms.CharField(
        label="ลักษณะ/ตำหนิ", required=False,
        widget=forms.Textarea(attrs={"class":"form-input", "rows": 3, "placeholder":"เช่น สีส้ม ขนฟู หางเป็นพวง..."})
    )
    lost_date = forms.DateField(
        label="วันที่หาย", required=False,
        widget=forms.DateInput(attrs={"type":"date", "class":"form-input"})
    )
    lost_location = forms.CharField(
        label="หายจาก (สถานที่)", required=False,
        widget=forms.TextInput(attrs={"class":"form-input", "placeholder":"เช่น ตลาด, ซอย..."})
    )
    contact_phone = forms.CharField(
        label="เบอร์ติดต่อฉุกเฉิน", required=False,
        widget=forms.TextInput(attrs={"class":"form-input", "placeholder":"เบอร์โทรที่ให้ติดต่อได้"})
    )
    contact_social = forms.CharField(
        label="ข้อมูลติดต่อ (Facebook, Line, IG)", required=False,
        widget=forms.Textarea(attrs={"class":"form-input", "rows": 3, "placeholder":"Facebook: ...\nLine ID: ..."})
    )

    # === 2. Fields for Pet model (ที่เราจะสร้างใหม่) ===
    pet_name = forms.CharField(
        label="ชื่อแมว/หมา",
        widget=forms.TextInput(attrs={"class":"form-input", "placeholder":"ชื่อแมว/หมา (ถ้ามี)"})
    )
    animal = forms.ModelChoiceField(
        label="สายพันธุ์",
        queryset=Animal.objects.all().order_by('species', 'breed'),
        widget=forms.Select(attrs={"class":"form-input"})
    )
    gender = forms.ChoiceField(
        label="เพศ",
        choices=Pet.GenderChoices.choices,
        initial=Pet.GenderChoices.UNKNOWN,
        widget=forms.Select(attrs={"class":"form-input"})
    )
    birth_date = forms.DateField(
        label="วันเกิด (ประมาณ)", required=False,
        widget=forms.DateInput(attrs={"type":"date", "class":"form-input"})
    )
    image = forms.ImageField(
        label="รูปภาพ", required=True,
        widget=forms.ClearableFileInput(attrs={"accept":"image/*"})
    )