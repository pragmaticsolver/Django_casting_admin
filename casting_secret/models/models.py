from django.db import models
from django.utils.translation import ugettext_lazy as _

from CastingSecret.settings.base import MANAGED


class TalentCategories(models.Model):
    name_en = models.CharField(max_length=150, null=False)
    name_ar = models.CharField(max_length=150, null=False)

    class Meta:
        managed = MANAGED
        ordering = ['name_en']
        db_table = 'talent_categories'
        verbose_name = 'Talent Category'
        unique_together = ['name_en', 'name_ar']
        verbose_name_plural = 'Talent Categories'

    def __str__(self):
        return self.name_en


class Subscription(models.Model):
    email = models.EmailField(_('Email'), max_length=100, blank=False)

    def __str__(self):
        return self.email
