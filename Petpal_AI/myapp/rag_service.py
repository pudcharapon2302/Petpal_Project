import os
import chromadb
from django.conf import settings
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
from chromadb.config import Settings

load_dotenv()

class RAGService:
    def __init__(self):
        self.api_key = "AIzaSyABlI_5tcVNockcXQz6WOkPnVzaxBUetoQ"  #os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("⚠️ Warning: GOOGLE_API_KEY not found.")
        
        # 1. ตั้งค่า Gemini & Embedding
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.api_key
        )
        self.llm = GoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7
        )

        # 2. เชื่อมต่อ ChromaDB (PersistentClient)
        try:
            self.chroma_client = chromadb.HttpClient(
                host=os.environ.get("CHROMA_HOST", "chroma_db"), 
                port=int(os.environ.get("CHROMA_PORT", 8000)),
                settings=Settings(anonymized_telemetry=False)
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
            
            # --- ZONE 1: พยายามค้นหาข้อมูล (RAG) ---
            try:
                if self.vector_store:
                    # ลองค้นหาดู
                    docs = self.vector_store.similarity_search(user_query, k=3)
                    if docs:
                        context_text = "\n".join([d.page_content for d in docs])
                        print(f" Found context for: {user_query}")
            except Exception as e:
                # ⚠️ ถ้าค้นหาพัง (เช่น โควตา Embedding เต็ม) -> ให้ข้ามไปเลย อย่า Error ใส่หน้าผู้ใช้
                print(f" Embedding/Search Error (Skipping RAG): {e}")
                context_text = "" # ตั้งค่าว่าง ไว้คุยเปล่าๆ

            # --- ZONE 2: สร้าง Prompt ---
            # ถ้ามีข้อมูล ก็ใส่ข้อมูล, ถ้าไม่มี ก็บอกว่าไม่มี
            intro = "ข้อมูลอ้างอิงจากระบบ:" if context_text else ""
            
            prompt = f"""
            คุณคือ 'Petpal AI' ผู้ช่วยอัจฉริยะประจำเว็บไซต์ Petpal
            
            {intro}
            {context_text}
            
            คำถามจากผู้ใช้: {user_query}
            
            ตอบคำถามอย่างเป็นมิตรและสุภาพ:
            """
            
            # --- ZONE 3: ให้ AI ตอบ (Generation) ---
            # ส่วนนี้ใช้โควตาแยกกับ Embedding มักจะไม่เต็มง่ายๆ
            response = self.llm.invoke(prompt)
            return response
            
        except Exception as e:
            print(f" AI Critical Error: {e}")
            return "ขออภัยครับ ระบบ AI กำลังประมวลผลหนัก โปรดลองใหม่ในอีกสักครู่"

    def add_documents(self, documents: list[Document]):
        """รับ list ของ Document objects แล้วเพิ่มเข้า vector store."""
        if not self.vector_store:
            raise Exception("Vector store is not initialized.")
        
        # LangChain's Chroma wrapper จะจัดการเรื่อง embedding ให้เอง
        self.vector_store.add_documents(documents)
        print(f"Successfully added {len(documents)} documents.")

    def add_post_to_rag(self, post):
        # (ฟังก์ชันสำหรับเทรนข้อมูล - ใส่ไว้เพื่อให้ครบองค์ประกอบ)
        try:
            text = f"ประกาศ: {post.get_post_type_display()}\nสัตว์: {post.pet.name} ({post.pet.animal.breed})\nรายละเอียด: {post.description}\nติดต่อ: {post.contact_phone}"
            doc = Document(page_content=text, metadata={"id": post.id})
            self.vector_store.add_documents([doc])
        except: pass
    
    def clear_knowledge(self):
        try: self.vector_store.delete_collection() 
        except: pass

# สร้างตัวแปร instance ไว้ให้ views.py เรียกใช้
rag_service = RAGService()