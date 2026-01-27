from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.http import HttpResponse
from .models import User,Blog,Comments,BlogLike,Bookmark
from django.contrib import messages 
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings


class LogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logout successful")
        return redirect("login")

class ReaderRegisterView(View):
    def get(self,request):
        return render(request,'reader_register.html')

    def post(self,request):
        name=request.POST.get("fullname")
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')

        # validation
        # if not (username and email and password):
        #     return render(request,'reader_register.html', {'error': 'All fields are required'})

        if User.objects.filter(username=username).exists():
            return render(request,'reader_register.html',{'error':'Username already exists'})

        user=User(
            first_name=name,
            username=username,
            email=email,
            password=make_password(password),
            role='reader'
        )
        user.save()
        return redirect('login')


class WriterRegisterView(View):
    def get(self, request):
        return render(request,'writer_register.html')

    def post(self,request):
        name=request.POST.get('firstname')
        email=request.POST.get('email')
        username=request.POST.get('username')
        password=request.POST.get('password')
        bio=request.POST.get('bio')
        profile=request.FILES.get('profile')

        # if not (username and email and password):
        #     return render(request,'writer_register.html', {'error': 'All fields are required'})

        if User.objects.filter(username=username).exists():
            return render(request,'writer_register.html',{'error':'Username already exists'})

        user=User(
            first_name=name,
            username=username,
            email=email,
            password=make_password(password),
            bio=bio,
            profile=profile,
            role='writer'
        )
        user.save()
        return redirect('login')


class LoginView(View):
    def get(self,request):
        return render(request,'login.html')
    
    def post(self,request):
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)

        if user:
            login(request,user)
            messages.success(request,'Login successful')
            if user.role=='reader':
                return redirect('reader-home')
            elif user.role=='writer':
                return redirect('writer-home')
            else:
                pass
        else:
            return redirect('login')
    


class ReaderHome(View):
    def get(self, request):
        blogs=Blog.objects.filter(status='published').order_by('-created_at')
        #categories for dropdown
        categories=Blog.objects.values_list('category',flat=True).distinct()
        # search query
        query=request.GET.get('q','')
        if query:
            blogs=blogs.filter(
                Q(blog_title__icontains=query) |
                Q(writer__first_name__icontains=query) |
                Q(category__icontains=query)
            )
        #category filter
        selected_category=request.GET.get('category','')
        if selected_category:
            blogs=blogs.filter(category=selected_category)
        #bookmarks
        if request.user.is_authenticated:
            bookmarked_ids=Bookmark.objects.filter(user=request.user).values_list('blog_id',flat=True)
        else:
            bookmarked_ids=[]

        return render(request,'readers_home.html',{
            'blogs':blogs,
            'category':categories,
            'query':query,
            'selected_category':selected_category,
            'bookmarked_ids':bookmarked_ids
        })

def search_suggestions(request):
    query=request.GET.get('q','')
    suggestions=[]
    if query:
        blogs=Blog.objects.filter(
            Q(blog_title__icontains=query) |
            Q(writer__first_name__icontains=query) |
            Q(category__icontains=query),
            status='published'
        )[:5] #limit suggestions
        for blog in blogs:
            suggestions.append(blog.blog_title)
    return JsonResponse(suggestions,safe=False)


@method_decorator(login_required(login_url='login'), name='dispatch')
class ReaderBlogDetailView(View):
    def get(self,request,**kwargs): 
        blogs=Blog.objects.get(id=kwargs.get("id"))
        comments=Comments.objects.filter(blog=blogs).order_by('-created_at')
        return render(request,'reader_blog_detaile.html',{'blog':blogs,'comments':comments})

    
class WriterHome(View):
    def get(self,request):
        writer=request.user
        blog=Blog.objects.filter(writer=writer,status='published')
        b_count=blog.count()
        c_count = Comments.objects.filter(blog__writer=writer).count()
        followers_count=writer.followers.count()
        return render(request,'writers_home.html',{
            'writer':writer,
            'blogs':blog,
            'blog_count':b_count,
            'c_count':c_count,
            'f_count':followers_count
            })
    

class WriterDashboard(View):
    def get(self,request):
        writer=request.user
        followers=writer.followers.count()
        total_blogs=Blog.objects.filter(writer=writer,status='published').count()
        total_comments = Comments.objects.filter(blog__writer=writer).count()
        like_count=BlogLike.objects.filter(blog__writer=request.user,is_like=True).count()
        dislike_count=BlogLike.objects.filter(blog__writer=request.user,is_like=False).count()

        return render(request,'statistics.html',
                      {
                        'followers':followers,
                        'blogs':total_blogs,
                        'comments':total_comments,
                        'like_count':like_count,
                        'dislike_count':dislike_count
                       })
    
class WriterBlogs(View):
    def get(self,request,**kwargs):
        blog=Blog.objects.get(id=kwargs.get("id"))
        comments=Comments.objects.filter(blog=blog)
        return render(request,'writer_blogs.html',{'blog':blog,'comments':comments})
    
