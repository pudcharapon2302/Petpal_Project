import os
import chromadb
from django.conf import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI, ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
import base64

load_dotenv()

class RAGService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        # 1. ตั้งค่า Local Embedding (CPU)
        print(" Loading Local Embedding Model (CPU)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        print(" Local Model Loaded!")

        # 2. ตั้งค่า Gemini Chat (LLM)
        if self.api_key:
            self.llm = GoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.7
            )
            self.vision_model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.3
            )
        else:
            print(" Warning: GOOGLE_API_KEY not found.")
            self.llm = None
            self.vision_model = None

        # 3. เชื่อมต่อ ChromaDB
        try:
            self.chroma_client = chromadb.HttpClient(
                host=os.environ.get("CHROMA_HOST", "chroma_db"), 
                port=int(os.environ.get("CHROMA_PORT", 8000))
            )
            # ใช้ Collection โดยตรงเพื่อความยืดหยุ่นในการใส่ Metadata
            self.collection = self.chroma_client.get_or_create_collection(name="petpal_collection")
            
            # (Optional) เก็บ vector_store ไว้เผื่อใช้ function อื่นของ langchain
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name="petpal_collection",
                embedding_function=self.embeddings,
            )
            print(" RAG Service Initialized")
        except Exception as e:
            print(f" ChromaDB Error: {e}")
            self.vector_store = None
            self.collection = None

    def add_post_to_rag(self, post):
        """ เพิ่มโพสต์สาธารณะลงใน AI Memory พร้อมวิเคราะห์รูปภาพ """
        try:
            # 1. ให้ AI Vision ช่วยดูรูป (ถ้ามี)
            visual_tags = ""
            if post.pet.image:
                print(f" Analyzing image for post {post.id}...")
                visual_tags = self.analyze_pet_image(post.pet.image)

            # 2. เตรียมข้อมูล (เพิ่ม visual_tags เข้าไป)
            location_parts = [
                post.tambon, 
                post.amphoe, 
                f"จ.{post.province}" if post.province else None
            ]
            location_text = " ".join(filter(None, location_parts)) or "ไม่ระบุพิกัด"
            url = getattr(post, 'ai_link', f"http://localhost:8000/post/{post.pk}/")

            # รวมร่างข้อมูล (ใส่สิ่งที่ AI เห็นลงไปด้วย!)
            content = f"""
            (ประกาศสาธารณะ)
            ประเภท: {post.post_type}
            ชื่อน้อง: {post.pet.name}
            สายพันธุ์: {post.pet.animal.breed}
            รายละเอียดจากเจ้าของ: {post.description}
            
            ลักษณะที่ AI มองเห็นจากรูปภาพ: {visual_tags} 
            
            สถานที่: {location_text}
            เบอร์ติดต่อ: {post.contact_phone}
            👉 ลิงก์ดูรายละเอียด: {url}
            """
            
            # 3. Embed และ Save ตามเดิม
            embedding = self.embeddings.embed_query(content)

            self.collection.upsert(
                documents=[content],
                embeddings=[embedding],
                metadatas=[{
                    "source": "post", 
                    "access": "public",
                    "owner_id": "public"
                }],
                ids=[f"post_{post.id}"]
            )
            print(f" Added Post {post.id} to AI memory (with Vision).")
            
        except Exception as e:
             print(f" Error adding post: {e}")

    def add_pet_to_rag(self, pet):
        """ เพิ่มข้อมูลสัตว์เลี้ยงส่วนตัวลงใน AI Memory """
        try:
            if getattr(pet, 'status', 'OWNED') != 'OWNED':
                return

            vaccines_qs = getattr(pet, 'vaccine_records', None)
            if vaccines_qs is None:
                vaccines_qs = getattr(pet, 'vaccine_record_set', None)
            
            if vaccines_qs:
                vaccines = ", ".join([f"{v.vaccine_name} ({v.vaccinated_on})" for v in vaccines_qs.all()])
            else:
                vaccines = "ไม่มีข้อมูล"

            allergies_qs = getattr(pet, 'allergies', None)
            if allergies_qs is None:
                allergies_qs = getattr(pet, 'pet_allergy_set', None)

            if allergies_qs:
                allergies = ", ".join([f"{a.allergy_name} ({a.severity})" for a in allergies_qs.all()])
            else:
                allergies = "ไม่มีข้อมูล"
            # -----------------------------------------------


            content = f"""
            (ข้อมูลสัตว์เลี้ยงส่วนตัว)
            ชื่อ: {pet.name}
            พันธุ์: {pet.animal.breed if pet.animal else 'ไม่ระบุ'}
            เพศ: {pet.get_gender_display()}
            ประวัติวัคซีน: {vaccines}
            ประวัติการแพ้: {allergies}
            เจ้าของ: {pet.owner.first_name or pet.owner.username}
            """

            embedding = self.embeddings.embed_query(content)

            self.collection.upsert(
                documents=[content],
                embeddings=[embedding],
                metadatas=[{
                    "source": "my_pet", 
                    "access": "private",           
                    "owner_id": str(pet.owner.id)  
                }],
                ids=[f"pet_{pet.id}"]
            )
            print(f" Added Pet {pet.name} to AI memory.")

        except Exception as e:
            print(f" Error adding pet {pet.name}: {e}")

    def generate_creative_description(self, user_prompt, pet_name, breed, post_type, image_field=None):
        """ 
        ผสมผสาน User Prompt + AI Vision เพื่อเขียนคำบรรยาย 
        """
        if not self.vision_model: # ใช้ vision_model ที่เราประกาศไว้รอบที่แล้ว
            return "ระบบ AI ไม่พร้อมใช้งาน (API Key Missing)"

        # 1. เตรียมรูปภาพ (ถ้ามี)
        image_part = None
        if image_field:
            try:
                import base64
                image_path = image_field.path if hasattr(image_field, 'path') else image_field
                # กรณีรับมาจาก InMemoryUploadedFile (ตอนยังไม่ Save ลง Disk)
                if hasattr(image_field, 'read'): 
                    image_field.seek(0)
                    image_data = base64.b64encode(image_field.read()).decode("utf-8")
                else:
                    with open(image_path, "rb") as img:
                        image_data = base64.b64encode(img.read()).decode("utf-8")
                
                image_part = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            except Exception as e:
                print(f"Image Error: {e}")

        if post_type == 'LOST':
            role_desc = "ผู้ช่วยเขียนประกาศตามหาสัตว์เลี้ยงหาย"
            tone_desc = "เร่งด่วน, ขอความช่วยเหลือ, เห็นใจ, ชัดเจน"
            objective = "เน้นจุดสังเกตตำหนิที่ชัดเจนที่สุด เพื่อให้คนช่วยมองหา"
        else: # ADOPTION
            role_desc = "นักเขียนประกาศหาบ้านให้สัตว์เลี้ยง"
            tone_desc = "น่ารัก, ขี้อ้อน, อบอุ่น, เชิญชวน"
            objective = "บรรยายความน่ารักและนิสัย เพื่อให้คนอยากรับไปเลี้ยง"

        # 2. สร้าง Prompt
        prompt_text = f"""
        คุณคือ: {role_desc}
        
        ข้อมูลสัตว์เลี้ยง:
        - ชื่อ: {pet_name} ({breed})
        - ข้อมูลจากเจ้าของ: "{user_prompt}"
        - บริบท: {objective}
        
        คำสั่ง:
        1. ดูรูปภาพประกอบ (ถ้ามี) เพื่อบรรยายลักษณะกายภาพ (สีขน, ลวดลาย, ปลอกคอ)
        2. เขียนคำบรรยายโดยใช้น้ำเสียงแบบ: {tone_desc}
        3. เรียบเรียงให้สั้นกระชับ (3-5 บรรทัด) ภาษาไทยธรรมชาติ
        4. ใส่ Emoji ให้เหมาะสมกับอารมณ์ของประกาศ
        5. หากไม่ได้บอกชื่อน้อง {pet_name} ใช้คำว่า "น้อง" แทน
        """

        content_parts = [{"type": "text", "text": prompt_text}]
        if image_part:
            content_parts.append(image_part)

        message = HumanMessage(content=content_parts)

        try:
            response = self.vision_model.invoke([message])
            return response.content
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"
    
    def analyze_pet_image(self, image_field):
        """ ให้ AI ดูรูปแล้วบอกลักษณะเด่นออกมาเป็น Text เพื่อเอาไปทำ Index """
        if not self.vision_model or not image_field:
            return ""

        try:
            # แปลงรูปเป็น Base64 (รองรับทั้ง Path และ InMemory)
            import base64
            image_data = None
            
            # กรณีเป็นไฟล์ที่ Save ลง Disk แล้ว (มี path)
            if hasattr(image_field, 'path') and os.path.exists(image_field.path):
                with open(image_field.path, "rb") as img:
                    image_data = base64.b64encode(img.read()).decode("utf-8")
            # กรณีเป็น InMemory (เช่นตอน Test หรือยังไม่ Save)
            elif hasattr(image_field, 'read'):
                image_field.seek(0)
                image_data = base64.b64encode(image_field.read()).decode("utf-8")
            
            if not image_data:
                return ""

            # Prompt สั่งให้ AI ดึง Key Visual ออกมา
            prompt = """
            จงวิเคราะห์รูปภาพสัตว์เลี้ยงนี้เพื่อใช้ในระบบค้นหา:
            1. ระบุชนิดสัตว์ (หมา, แมว, ฯลฯ)
            2. ระบุสีขนและลวดลายอย่างละเอียด (เช่น สีส้มลายสลิด, สีขาวดำลายวัว, สามสี)
            3. ระบุลักษณะเด่น (เช่น หูพับ, หางกุด, ใส่ปลอกคอสีแดง, ตาบอดข้างหนึ่ง)
            4. ไม่ต้องเขียนเป็นประโยคสวยงาม ขอแค่ Keyword สำคัญคั่นด้วย comma
            ตัวอย่าง: "แมว, สีส้ม, ลายสลิด, หางยาว, ปลอกคอสีเขียว"
            """

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            )
            
            # ส่งให้ Gemini Vision
            response = self.vision_model.invoke([message])
            print(f" AI Vision Analysis: {response.content}") # Debug ดูว่า AI เห็นอะไร
            return response.content

        except Exception as e:
            print(f" Vision Analysis Failed: {e}")
            return ""

    def ask_ai(self, user_query, user=None, history=[]):
        user_id = user.id if user and user.is_authenticated else 'Guest'
        print(f"DEBUG: กำลังค้นหาข้อมูลให้ User ID: {user_id}")
        try:
            context_text = ""
            history_text = ""
            if history:
                # เอาแค่ 5 ข้อความล่าสุดพอ (ประหยัด Token และกัน AI งงเรื่องเก่าเกินไป)
                recent_history = history[-5:] 
                for msg in recent_history:
                    sender = "User" if msg.get('sender') == 'user' else "AI"
                    message = msg.get('message', '')
                    history_text += f"{sender}: {message}\n"
            else:
                history_text = "ไม่มีประวัติการสนทนา (เริ่มต้นคุยใหม่)"

            # 1. สร้างเงื่อนไขการค้นหา (Filter)
            # กฎ: หาข้อมูลที่เป็น Public หรือ (Private และเป็นของ User คนนี้)
            where_filter = {"access": "public"} # Default: เอาแค่ Public

            if user and user.is_authenticated:
                pass 

            try:
                # Query รอบที่ 1: ข้อมูลสาธารณะ (Public)
                public_results = self.collection.query(
                    query_texts=[user_query],
                    n_results=3,
                    where={"access": "public"}
                )
                
                docs = public_results['documents'][0]

                # Query รอบที่ 2: ข้อมูลส่วนตัว (Private) - ถ้ามี user
                if user and user.is_authenticated:
                    private_results = self.collection.query(
                        query_texts=[user_query],
                        n_results=10, # เอาข้อมูลส่วนตัวมาเสริม 2 อัน
                        where={"owner_id": str(user.id)}
                    )
                    docs.extend(private_results['documents'][0])

                if docs:
                    context_text = "\n".join(docs)
                    # ปริ้นท์ออกมาดูเลยว่า AI เห็นอะไรบ้าง (เช็กตรงนี้ใน Terminal)
                    print(f"---- AI Context ({len(docs)} docs) ----")
                    print(context_text)
                    print("------------------------------------------")

            except Exception as e:
                print(f"Search Error: {e}")

            # 2. สร้าง Prompt ส่งให้ Gemini
            prompt = f"""
            คุณคือ 'Petpal AI' ผู้ช่วยอัจฉริยะสำหรับคนรักสัตว์ คุณมีนิสัยร่าเริง สุภาพ และขี้เล่นนิดๆ พูดจาเหมือนเพื่อนที่รักสัตว์ด้วยกัน พูดจาไพเราะเสมอ คุณเป็นผู้หญิง

            ประวัติการสนทนาล่าสุด:
            {history_text}

            ข้อมูลที่หาเจอ (จากฐานข้อมูล):
            {context_text}
            
            คำถามล่าสุดจากผู้ใช้: {user_query}
            
            คำแนะนำการตอบ:
            1. ตอบคำถามโดยใช้ข้อมูลข้างต้น
            2. เน้นความเป็นกันเอง สุภาพ และช่วยเหลือ
            3. ❌ ห้ามใช้สัญลักษณ์ Markdown (เช่น **ตัวหนา**, - รายการ) เด็ดขาด 
            4. ให้ตอบเป็นข้อความธรรมดา (Plain Text) เหมือนเพื่อนคุยกัน
            5. ถ้ามีการแบ่งหัวข้อ ให้ใช้การเว้นบรรทัด หรือใช้ Emoji แทน
            6. ✅ **สำคัญมาก: ถ้าแนะนำน้องตัวไหน (ที่เป็นประกาศสาธารณะ) ให้แนบ "ลิงก์ดูรายละเอียด" ของน้องตัวนั้นต่อท้ายด้วยเสมอ**
            7. ถ้าข้อมูลมาจาก "ข้อมูลสัตว์เลี้ยงส่วนตัว" ให้ตอบในลักษณะ "น้อง... ของคุณ" (ไม่ต้องแนบลิงก์)
            8. ข้อมูลที่มี Tag [สัตว์เลี้ยงของ User] คือสัตว์เลี้ยงของผู้ใช้โดยตรง
            9. ข้อมูลที่มี Tag [ประกาศสาธารณะ] คือโพสต์หาบ้านหรือสัตว์หายของคนอื่น
            10. **ถ้าผู้ใช้ถามว่า "มีสัตว์กี่ตัว" หรือ "สัตว์เลี้ยงของฉัน" ให้ตอบเฉพาะข้อมูลจาก [สัตว์เลี้ยงของ User] เท่านั้น**
            11. หากเป็นข้อมูลสัตว์เลี้ยงส่วนตัว ให้ใช้คำแทนตัวว่า "น้อง..." หรือชื่อของสัตว์เลี้ยง
            12. ⚠️ หากเป็นเรื่องอาการป่วย ให้แนะนำเบื้องต้นและย้ำว่า "ควรปรึกษาสัตวแพทย์" เสมอ
            13. หากไม่พบข้อมูล ให้ตอบว่า "ขอโทษด้วยครับ ผมไม่ข้อมูลเรื่องนี้ในระบบเลย" อย่างสุภาพ
            14. ตอบสั้นๆ ไม่เกิน 3 ประโยค และ ไม่ต้องเอาลิงค์ดูรายละเอียดมาให้ แนะนำให้ผู้ใช้งานกดปุ่มเอไอเต็มจอแทน
            """
            
            # ให้ Gemini ตอบ
            if self.llm:
                return self.llm.invoke(prompt)
            return "ระบบยังไม่พร้อมใช้งาน (No API Key)"
            
        except Exception as e:
            print(f"Ask AI Error: {e}")
            return "ขออภัย ระบบขัดข้องชั่วคราว"

    def ask_ai_stream(self, user_query, user=None, history=[]):
        """ ฟังก์ชันสำหรับ Streaming Response (Generator) """    
        user_id = user.id if user and user.is_authenticated else 'Guest'
        
        # 1. เตรียม Context (ใช้ Logic เดียวกับ ask_ai เดิม)
        context_text = ""
        try:
            # Query ข้อมูล Public
            public_docs = []
            public_results = self.collection.query(query_texts=[user_query], n_results=3, where={"access": "public"})
            if public_results['documents']:
                public_docs = [f"[ประกาศสาธารณะ]: {d}" for d in public_results['documents'][0]]

            # Query ข้อมูล Private
            private_docs = []
            if user and user.is_authenticated:
                private_results = self.collection.query(query_texts=[user_query], n_results=5, where={"owner_id": str(user.id)})
                if private_results['documents']:
                    private_docs = [f"[สัตว์เลี้ยงของ User]: {d}" for d in private_results['documents'][0]]
            
            context_text = "\n\n".join(public_docs + private_docs)
            
        except Exception as e:
            print(f"Stream Search Error: {e}")

        # 2. เตรียม History
        history_text = ""
        if history:
            for msg in history[-5:]:
                sender = "User" if msg.get('sender') == 'user' else "AI"
                history_text += f"{sender}: {msg.get('message', '')}\n"

        # 3. สร้าง Prompt (เหมือนเดิม)
        prompt = f"""
        คุณคือ 'Petpal AI' ผู้ช่วยอัจฉริยะสำหรับคนรักสัตว์ คุณมีนิสัยร่าเริง สุภาพ และขี้เล่นนิดๆ พูดจาเหมือนเพื่อนที่รักสัตว์ด้วยกัน พูดจาไพเราะเสมอ คุณเป็นผู้หญิง
        
        📜 ประวัติการสนทนา:
        {history_text}
        
        📚 ข้อมูลอ้างอิง:
        {context_text}
        
        💬 คำถาม: {user_query}
        
        คำแนะนำ:
        1. ตอบคำถามโดยใช้ข้อมูลข้างต้น
        2. เน้นความเป็นกันเอง สุภาพ และช่วยเหลือ
        3. ❌ ห้ามใช้สัญลักษณ์ Markdown (เช่น **ตัวหนา**, - รายการ) เด็ดขาด 
        4. ให้ตอบเป็นข้อความธรรมดา (Plain Text) เหมือนเพื่อนคุยกัน
        5. ถ้ามีการแบ่งหัวข้อ ให้ใช้การเว้นบรรทัด หรือใช้ Emoji แทน
        6. ✅ **สำคัญมาก: ถ้าแนะนำน้องตัวไหน (ที่เป็นประกาศสาธารณะ) ให้แนบ "ลิงก์ดูรายละเอียด" ของน้องตัวนั้นต่อท้ายด้วยเสมอ**
        7. ถ้าข้อมูลมาจาก "ข้อมูลสัตว์เลี้ยงส่วนตัว" ให้ตอบในลักษณะ "น้อง... ของคุณ" (ไม่ต้องแนบลิงก์)
        8. ข้อมูลที่มี Tag [สัตว์เลี้ยงของ User] คือสัตว์เลี้ยงของผู้ใช้โดยตรง
        9. ข้อมูลที่มี Tag [ประกาศสาธารณะ] คือโพสต์หาบ้านหรือสัตว์หายของคนอื่น
        10. **ถ้าผู้ใช้ถามว่า "มีสัตว์กี่ตัว" หรือ "สัตว์เลี้ยงของฉัน" ให้ตอบเฉพาะข้อมูลจาก [สัตว์เลี้ยงของ User] เท่านั้น**
        11. หากเป็นข้อมูลสัตว์เลี้ยงส่วนตัว ให้ใช้คำแทนตัวว่า "น้อง..." หรือชื่อของสัตว์เลี้ยง
        12. ⚠️ หากเป็นเรื่องอาการป่วย ให้แนะนำเบื้องต้นและย้ำว่า "ควรปรึกษาสัตวแพทย์" เสมอ
        13. หากไม่พบข้อมูล ให้ตอบว่า "ขอโทษด้วยครับ ผมไม่ข้อมูลเรื่องนี้ในระบบเลย" อย่างสุภาพ
        """

        # 4. เรียก LLM แบบ Streaming (สำคัญ! ใช้ .stream แทน .invoke)
        if self.llm:
            try:
                # ส่งข้อมูลทีละก้อน (Chunk)
                for chunk in self.llm.stream(prompt):
                    yield chunk 
            except Exception as e:
                yield f"เกิดข้อผิดพลาด: {str(e)}"
        else:
            yield "ระบบยังไม่พร้อมใช้งาน (No API Key)"

    def clear_knowledge(self):
        try: 
            # ลบและสร้างใหม่ (Reset)
            self.chroma_client.delete_collection("petpal_collection")
            self.collection = self.chroma_client.get_or_create_collection(name="petpal_collection")
            print(" Re-initialized Collection")
        except Exception as e:
            print(f" Error re-initializing: {e}")

    def delete_post_from_rag(self, post_id):
        try:
            if self.collection:
                self.collection.delete(ids=[f"post_{post_id}"])
                print(f" Deleted post {post_id} from AI memory.")
        except Exception as e:
            print(f" Delete Error: {e}")

rag_service = RAGService()