from rest_framework import serializers

from .models import Flat, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = 'image', 'created_at', 'updated_at'


class FlatSerializer(serializers.ModelSerializer):
    # images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Flat
        fields = ('title', 'price', 'link', 'images')