class BlogUpdateView(View):
    def get(self,request,**kwargs):
        blog=Blog.objects.get(id=kwargs.get("id"),writer=request.user)
        return render(request,'update_blog.html',{'blog':blog})
    
    def post(self,request,**kwargs):
        blog=Blog.objects.get(id=kwargs.get("id"),writer=request.user)
        title=request.POST.get("title")
        category=request.POST.get("category")
        content=request.POST.get("content")
        image=request.FILES.get("cover-image")

        blog.blog_title=title
        blog.category=category
        blog.content=content
        if image:
            blog.image=image
        blog.save()
        messages.success(request,"Blog updated successfully!")
        return redirect('writer-blogs',id=blog.id)
        

class DeleteBlogView(View):
    def get(self,request,**kwargs):
        blog=Blog.objects.get(id=kwargs.get("id"))
        blog.delete()
        messages.success(request,"Blog deleted successfully!")
        return redirect('writer-home')

        
class WriterAddBlogView(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request,'add_blog.html')
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        writer=request.user
        title=request.POST.get("title")
        category=request.POST.get("category")
        content=request.POST.get("content")
        cover_image=request.FILES.get("cover-image")
        status=request.POST.get("status")

        blog=Blog(
            writer=writer,
            blog_title=title,
            category=category,
            content=content,
            image=cover_image,
            status=status
        )
        blog.save()
        messages.success(request,"New blog added ")
        return redirect('writer-home')
    


class PostComment(View):
    def post(self,request,**kwargs):
        user=request.user
        blog=Blog.objects.get(id=kwargs.get("id"))
        comment_text=request.POST.get("comment")

        if comment_text and comment_text.strip():
            Comments.objects.create(
                user=user,
                blog=blog,
                comment=comment_text
            )
            messages.success(request,"Your comment has been posted successfully!")
        else:
            messages.warning(request,"Comment cannot be empty or just spaces!")
        return redirect('reader-blog_detail',id=blog.id)

class RenderWriters(View):
    def get(self,request):
        writers=User.objects.filter(role='writer')
        return render(request,'r-writers_list.html',{'writers':writers})


class SpecificWriter(LoginRequiredMixin, View):
    login_url='/login/'
    def get(self,request,**kwargs):
        writer=get_object_or_404(User, id=kwargs.get("id"))
        blogs=Blog.objects.filter(writer=writer,status="published")
        blogs_count=blogs.count()
        is_following=request.user in writer.followers.all()
        followers_count=writer.followers.count()
        return render(request,'r-writerdetail.html',{
            'writer':writer,
            'blogs':blogs,
            'is_following':is_following,
            'followers_count':followers_count,
            'blogs_count':blogs_count
        })

    def post(self,request,**kwargs):
        writer=get_object_or_404(User,id=kwargs.get("id"))
        user=request.user
        if user!=writer:
            if user in writer.followers.all():
                writer.followers.remove(user)
            else:
                writer.followers.add(user)
        return redirect('writer',id=writer.id)
    
class BlogLikeDislikeView(LoginRequiredMixin, View):
    def post(self,request,blog_id):
        blog=get_object_or_404(Blog, id=blog_id)
        action=request.POST.get('action')

        like_obj, created=BlogLike.objects.get_or_create(
            blog=blog,
            user=request.user,
            defaults={'is_like':action=='like'}
        )

        if not created:
            if like_obj.is_like and action=='like':
                like_obj.delete()  # unlike
            elif not like_obj.is_like and action=='dislike':
                like_obj.delete()  # undislike
            else:
                like_obj.is_like=action=='like'
                like_obj.save()

        return JsonResponse({'likes':blog.like_count(),'dislikes':blog.dislike_count()})


class BookmarkView(LoginRequiredMixin, View):
    login_url='login'

    def post(self, request, blog_id):
        blog=get_object_or_404(Blog, id=blog_id)

        bookmark,created=Bookmark.objects.get_or_create(
            user=request.user,
            blog=blog
        )
        if not created:
            bookmark.delete()
            return JsonResponse({"saved": False})

        return JsonResponse({"saved": True})
    
class BookmarkList(View):
    def get(self,request):
        saved_blogs=Bookmark.objects.filter(user=request.user)
        return render(request,'bookmarks_list.html',{'saved_blogs':saved_blogs})


class WriterDraftView(View):
    def get(self,request):
        writer=request.user
        drafted_blogs=Blog.objects.filter(status='draft',writer=writer)
        return render(request,'draft.html',{'drafted_blogs':drafted_blogs})
    
class PublishDraft(View):
    def post(self,request,**kwargs):
        blog=Blog.objects.get(id=kwargs.get('id'))
        blog.status='published'
        blog.save()
        return redirect('writer-home')
    

class FollowersView(View):
    def get(self,request):
        writer=request.user
        followers=writer.followers.all()
        return render(request,'followers.html',{'followers':followers})
    
    
class LikedBlogs(View):
    def get(self,request):
        l_blogs = Blog.objects.filter(likes__user=request.user,likes__is_like=True).distinct()
        return render(request,'liked_blogs.html',{'blogs':l_blogs})

class DislikedBlogs(View):
    def get(self,request):
        d_blogs=Blog.objects.filter(likes__user=request.user,likes__is_like=False).distinct()
        return render(request,'disliked_blogs.html',{'blogs':d_blogs})
    
