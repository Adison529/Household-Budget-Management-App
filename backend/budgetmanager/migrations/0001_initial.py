# Generated by Django 5.0.6 on 2024-06-13 16:01

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OperationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OperationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=7, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_budgetmanagers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('income', 'Income'), ('expense', 'Expense')], max_length=7)),
                ('date', models.DateField()),
                ('title', models.CharField(max_length=128)),
                ('value', models.DecimalField(decimal_places=2, max_digits=8)),
                ('budget_manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='budgetmanager.budgetmanager')),
                ('by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='operations', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='budgetmanager.operationcategory')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('read_only', 'Read Only'), ('edit', 'Edit')], max_length=10)),
                ('budget_manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='budgetmanager.budgetmanager')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'budget_manager')},
            },
        ),
    ]
