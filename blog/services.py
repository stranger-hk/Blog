import requests
import json
import os
import random
from django.core.files.base import ContentFile
from django.conf import settings
from urllib.parse import quote_plus


def generate_blog_content(topic, api_key, model="openai/gpt-3.5-turbo"):
    """
    Generate blog content using OpenRouter API
    Returns: (content, image_url)
    """
    # Prepare the prompt for blog generation
    prompt = f"""
    Write a comprehensive, engaging, and informative blog post about "{topic}".
    
    The blog should:
    1. Have a catchy title
    2. Include an introduction that hooks the reader
    3. Contain at least 3-4 main sections with subheadings
    4. Include relevant facts and information
    5. End with a conclusion
    
    Format the blog in Markdown.
    """
    
    # Make API request to OpenRouter
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional blog writer who creates engaging, informative content."},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    # Extract blog content from response
    response_data = response.json()
    blog_content = response_data['choices'][0]['message']['content']
    
    # Paraphrase the content
    paraphrased_content = paraphrase_content(blog_content, api_key, model)
    
    # Find a relevant image
    image_url = find_relevant_image(topic)
    
    return paraphrased_content, image_url


def paraphrase_content(content, api_key, model="openai/gpt-3.5-turbo"):
    """Paraphrase the generated content to make it unique"""
    prompt = f"""
    Please paraphrase the following blog content to make it unique while preserving all information and the structure:
    
    {content}
    
    Keep all formatting, headings, and markdown intact.
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional editor who paraphrases content to make it unique while preserving meaning."},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )
    
    if response.status_code != 200:
        # If paraphrasing fails, return the original content
        return content
    
    response_data = response.json()
    paraphrased_content = response_data['choices'][0]['message']['content']
    
    return paraphrased_content


def find_relevant_image(topic):
    """Find a relevant image for the blog topic using Unsplash API"""
    # Using Unsplash API for demo purposes
    # In a production environment, you should register for an API key
    search_term = quote_plus(topic)
    url = f"https://api.unsplash.com/photos/random?query={search_term}&client_id=YOUR_UNSPLASH_API_KEY"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['urls']['regular']
    except Exception:
        pass
    
    # Fallback to placeholder images if Unsplash API fails
    placeholders = [
        "https://via.placeholder.com/800x400?text=Blog+Image",
        "https://picsum.photos/800/400",
    ]
    return random.choice(placeholders)


def download_image_from_url(blog_post, url):
    """Download image from URL and save it to the blog post"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Extract filename from URL or create a unique one
            filename = f"blog_{blog_post.id}_{blog_post.slug}.jpg"
            
            # Save the image to the blog post
            blog_post.image.save(filename, ContentFile(response.content), save=True)
            return True
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
    
    return False
