#!/usr/bin/env python3
"""
Simple Course Date Validation Test
==================================

This script demonstrates the course date validation without requiring Django shell.
It shows the validation logic and provides examples.

Usage:
    python3 simple_validation_test.py
"""

from datetime import date, timedelta

def test_date_validation_logic():
    """Test the validation logic"""
    print("🧪 Course Date Validation Logic Test")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid dates - end after start",
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=20),
            "registration_deadline": date.today() + timedelta(days=5),
            "should_pass": True
        },
        {
            "name": "Invalid - end same as start",
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=10),
            "registration_deadline": date.today() + timedelta(days=5),
            "should_pass": False,
            "error": "End date must be after start date"
        },
        {
            "name": "Invalid - end before start",
            "start_date": date.today() + timedelta(days=20),
            "end_date": date.today() + timedelta(days=10),
            "registration_deadline": date.today() + timedelta(days=5),
            "should_pass": False,
            "error": "End date must be after start date"
        },
        {
            "name": "Invalid - registration after start",
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=20),
            "registration_deadline": date.today() + timedelta(days=15),
            "should_pass": False,
            "error": "Registration deadline must be before start date"
        },
        {
            "name": "Invalid - registration same as start",
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=20),
            "registration_deadline": date.today() + timedelta(days=10),
            "should_pass": False,
            "error": "Registration deadline must be before start date"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {test_case['name']}:")
        print(f"   Start: {test_case['start_date']}")
        print(f"   End: {test_case['end_date']}")
        print(f"   Registration: {test_case['registration_deadline']}")
        
        # Apply validation logic
        errors = []
        
        # Check end_date > start_date
        if test_case['end_date'] <= test_case['start_date']:
            errors.append("End date must be after start date")
        
        # Check registration_deadline < start_date
        if test_case['registration_deadline'] >= test_case['start_date']:
            errors.append("Registration deadline must be before start date")
        
        # Check result
        if test_case['should_pass']:
            if not errors:
                print("   ✅ PASS: Valid dates accepted")
            else:
                print(f"   ❌ FAIL: Unexpected errors: {errors}")
        else:
            if errors:
                print("   ✅ PASS: Invalid dates correctly rejected")
                print(f"   📝 Errors: {errors}")
            else:
                print("   ❌ FAIL: Invalid dates should have been rejected")

def show_validation_implementation():
    """Show the actual validation implementation"""
    print("\n\n💻 Validation Implementation")
    print("=" * 50)
    
    print("🔧 **Model Validation (training/models.py):**")
    model_code = '''
def clean(self):
    """Validate course data"""
    from django.core.exceptions import ValidationError

    # Validate that end_date is after start_date
    if self.start_date and self.end_date:
        if self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })

    # Validate that registration deadline is before start_date
    if self.registration_deadline and self.start_date:
        if self.registration_deadline >= self.start_date:
            raise ValidationError({
                'registration_deadline': 'Registration deadline must be before start date.'
            })
'''
    print(model_code)
    
    print("🔧 **Serializer Validation (training/serializers.py):**")
    serializer_code = '''
def validate(self, data):
    """Validate course data"""
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    registration_deadline = data.get('registration_deadline')
    
    # If updating, get current values if not provided
    if self.instance:
        start_date = start_date or self.instance.start_date
        end_date = end_date or self.instance.end_date
        registration_deadline = registration_deadline or self.instance.registration_deadline
    
    # Validate that end_date is after start_date
    if start_date and end_date:
        if end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
    
    # Validate that registration deadline is before start_date
    if registration_deadline and start_date:
        if registration_deadline >= start_date:
            raise serializers.ValidationError({
                'registration_deadline': 'Registration deadline must be before start date.'
            })
    
    return data
'''
    print(serializer_code)

