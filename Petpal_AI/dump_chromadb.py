import json
from myapp.rag_service import rag_service

def run():
    print("⏳ กำลังดึงข้อมูลจาก ChromaDB...")
    
    # ดึงข้อมูลทั้งหมด (ถ้าอยากได้ Vector ด้วย ให้เพิ่ม 'embeddings' เข้าไปใน list)
    all_data = rag_service.collection.get(
        include=["documents", "metadatas"] 
    )

    total_items = len(all_data['ids'])

    if total_items == 0:
        print("⚠️ ไม่พบข้อมูลในระบบ")
        return

    # บันทึกเป็นไฟล์ JSON
    file_name = 'chromadb_backup.json'
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Dump ข้อมูลสำเร็จจำนวน {total_items} รายการ!")
    print(f"📁 บันทึกไฟล์ไว้ที่: {file_name}")

if __name__ == "__main__":
    run()