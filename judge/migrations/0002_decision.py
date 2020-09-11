# Generated by Django 3.0.8 on 2020-09-02 22:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('judge', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('judge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('loser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decision_loser', to='judge.Project')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decision_winner', to='judge.Project')),
            ],
        ),
    ]
