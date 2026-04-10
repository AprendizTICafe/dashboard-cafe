# Generated migration to fix LastUpdatetByID typo

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RH', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investigationprocess',
            old_name='LastUpdatetByID',
            new_name='LastUpdatedByID',
        ),
    ]
