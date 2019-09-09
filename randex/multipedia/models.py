from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify


class Page(models.Model):
    """Represents a wiki article"""

    subject = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=50)
    text = models.TextField()

    def __str__(self):
        return self.subject

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.subject)
        super(Page, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail_page', args=(self.slug,))
