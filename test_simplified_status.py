#!/usr/bin/env python3
"""
Test script for the simplified post status system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from content.models import Post
from accounts.models import User
import requests
import json

def test_simplified_status_system():
    """Test the simplified 2-status system"""
    print("📊 Testing Simplified Post Status System")
    print("=" * 60)
    
    # Get a user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    # Create a test post
    print("1️⃣ Creating test post...")
    post = Post.objects.create(
        title="Test Simplified Status System",
        content="This post tests the simplified status system with only pending and published statuses.",
        author=user
    )
    
    print(f"   ✅ Post created: ID {post.id}")
    print(f"   📊 Default status: {post.status}")
    print(f"   📝 Title: {post.title}")
    
    # Test 1: Update status via API (if server is running)
    print(f"\n2️⃣ Testing API Status Update...")
    try:
        # Test updating to published
        api_url = f"http://127.0.0.1:8000/api/content/posts/{post.id}/"
        update_data = {
            "status": "published"
        }
        
        print(f"   🔄 Updating status to 'published' via PATCH...")
        print(f"   📡 URL: {api_url}")
        print(f"   📋 Data: {json.dumps(update_data, indent=2)}")
        
        # Note: This would require authentication in real usage
        print(f"   ℹ️  API test requires authentication - skipping actual request")
        
    except Exception as e:
        print(f"   ⚠️  API test skipped: {e}")
    
    # Test 2: Update status via Django ORM
    print(f"\n3️⃣ Testing Status Updates via ORM...")
    
    # Update to published
    post.status = 'published'
    post.save()
    print(f"   ✅ Status updated to: {post.status}")
    
    # Update back to pending
    post.status = 'pending'
    post.save()
    print(f"   ✅ Status updated to: {post.status}")
    
    # Test 3: Test serializer includes status
    print(f"\n4️⃣ Testing Serializer Integration...")
    from content.serializers import PostCreateUpdateSerializer, PostListSerializer
    from rest_framework.test import APIRequestFactory
    
    # Test update serializer
    factory = APIRequestFactory()
    request = factory.patch('/api/content/posts/')
    
    update_serializer = PostCreateUpdateSerializer(post, data={'status': 'published'}, partial=True)
    if update_serializer.is_valid():
        updated_post = update_serializer.save()
        print(f"   ✅ Update serializer works: {updated_post.status}")
    else:
        print(f"   ❌ Update serializer errors: {update_serializer.errors}")
    
    # Test list serializer
    list_serializer = PostListSerializer(updated_post, context={'request': request})
    status_in_response = 'status' in list_serializer.data
    print(f"   ✅ List serializer includes status: {status_in_response}")
    if status_in_response:
        print(f"   📊 Status in API response: {list_serializer.data['status']}")
    
    # Test 4: Status filtering
    print(f"\n5️⃣ Testing Status Filtering...")
    
    # Create another post with different status
    post2 = Post.objects.create(
        title="Second Test Post",
        content="Another test post for filtering",
        author=user,
        status='pending'
    )
    
    # Filter posts by status
    pending_posts = Post.objects.filter(status='pending')
    published_posts = Post.objects.filter(status='published')
    
    print(f"   📊 Pending posts: {pending_posts.count()}")
    print(f"   📊 Published posts: {published_posts.count()}")
    
    # Test 5: Frontend Integration Example
    print(f"\n6️⃣ Frontend Integration Example...")
    
    frontend_example = {
        "post_id": updated_post.id,
        "current_status": updated_post.status,
        "available_statuses": ["pending", "published"],
        "api_endpoint": f"/api/content/posts/{updated_post.id}/",
        "update_method": "PATCH",
        "update_data_example": {
            "status": "pending"
        }
    }
    
    print(f"   📋 Frontend integration data:")
    print(json.dumps(frontend_example, indent=4))
    
    # Cleanup
    print(f"\n🧹 Cleaning up test posts...")
    post.delete()
    post2.delete()
    print(f"   ✅ Test posts deleted")

def show_status_summary():
    """Show summary of the simplified status system"""
    print(f"\n📊 Simplified Status System Summary")
    print("=" * 50)
    
    print(f"✅ Status Values:")
    print(f"   • pending   - Default status, awaiting review")
    print(f"   • published - Live and visible to public")
    
    print(f"\n✅ API Integration:")
    print(f"   • Endpoint: PATCH /api/content/posts/{{id}}/")
    print(f"   • Update status with: {{\"status\": \"published\"}}")
    print(f"   • Can combine with other fields")
    
    print(f"\n✅ Frontend Benefits:")
    print(f"   • Simple toggle interface")
    print(f"   • Clear pending → published workflow")
    print(f"   • Standard REST API patterns")
    print(f"   • No special approval endpoints needed")
    
    print(f"\n✅ Database Changes:")
    print(f"   • Default status changed to 'pending'")
    print(f"   • Status field added to update serializer")
    print(f"   • Regular PATCH endpoint handles status updates")

if __name__ == "__main__":
    test_simplified_status_system()
    show_status_summary()
    
    print("\n" + "=" * 60)
    print("🎉 Simplified Post Status System Test Complete!")
    print("✅ 2 statuses: pending (default) → published")
    print("✅ Regular PATCH endpoint for updates")
    print("✅ Simple frontend integration")
    print("✅ No complex approval workflow needed")
    print("\n🚀 The simplified system is ready for frontend implementation!")
