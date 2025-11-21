import time
from django.core.management.base import BaseCommand
from myapp.models import Post, Foundation
from myapp.rag_service import rag_service
from langchain_core.documents import Document

class Command(BaseCommand):
    help = 'Trains the RAG model with data from the MySQL database (Safe Mode).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting AI training...'))

        # 1. รวบรวมข้อมูลทั้งหมดมาเตรียมไว้ก่อน (ยังไม่ส่งไป Google)
        documents = []

        # --- เก็บข้อมูล Posts ---
        posts = Post.objects.filter(is_active=True).select_related('pet', 'pet__animal')
        for post in posts:
            pet = post.pet
            if not pet: continue
            
            breed_info = pet.animal.breed if pet.animal and pet.animal.breed else 'ไม่ระบุสายพันธุ์'
            content = (
                f"ข้อมูลประกาศ {post.get_post_type_display()}: "
                f"ชื่อสัตว์เลี้ยง {pet.name}, "
                f"สายพันธุ์ {breed_info}, "
                f"เพศ {pet.get_gender_display()}. "
                f"รายละเอียดเพิ่มเติม: {post.description}"
            )
            doc = Document(
                page_content=content,
                metadata={"source": "post", "post_id": post.id, "pet_name": pet.name}
            )
            documents.append(doc)
        
        # --- เก็บข้อมูล Foundations ---
        foundations = Foundation.objects.filter(is_active=True)
        for foundation in foundations:
            content = (
                f"ข้อมูลมูลนิธิ: ชื่อ {foundation.name}, "
                f"ที่อยู่ {foundation.address}, "
                f"เบอร์ติดต่อ {foundation.phone}"
            )
            doc = Document(
                page_content=content,
                metadata={"source": "foundation", "foundation_id": foundation.id}
            )
            documents.append(doc)

        # 2. เริ่มส่งข้อมูล (ทีละชุด + พัก)
        total_docs = len(documents)
        if total_docs > 0:
            self.stdout.write(f'Found {total_docs} documents. Starting slow upload...')
            
            BATCH_SIZE = 1  
            
            for i in range(0, total_docs, BATCH_SIZE):
                batch = documents[i : i + BATCH_SIZE]
                
                # --- เพิ่มโค้ดส่วนนี้ ---
                # แสดงข้อมูลที่กำลังจะส่ง เพื่อให้เห็นว่ากำลังเทรนอะไรอยู่
                for doc in batch:
                    # แสดงตัวอย่างข้อมูล 120 ตัวอักษรแรก เพื่อไม่ให้ log ยาวเกินไป
                    content_preview = (doc.page_content[:120] + '...') if len(doc.page_content) > 120 else doc.page_content
                    self.stdout.write(f"  -> Sending: \"{content_preview}\"")
                # -----------------------
                
                try:
                    rag_service.vector_store.add_documents(batch)
                    self.stdout.write(self.style.SUCCESS(f"   Processed {i + 1}/{total_docs}... OK"))
                    
                    # เปลี่ยน: พักนานขึ้น (10-15 วินาที ต่อ 1 รายการ)
                    # Google Free Tier ให้ประมาณ 2-15 requests/minute
                    time.sleep(10) 
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error in item {i}: {e}'))
                    time.sleep(60) 

            self.stdout.write(self.style.SUCCESS('🎉 Training finished!'))
        else:
            self.stdout.write(self.style.WARNING('No documents found to train.'))