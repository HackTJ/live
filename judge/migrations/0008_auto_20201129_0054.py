# Generated by Django 3.1.3 on 2020-11-29 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0007_project_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotator',
            name='next',
        ),
        migrations.AddField(
            model_name='annotator',
            name='current',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='annotator_current', to='judge.project'),
        ),
    ]
