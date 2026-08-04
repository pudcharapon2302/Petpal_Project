from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0019_post_birth_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="latitude"),
        ),
        migrations.AddField(
            model_name="post",
            name="longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="longitude"),
        ),
    ]
