from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from myapp.models import Post
from datetime import timedelta

class Command(BaseCommand):
    help = 'ส่งอีเมลแจ้งเตือนแบบ HTML'

    def handle(self, *args, **options):
        today = timezone.now().date()
        notification_date = today + timedelta(days=3)
        
        expiring_posts = Post.objects.filter(expiry_date=notification_date, is_active=True)
        
        for post in expiring_posts:
            user_email = post.user.email
            if user_email:
                subject = f" [Petpal AI] ประกาศ '{post.pet.name}' ใกล้หมดอายุ"
                
                # 1. แปลง HTML เป็น String
                html_content = render_to_string('emails/expiry_alert.html', {'post': post})
                # 2. สร้างเวอร์ชัน Text ธรรมดา (เผื่อเมลใครไม่รองรับ HTML)
                text_content = strip_tags(html_content)
                
                try:
                    # 3. สร้างและส่งอีเมล
                    email = EmailMultiAlternatives(
                        subject,
                        text_content,
                        None,
                        [user_email]
                    )
                    email.attach_alternative(html_content, "text/html") # แนบ HTML
                    email.send()
                    
                    self.stdout.write(self.style.SUCCESS(f' Sent HTML email to {user_email}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f' Error: {e}'))