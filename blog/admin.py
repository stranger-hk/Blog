from django.contrib import admin
from django.utils.html import format_html
from .models import BlogPost, APISettings
from .services import generate_blog_content, download_image_from_url


class APISettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'model')
    fieldsets = (
        (None, {
            'fields': ('name', 'api_key', 'model')
        }),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'status', 'created_at', 'image_preview', 'has_content')
    list_filter = ('status', 'created_at', 'auto_generate')
    search_fields = ('title', 'topic', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    actions = ['generate_blog_content']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'topic', 'slug', 'status', 'auto_generate')
        }),
        ('Content', {
            'fields': ('content', 'image')
        }),
        ('Dates', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    
    image_preview.short_description = 'Image Preview'
    
    def has_content(self, obj):
        return bool(obj.content)
    
    has_content.boolean = True
    has_content.short_description = 'Has Content'
    
    def generate_blog_content(self, request, queryset):
        for blog in queryset:
            if blog.topic:
                try:
                    # Get API settings
                    api_settings = APISettings.objects.first()
                    if not api_settings:
                        self.message_user(request, "API settings not found. Please configure API settings first.")
                        return
                    
                    # Generate blog content
                    content, image_url = generate_blog_content(blog.topic, api_settings.api_key, api_settings.model)
                    
                    # Update blog post
                    blog.content = content
                    
                    # Download and save image if available
                    if image_url:
                        blog.image_url = image_url
                        download_image_from_url(blog, image_url)
                    
                    blog.save()
                    self.message_user(request, f"Successfully generated content for '{blog.title}'")
                except Exception as e:
                    self.message_user(request, f"Error generating content for '{blog.title}': {str(e)}")
            else:
                self.message_user(request, f"Blog '{blog.title}' has no topic specified.")
    
    generate_blog_content.short_description = "Generate blog content using AI"


# Register models
admin.site.register(APISettings, APISettingsAdmin)
