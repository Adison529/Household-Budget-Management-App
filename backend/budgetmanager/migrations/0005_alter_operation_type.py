# Generated by Django 5.0.6 on 2024-06-17 15:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgetmanager', '0004_alter_operation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='budgetmanager.operationtype'),
        ),
    ]
