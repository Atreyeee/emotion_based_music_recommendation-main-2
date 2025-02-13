from rest_framework import serializers
from .models import *

class NeutralSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = neutral
        fields = ['id', 'title', 'artist', 'audio_file', 'image', 'duration']
        
class HappySongSerializer(serializers.ModelSerializer):
    class Meta:
        model = happy
        fields = ['id', 'title', 'artist', 'audio_file', 'image', 'duration']
        
        
class FearSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = fear
        fields = ['id', 'title', 'artist', 'audio_file', 'image', 'duration']
        
class SadSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = sad
        fields = ['id', 'title', 'artist', 'audio_file', 'image', 'duration']
        
class SurpriseSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = surprise
        fields = ['id', 'title', 'artist', 'audio_file', 'image', 'duration']
        
class AngrySongSerializer(serializers.ModelSerializer):
    class Meta:
        model = angry
        fields = ['id', 'title', 'artist', 'audio_file', 'image', 'duration']
