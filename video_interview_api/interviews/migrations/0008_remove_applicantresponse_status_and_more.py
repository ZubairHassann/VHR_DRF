# Generated by Django 5.1.6 on 2025-02-26 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0007_applicant_created_at_interview_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicantresponse',
            name='status',
        ),
        migrations.AddField(
            model_name='applicantresponse',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
