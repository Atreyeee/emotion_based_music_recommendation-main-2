from django.db import models

# Create your models here.
class neutral(models.Model):
    title = models.TextField()
    artist = models.TextField()
    image= models.ImageField()
    audio_file=models.FileField()
    audio_link = models.CharField(max_length=200,blank=True,null=True)
    lyrics = models.TextField(blank=True,null=True,default="No lyrics is available for this songs")
    duration=models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
class happy(models.Model):
    title = models.TextField()
    artist = models.TextField()
    image= models.ImageField()
    audio_file=models.FileField()
    audio_link = models.CharField(max_length=200,blank=True,null=True)
    lyrics = models.TextField(blank=True,null=True,default="No lyrics is available for this songs")
    duration=models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
class sad(models.Model):
    title = models.TextField()
    artist = models.TextField()
    image= models.ImageField()
    audio_file=models.FileField()
    audio_link = models.CharField(max_length=200,blank=True,null=True)
    lyrics = models.TextField(blank=True,null=True,default="No lyrics is available for this songs")
    duration=models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
class fear(models.Model):
    title = models.TextField()
    artist = models.TextField()
    image= models.ImageField()
    audio_file=models.FileField()
    audio_link = models.CharField(max_length=200,blank=True,null=True)
    lyrics = models.TextField(blank=True,null=True,default="No lyrics is available for this songs")
    duration=models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
class surprise(models.Model):
    title = models.TextField()
    artist = models.TextField()
    image= models.ImageField()
    audio_file=models.FileField()
    audio_link = models.CharField(max_length=200,blank=True,null=True)
    lyrics = models.TextField(blank=True,null=True,default="No lyrics is available for this songs")
    duration=models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
class angry(models.Model):
    title = models.TextField()
    artist = models.TextField()
    image= models.ImageField()
    audio_file=models.FileField()
    audio_link = models.CharField(max_length=200,blank=True,null=True)
    lyrics = models.TextField(blank=True,null=True,default="No lyrics is available for this songs")
    duration=models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
    