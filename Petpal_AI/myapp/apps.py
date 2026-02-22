import os
from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

class Embedding(AppConfig): # ชื่อคลาสจะเป็นไปตามที่คุณตั้งไว้
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp' # ชื่อแอปของคุณ

    def ready(self):
        # ป้องกันไม่ให้ Django โหลดโมเดลเบิ้ล 2 รอบตอนใช้คำสั่ง runserver
        if os.environ.get('RUN_MAIN') == 'true':
            # import rag_service มาเรียกใช้งาน
            from .rag_service import rag_service
            rag_service.setup_models()