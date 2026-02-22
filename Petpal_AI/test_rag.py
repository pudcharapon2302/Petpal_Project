from myapp.rag_service import rag_service

# ❌ ลบบรรทัด rag_service.setup_models() ออกไปเลย เพราะใน rag_service.py ของคุณ โมเดลถูกโหลดเสร็จแล้วตั้งแต่บรรทัด rag_service = RAGService()

queries = [
    "ประกาศตามหาสุนัขพันธุ์ชิสุ สีขาว ขนยาว หาย",
    "สุนัขพันธุ์ไทย สีน้ำตาล ใส่ปลอกคอสีแดง หาย",
    "แมวเปอร์เซีย สีส้ม ขนยาว หาย",
    "แมวไทย สีดำ ตาสีเขียว หาย",
    "สุนัขพันธุ์ปอม สีขาว ขนฟู หาย",
    "แมวลายส้มขาว หาย",
    "สุนัขพันธุ์บางแก้ว สีขาวดำ หาย",
    "แมวสามสี เพศเมีย หาย",
    "หาบ้านให้ลูกแมวสีส้ม สุขภาพดี",
    "สุนัขเพศเมีย ทำหมันแล้ว หาบ้าน"
]

for k in [1, 2, 3, 4, 5]:
    print("\n==========================")
    print("ทดสอบ n_results =", k)
    print("==========================")

    for q in queries:
        # 1. แปลงข้อความคำถามให้เป็น Vector ก่อนส่งให้ ChromaDB
        query_vector = rag_service.embeddings.embed_query(q)

        # 2. เปลี่ยนจาก query_texts เป็น query_embeddings
        results = rag_service.collection.query(
            query_embeddings=[query_vector], # ใช้ Vector ที่แปลงแล้ว
            n_results=k,
            where={"access": "public"}
        )

        ids = results.get("ids", [[]])[0]
        print(q)
        print("Retrieved:", ids)
        print("-------------------")