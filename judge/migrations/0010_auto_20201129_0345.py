# Generated by Django 3.1.3 on 2020-11-29 03:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('judge', '0009_auto_20201129_0338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotator',
            name='id',
        ),
        migrations.AlterField(
            model_name='annotator',
            name='judge',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]