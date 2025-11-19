from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from myapp.models import Post
from datetime import timedelta

class Command(BaseCommand):
    help = 'ส่งอีเมลแจ้งเตือนโพสต์ที่ใกล้หมดอายุ (อีก 3 วัน)'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # กำหนดวันแจ้งเตือนล่วงหน้า (เช่น อีก 3 วันจะหมดอายุ)
        notification_date = today + timedelta(days=3)

        self.stdout.write(f"Checking for posts expiring on {notification_date}...")

        # หาโพสต์ที่ (1) จะหมดอายุในอีก 3 วัน และ (2) ยังเปิดใช้งานอยู่
        expiring_posts = Post.objects.filter(
            expiry_date=notification_date,
            is_active=True
        )

        if expiring_posts.count() == 0:
            self.stdout.write(self.style.WARNING("No posts found expiring in 3 days."))
            return

        self.stdout.write(f"Found {expiring_posts.count()} posts to notify.")

        for post in expiring_posts:
            user_email = post.user.email
            
            if user_email:
                subject = f"[Petpal AI] แจ้งเตือน: ประกาศ '{post.pet.name}' ใกล้หมดอายุ"
                message = f"""
สวัสดีคุณ {post.user.username},

ประกาศของคุณสำหรับน้อง "{post.pet.name}" กำลังจะหมดอายุในวันที่ {post.expiry_date} (อีก 3 วัน)

- หากน้องยังไม่ได้บ้าน: กรุณาเข้าสู่ระบบเพื่อต่ออายุประกาศ
- หากน้องได้บ้านแล้ว: คุณสามารถปล่อยให้ประกาศหมดอายุได้เลย

ขอบคุณที่ใช้บริการ Petpal AI
ทีมงาน
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        None, # ใช้ DEFAULT_FROM_EMAIL จาก settings
                        [user_email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f'✅ Sent email to {user_email}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Failed to send to {user_email}: {e}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ User for post {post.id} has no email address.'))