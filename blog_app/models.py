from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils.html import strip_tags
import math


class User(AbstractUser):
    bio=models.CharField(max_length=500,blank=True, null=True)
    profile=models.FileField(upload_to='medias',blank=True, null=True)
    role_choices=[
        ('reader','reader'),
        ('writer','writer'),
    ]
    role=models.CharField(max_length=100,choices=role_choices,default='reader')

    followers=models.ManyToManyField('self',symmetrical=False,related_name='following',blank=True)

    def __str__(self):
        return self.username

class Blog(models.Model):
    writer=models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={'role':'writer'})
    blog_title=models.CharField(max_length=100)
    category_options=[
        ('Technology','Technology'),
        ('Lifestyle','Lifestyle'),
        ('Travel','Travel'),
        ('Food','Food'),
        ('Education','Education'),
        ('Other','Other'),
    ]
    category=models.CharField(max_length=100,choices=category_options)

    status_options=[
        ('draft','Draft'),
        ('published','Published'),
    ]
    status=models.CharField(max_length=100,choices=status_options,default='draft')
    content=models.CharField(max_length=1000)
    image=models.FileField(upload_to='medias')
    created_at=models.DateTimeField(auto_now_add=True)
    reading_time=models.PositiveBigIntegerField(default=1)


    def __str__(self):
        return self.blog_title
    
    def like_count(self):
        return self.likes.filter(is_like=True).count()

    def dislike_count(self):
        return self.likes.filter(is_like=False).count()

    def save(self,*args,**kwargs):
        text=strip_tags(self.content)
        word_count=len(text.split())
        self.reading_time=max(1,math.ceil(word_count/150))
        super().save(*args,**kwargs)



    
class BlogLike(models.Model):
    blog=models.ForeignKey(Blog,related_name='likes',on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    is_like=models.BooleanField()#True=Like,False=Dislike

    class Meta:
        unique_together=('blog','user')

class Comments(models.Model):
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE, related_name='comments')
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    comment=models.CharField(max_length=500)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.blog.blog_title}"
    

class Bookmark(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name="bookmarks")
    blog=models.ForeignKey('Blog', on_delete=models.CASCADE,related_name="bookmarked_by")

    class Meta:
        unique_together=('user','blog')

