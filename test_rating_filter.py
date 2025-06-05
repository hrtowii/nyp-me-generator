#!/usr/bin/env python3
"""
Test script to verify that the Gelbooru rating filter is working correctly.
This script will search for various anime characters and verify that only
general-rated images are returned.
"""

import json
from gelbooru import GelbooruSearcher, validate_rating

def test_rating_filter():
    """Test that only general-rated images are returned"""
    searcher = GelbooruSearcher()
    
    # Test cases with popular anime characters
    test_cases = [
        "megumin konosuba",
        "naruto uzumaki",
        "sailor_moon",
        "pikachu pokemon",
        "goku dragon_ball"
    ]
    
    print("=" * 60)
    print("TESTING GELBOORU RATING FILTER")
    print("=" * 60)
    
    for tags in test_cases:
        print(f"\n🔍 Testing search: '{tags}'")
        print("-" * 40)
        
        # Search for images
        posts = searcher.search_images(tags, limit=10)
        
        if not posts:
            print("❌ No posts found")
            continue
            
        # Validate ratings
        print(f"📊 Total posts found: {len(posts)}")
        validated_posts = validate_rating(posts)
        
        # Check if all posts are general-rated
        ratings_found = set(post.get('rating', 'unknown') for post in posts)
        general_count = len(validated_posts)
        
        print(f"✅ General-rated posts: {general_count}")
        print(f"📋 All ratings found: {list(ratings_found)}")
        
        # Verify our filter is working
        if all(post.get('rating') == 'general' for post in validated_posts):
            print("✅ PASS: All filtered posts are general-rated")
        else:
            print("❌ FAIL: Some non-general posts passed through filter")
            
        # Show sample post data (first post only)
        if validated_posts:
            sample_post = validated_posts[0]
            print(f"📄 Sample post: ID={sample_post.get('id')}, Rating={sample_post.get('rating')}")
            print(f"🏷️  Tags: {sample_post.get('tags', '')[:100]}...")
        
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

def test_search_with_fallback():
    """Test the search_with_fallback method specifically"""
    searcher = GelbooruSearcher()
    
    print("\n🔄 Testing search_with_fallback method...")
    
    # Test with a specific character
    test_tags = ["megumin", "konosuba", "explosion", "red_dress"]
    
    print(f"🎯 Searching with tags: {test_tags}")
    result_url = searcher.search_with_fallback(test_tags)
    
    if result_url:
        print(f"✅ Successfully found image URL: {result_url[:60]}...")
        print("✅ PASS: search_with_fallback returned a result")
    else:
        print("❌ FAIL: search_with_fallback returned None")

def main():
    """Run all tests"""
    try:
        test_rating_filter()
        test_search_with_fallback()
        
        print("\n🎉 All tests completed!")
        print("Note: Check the console output above to verify that:")
        print("  1. Only 'general' ratings are being returned")
        print("  2. The rating filter is working correctly")
        print("  3. Search fallback is functioning")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()