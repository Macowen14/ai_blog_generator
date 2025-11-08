from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="author_profile"
    )
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    social_x = models.URLField(blank=True, null=True)
    social_github = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Blog(models.Model):
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="blogs"
    )
    title = models.CharField(max_length=255)
    youtube_url = models.URLField()
    transcript = models.TextField(blank=True, null=True)
    content = models.CharField()  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
