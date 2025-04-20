from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from .services import generate_blog_content, download_image_from_url


class APISettings(models.Model):
    """Model to store API settings that can be modified in the admin panel"""
    name = models.CharField(max_length=100, default="OpenRouter API")
    api_key = models.CharField(max_length=255, help_text="API key for OpenRouter")
    model = models.CharField(max_length=100, default="openai/gpt-3.5-turbo", 
                            help_text="Model to use for blog generation")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "API Setting"
        verbose_name_plural = "API Settings"


class BlogPost(models.Model):
    """Model to store blog posts"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    auto_generate = models.BooleanField(default=True, help_text="Automatically generate content when topic is provided")
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate content if enabled and topic is provided
        if self.auto_generate and self.topic and not self.content:
            try:
                # Get API settings
                api_settings = APISettings.objects.first()
                if api_settings:
                    # Generate blog content
                    content, image_url = generate_blog_content(self.topic, api_settings.api_key, api_settings.model)
                    
                    # Update blog post
                    self.content = content
                    
                    # Save first to get an ID if this is a new post
                    super().save(*args, **kwargs)
                    
                    # Download and save image if available
                    if image_url:
                        self.image_url = image_url
                        download_image_from_url(self, image_url)
                        # We'll save again after this
                    return  # Skip the second save since we already saved
            except Exception as e:
                print(f"Error auto-generating content: {str(e)}")
        
        # Update published_at if status changed to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
