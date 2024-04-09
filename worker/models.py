from django.db import models


class Flat(models.Model):
    title = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    link = models.URLField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.title


class Image(models.Model):
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE,
                             related_name='images')
    image = models.ImageField(upload_to='flats/%Y/5%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image.url

