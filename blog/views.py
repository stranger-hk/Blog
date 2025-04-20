from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from .models import BlogPost, APISettings
from .services import generate_blog_content, download_image_from_url


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published')


def home(request):
    latest_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    return render(request, 'blog/home.html', {'latest_posts': latest_posts})


def generate_blog(request):
    """View to generate a blog post from a topic"""
    if request.method == 'POST':
        topic = request.POST.get('topic')
        if topic:
            # Create a new blog post
            title = f"Blog about {topic}"
            blog = BlogPost(
                title=title,
                topic=topic,
                auto_generate=True
            )
            blog.save()  # This will trigger auto-generation
            
            messages.success(request, f"Blog post about '{topic}' has been created and content generated!")
            return redirect('blog:blog_detail', slug=blog.slug)
        else:
            messages.error(request, "Please provide a topic for the blog post.")
    
    return render(request, 'blog/generate_blog.html')