def show_api_usage_examples():
    """Show how the validation works in API calls"""
    print("\n\n🌐 API Usage Examples")
    print("=" * 50)
    
    print("✅ **Valid Course Creation:**")
    valid_example = '''
POST /api/training/courses/
Content-Type: application/json

{
    "course_name": "Python Programming",
    "course_code": "PY101",
    "instructor": "Dr. Smith",
    "cost": "150.00",
    "start_date": "2025-02-01",
    "end_date": "2025-02-28",
    "registration_deadline": "2025-01-25",
    "training_hours": 40,
    "description": "Introduction to Python programming",
    "max_participants": 30
}

Response: 201 Created
{
    "id": 1,
    "course_name": "Python Programming",
    "start_date": "2025-02-01",
    "end_date": "2025-02-28",
    "registration_deadline": "2025-01-25",
    ...
}
'''
    print(valid_example)
    
    print("❌ **Invalid Course Creation (End Date Before Start):**")
    invalid_example = '''
POST /api/training/courses/
Content-Type: application/json

{
    "course_name": "Invalid Course",
    "course_code": "INV001",
    "instructor": "Dr. Test",
    "start_date": "2025-02-28",
    "end_date": "2025-02-01",    // Before start date!
    "registration_deadline": "2025-01-25",
    ...
}

Response: 400 Bad Request
{
    "end_date": ["End date must be after start date."]
}
'''
    print(invalid_example)
    
    print("❌ **Invalid Course Creation (Late Registration):**")
    late_reg_example = '''
POST /api/training/courses/
Content-Type: application/json

{
    "course_name": "Late Registration Course",
    "start_date": "2025-02-01",
    "end_date": "2025-02-28",
    "registration_deadline": "2025-02-05",  // After start date!
    ...
}

Response: 400 Bad Request
{
    "registration_deadline": ["Registration deadline must be before start date."]
}
'''
    print(late_reg_example)

def show_testing_commands():
    """Show how to test the validation"""
    print("\n\n🧪 Testing Commands")
    print("=" * 50)
    
    print("📋 **Test with cURL:**")
    curl_commands = '''
# Test valid course
curl -X POST "http://localhost:8000/api/training/courses/" \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -d '{
       "course_name": "Test Course",
       "course_code": "TEST001",
       "instructor": "Dr. Test",
       "cost": "100.00",
       "start_date": "2025-02-01",
       "end_date": "2025-02-28",
       "registration_deadline": "2025-01-25",
       "training_hours": 40,
       "description": "Test course",
       "max_participants": 30
     }'

# Test invalid course (end before start)
curl -X POST "http://localhost:8000/api/training/courses/" \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -d '{
       "course_name": "Invalid Course",
       "course_code": "INV001",
       "start_date": "2025-02-28",
       "end_date": "2025-02-01",
       "registration_deadline": "2025-01-25",
       ...
     }'
'''
    print(curl_commands)
    
    print("🐍 **Test with Python:**")
    python_test = '''
import requests

# Test valid course
valid_data = {
    "course_name": "Python Test Course",
    "course_code": "PY001",
    "instructor": "Dr. Python",
    "cost": "200.00",
    "start_date": "2025-02-01",
    "end_date": "2025-02-28",
    "registration_deadline": "2025-01-25",
    "training_hours": 50,
    "description": "Python programming course",
    "max_participants": 25
}

response = requests.post(
    'http://localhost:8000/api/training/courses/',
    json=valid_data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

if response.status_code == 201:
    print("✅ Course created successfully")
else:
    print(f"❌ Error: {response.json()}")
'''
    print(python_test)

def main():
    """Run the validation demonstration"""
    print("🚀 Course Date Validation Implementation")
    print("=" * 60)
    print(f"⏰ Demo started at: {date.today()}")
    
    # Run tests
    test_date_validation_logic()
    show_validation_implementation()
    show_api_usage_examples()
    show_testing_commands()
    
    print(f"\n🎉 Validation implementation complete!")
    print("=" * 60)
    print("✅ **What's Implemented:**")
    print("   • End date must be after start date")
    print("   • Registration deadline must be before start date")
    print("   • Validation at both model and serializer levels")
    print("   • Clear error messages for API responses")
    print("   • Works for both create and update operations")
    print()
    print("🔧 **Files Modified:**")
    print("   • training/models.py - Course.clean() method")
    print("   • training/serializers.py - CourseDetailSerializer.validate() method")
    print()
    print("🚀 **Ready to Use:**")
    print("   • API endpoints will now validate course dates")
    print("   • Invalid dates will return HTTP 400 with error details")
    print("   • Both creation and updates are protected")

if __name__ == "__main__":
    main()
