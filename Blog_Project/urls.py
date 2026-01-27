from django.contrib import admin
from django.urls import path
from blog_app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', views.LoginView.as_view(),name='login'),
    path('logout', views.LogoutView.as_view(),name='logout'),

    path('reader/register',views.ReaderRegisterView.as_view(),name='reader-register'),
    path('', views.ReaderHome.as_view(),name='reader-home'),
    path('reader/blogs/<int:id>', views.ReaderBlogDetailView.as_view(),name='reader-blog_detail'),
    path('reader/comment/<int:id>', views.PostComment.as_view(),name='comment'),
    path('reader/writers', views.RenderWriters.as_view(),name='render-writer'),
    path('reader/specific/writer/<int:id>', views.SpecificWriter.as_view(),name='writer'),
    path('blog/<int:blog_id>/react/',views.BlogLikeDislikeView.as_view(),name='blog-react'),
    path('blog/<int:blog_id>/bookmark/',views.BookmarkView.as_view(),name='toggle-bookmark'),
    path('blog/saved-blogs/',views.BookmarkList.as_view(),name='bookmarks'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('reader/liked/blogs/',views.LikedBlogs.as_view(),name='liked_blogs'),
    path('reader/disliked/blogs/',views.DislikedBlogs.as_view(),name='disliked_blogs'),



    path('writer/register',views.WriterRegisterView.as_view(),name='writer-register'),
    path('writer/home',views.WriterHome.as_view(),name='writer-home'),
    path('writer/addblog', views.WriterAddBlogView.as_view(),name='add-blog'),
    path('writer/blogs/<int:id>', views.WriterBlogs.as_view(),name='writer-blogs'),
    path('writer/updateblog/<int:id>', views.BlogUpdateView.as_view(),name='update-blogs'),
    path('writer/deleteblog/<int:id>', views.DeleteBlogView.as_view(),name='delete-blog'),
    path('writer/drafted/blogs', views.WriterDraftView.as_view(),name='drafted-blogs'),
    path('writer/drafted/<int:id>/blogs', views.PublishDraft.as_view(),name='publish-draft'),
    path('writer/followers', views.FollowersView.as_view(),name='followers'),
    path('writer/dashboard', views.WriterDashboard.as_view(),name='dashboard'),


    path('forgot-password/',auth_views.PasswordResetView.as_view(template_name=
            'forgot_password.html'),name='forgot-password'),

    path('forgot-password/done/',auth_views.PasswordResetDoneView.as_view(template_name=
            'password_reset_done.html'),name='password_reset_done'),

    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(
        template_name='reset_password.html'),name='password_reset_confirm'),

    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name=
                'password_reset_complete.html'),name='password_reset_complete'),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
