import os
import chromadb
from django.conf import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        # ---------------------------------------------------------
        # 1. ตั้งค่า Local Embedding (CPU)
        # ---------------------------------------------------------
        print(" Loading Local Embedding Model (CPU)...")
        # รุ่นนี้ (paraphrase-multilingual) เก่งภาษาไทยและเบา
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'}, # บังคับใช้ CPU
            encode_kwargs={'normalize_embeddings': False}
        )
        print(" Local Model Loaded!")

        # ---------------------------------------------------------
        # 2. ตั้งค่า Gemini Chat (LLM)
        # ---------------------------------------------------------
        if self.api_key:
            self.llm = GoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.7
            )
        else:
            print(" Warning: GOOGLE_API_KEY not found.")
            self.llm = None

        # 3. เชื่อมต่อ ChromaDB
        try:
            self.chroma_client = chromadb.HttpClient(
                host=os.environ.get("CHROMA_HOST", "chroma_db"), 
                port=int(os.environ.get("CHROMA_PORT", 8000))
            )
            
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name="petpal_collection",
                embedding_function=self.embeddings,
            )
            print(" RAG Service Initialized")
        except Exception as e:
            print(f" ChromaDB Error: {e}")
            self.vector_store = None

    def ask_ai(self, user_query):
        try:
            context_text = ""
            try:
                if self.vector_store:
                    # ค้นหาข้อมูล (ใช้ Local Embedding ทำงานในเครื่อง)
                    docs = self.vector_store.similarity_search(user_query, k=3)
                    if docs:
                        context_text = "\n".join([d.page_content for d in docs])
            except Exception as e:
                print(f"Search Error: {e}")

            intro = "ข้อมูลอ้างอิงจากระบบ:" if context_text else ""
            prompt = f"""
            คุณคือ 'Petpal AI' ผู้ช่วยอัจฉริยะ
            {intro}
            {context_text}
            คำถาม: {user_query}
            ตอบคำถามอย่างเป็นมิตรและสุภาพ:
            """
            
            # ให้ Gemini ตอบ (ใช้โควตา Chat ซึ่งไม่ค่อยเต็ม)
            if self.llm:
                return self.llm.invoke(prompt)
            return "ระบบยังไม่พร้อมใช้งาน (No API Key)"
            
        except Exception as e:
            return "ขออภัย ระบบขัดข้องชั่วคราว"

    def add_post_to_rag(self, post):
        try:
            text = f"ประกาศ: {post.get_post_type_display()}\nสัตว์: {post.pet.name} ({post.pet.animal.breed})\nรายละเอียด: {post.description}\nติดต่อ: {post.contact_phone}"
            doc = Document(page_content=text, metadata={"id": str(post.id)})
            self.vector_store.add_documents([doc])
        except: pass
    
    def clear_knowledge(self):
        try: self.vector_store.delete_collection() 
        except: pass

    def delete_post_from_rag(self, post_id):
        """ ลบข้อมูลโพสต์ออกจากสมอง AI """
        try:
            if not self.vector_store: return
            self.vector_store._collection.delete(
                where={"id": str(post_id)}
            )
            print(f"🗑️ Deleted post {post_id} from AI memory.")
            
        except Exception as e:
            print(f"⚠️ Delete Error: {e}")

rag_service = RAGService()