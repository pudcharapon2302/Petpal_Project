from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from myapp.models import Animal, Foundation, Pet, Post, User


class Command(BaseCommand):
    help = "Create repeatable demo data for Petpal AI local development."

    def handle(self, *args, **options):
        demo_user, _ = User.objects.get_or_create(
            username="petpal_demo",
            defaults={
                "email": "demo@petpal.local",
                "first_name": "Petpal",
                "last_name": "Demo",
                "phone": "0800000000",
                "address": "Bangkok, Thailand",
            },
        )
        demo_user.set_unusable_password()
        demo_user.save(update_fields=["password"])

        cat, _ = Animal.objects.get_or_create(species="CAT", breed="Domestic Shorthair")
        dog, _ = Animal.objects.get_or_create(species="DOG", breed="Thai Ridgeback Mix")

        samples = [
            {
                "name": "Mali",
                "animal": cat,
                "gender": "FEMALE",
                "post_type": "LOST",
                "description": "Friendly orange-and-white cat wearing a blue collar. Demo listing.",
                "location": "Lumphini Park",
                "tambon": "Lumphini",
                "amphoe": "Pathum Wan",
                "province": "Bangkok",
                "latitude": 13.730556,
                "longitude": 100.541667,
            },
            {
                "name": "Khao Niao",
                "animal": dog,
                "gender": "MALE",
                "post_type": "LOST",
                "description": "Medium-sized brown dog with a white chest. Demo listing.",
                "location": "Chatuchak Park",
                "tambon": "Chatuchak",
                "amphoe": "Chatuchak",
                "province": "Bangkok",
                "latitude": 13.807778,
                "longitude": 100.555278,
            },
            {
                "name": "Som Som",
                "animal": cat,
                "gender": "MALE",
                "post_type": "ADOPTION",
                "description": "Calm and affectionate cat looking for a loving home. Demo listing.",
                "location": "Benchasiri Park",
                "tambon": "Khlong Tan",
                "amphoe": "Khlong Toei",
                "province": "Bangkok",
                "latitude": 13.730000,
                "longitude": 100.569722,
            },
        ]

        for sample in samples:
            pet, _ = Pet.objects.get_or_create(
                owner=demo_user,
                name=sample["name"],
                defaults={
                    "animal": sample["animal"],
                    "gender": sample["gender"],
                    "birth_date": date(2022, 1, 1),
                    "description": sample["description"],
                    "contact_phone": demo_user.phone,
                },
            )
            Post.objects.update_or_create(
                pet=pet,
                user=demo_user,
                post_type=sample["post_type"],
                defaults={
                    "description": sample["description"],
                    "lost_location": sample["location"],
                    "tambon": sample["tambon"],
                    "amphoe": sample["amphoe"],
                    "province": sample["province"],
                    "latitude": sample["latitude"],
                    "longitude": sample["longitude"],
                    "contact_phone": demo_user.phone,
                    "lost_date": timezone.localdate() if sample["post_type"] == "LOST" else None,
                    "is_active": True,
                },
            )

        Foundation.objects.update_or_create(
            name="Petpal Demo Animal Support",
            defaults={
                "org_type": "FOUNDATION",
                "description": "Demo organization for local development.",
                "address": "Bangkok, Thailand",
                "phone": "020000000",
                "email": "support@petpal.local",
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Petpal demo data is ready."))
