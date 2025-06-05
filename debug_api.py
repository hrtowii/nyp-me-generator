#!/usr/bin/env python3
"""
Debug script to examine actual Gelbooru API responses and understand
the data structure, including ratings and available content.
"""

import requests
import json
from pprint import pprint

def debug_gelbooru_api():
    """Debug the Gelbooru API to understand response structure"""
    
    base_url = "https://gelbooru.com/index.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("=" * 80)
    print("GELBOORU API DEBUG")
    print("=" * 80)
    
    # Test 1: Basic search without rating filter
    print("\n🔍 TEST 1: Basic search (no rating filter)")
    print("-" * 50)
    
    params = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'tags': 'megumin',
        'limit': 5,
        'json': '1'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Response status: {response.status_code}")
        print(f"Response type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Response keys: {list(data.keys())}")
            if 'post' in data:
                posts = data['post']
                print(f"Number of posts: {len(posts)}")
                
                if posts:
                    print("\n📊 RATING ANALYSIS:")
                    ratings = {}
                    for post in posts:
                        rating = post.get('rating', 'unknown')
                        ratings[rating] = ratings.get(rating, 0) + 1
                    
                    for rating, count in ratings.items():
                        print(f"  {rating}: {count} posts")
                    
                    print("\n📄 SAMPLE POST DATA:")
                    sample_post = posts[0]
                    for key, value in sample_post.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  {key}: {value[:100]}...")
                        else:
                            print(f"  {key}: {value}")
            else:
                print("No 'post' key in response")
                pprint(data)
        else:
            print(f"Unexpected response format: {data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Search with rating:general filter
    print("\n\n🔍 TEST 2: Search with rating:general filter")
    print("-" * 50)
    
    params_with_rating = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'tags': 'megumin+rating:general',
        'limit': 5,
        'json': '1'
    }
    
    try:
        response = requests.get(base_url, params=params_with_rating, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"Response status: {response.status_code}")
        
        if isinstance(data, dict) and 'post' in data:
            posts = data['post']
            print(f"Number of posts with rating:general: {len(posts)}")
            
            if posts:
                print("\n📊 RATING VERIFICATION:")
                for i, post in enumerate(posts):
                    rating = post.get('rating', 'unknown')
                    post_id = post.get('id', 'unknown')
                    print(f"  Post {i+1} (ID: {post_id}): rating = '{rating}'")
            else:
                print("No posts found with rating:general filter")
        else:
            print("No posts found or unexpected response format")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try different safe characters
    print("\n\n🔍 TEST 3: Testing safe anime characters")
    print("-" * 50)
    
    safe_characters = [
        "pikachu",
        "pokemon",
        "naruto",
        "sailor_moon",
        "totoro"
    ]
    
    for character in safe_characters:
        print(f"\n🎯 Testing: {character}")
        
        params = {
            'page': 'dapi',
            's': 'post',
            'q': 'index',
            'tags': f'{character}+rating:general',
            'limit': 3,
            'json': '1'
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and 'post' in data:
                posts = data['post']
                print(f"  Found {len(posts)} general-rated posts")
                
                if posts:
                    sample_post = posts[0]
                    print(f"  Sample ID: {sample_post.get('id')}")
                    print(f"  Sample rating: {sample_post.get('rating')}")
                    print(f"  Sample tags: {sample_post.get('tags', '')[:80]}...")
            else:
                print("  No posts found")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test 4: Try rating:safe instead
    print("\n\n🔍 TEST 4: Testing rating:safe filter")
    print("-" * 50)
    
    params_safe = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'tags': 'megumin+rating:safe',
        'limit': 5,
        'json': '1'
    }
    
    try:
        response = requests.get(base_url, params=params_safe, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and 'post' in data:
            posts = data['post']
            print(f"Found {len(posts)} posts with rating:safe")
            
            if posts:
                print("\n📊 RATING VERIFICATION:")
                for i, post in enumerate(posts):
                    rating = post.get('rating', 'unknown')
                    post_id = post.get('id', 'unknown')
                    print(f"  Post {i+1} (ID: {post_id}): rating = '{rating}'")
        else:
            print("No posts found with rating:safe")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run the debug analysis"""
    debug_gelbooru_api()
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)
    print("\nKey findings to look for:")
    print("1. What rating values actually exist? (general, safe, questionable, explicit)")
    print("2. Are there any general-rated posts for popular characters?")
    print("3. What's the correct rating filter syntax?")
    print("4. What does the API response structure look like?")

if __name__ == "__main__":
    main()