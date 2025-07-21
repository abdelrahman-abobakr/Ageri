#!/usr/bin/env python3
"""
Create Demo Labs and Researchers
===============================

This script creates demo labs and researchers to test the department info endpoint.

Usage:
    python3 manage.py shell < create_demo_labs.py
"""

from django.contrib.auth import get_user_model
from accounts.models import UserRole
from organization.models import Department, Lab, ResearcherAssignment
from datetime import date

User = get_user_model()

def create_demo_data():
    """Create demo labs and researchers"""
    print("🔧 Creating demo labs and researchers...")
    
    # Get or create department
    try:
        department = Department.objects.get(name="Cell Biology")
        print(f"✅ Using existing department: {department.name}")
    except Department.DoesNotExist:
        department = Department.objects.create(
            name="Cell Biology",
            description="Department specialized in cell biology research and molecular studies"
        )
        print(f"✅ Created department: {department.name}")
    
    # Create labs
    labs_data = [
        {
            'name': 'Molecular Biology Lab',
            'description': 'Advanced molecular biology research focusing on gene expression and protein synthesis'
        },
        {
            'name': 'Cell Culture Lab',
            'description': 'Specialized facility for cell culture, tissue engineering, and cellular studies'
        },
        {
            'name': 'Microscopy Lab',
            'description': 'High-resolution imaging facility with confocal and electron microscopy'
        }
    ]
    
    created_labs = []
    for lab_data in labs_data:
        lab, created = Lab.objects.get_or_create(
            name=lab_data['name'],
            department=department,
            defaults={
                'description': lab_data['description'],
                'capacity': 8,
                'status': 'active'
            }
        )
        if created:
            print(f"✅ Created lab: {lab.name}")
        else:
            print(f"✅ Using existing lab: {lab.name}")
        created_labs.append(lab)
    
    # Create researchers
    researchers_data = [
        {
            'username': 'dr_smith',
            'email': 'dr.smith@research.edu',
            'first_name': 'John',
            'last_name': 'Smith',
            'lab_index': 0,
            'position': 'Principal Investigator'
        },
        {
            'username': 'dr_johnson',
            'email': 'dr.johnson@research.edu',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'lab_index': 0,
            'position': 'Postdoctoral Researcher'
        },
        {
            'username': 'dr_brown',
            'email': 'dr.brown@research.edu',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'lab_index': 1,
            'position': 'Lab Head'
        },
        {
            'username': 'dr_davis',
            'email': 'dr.davis@research.edu',
            'first_name': 'Emily',
            'last_name': 'Davis',
            'lab_index': 1,
            'position': 'PhD Student'
        },
        {
            'username': 'dr_wilson',
            'email': 'dr.wilson@research.edu',
            'first_name': 'David',
            'last_name': 'Wilson',
            'lab_index': 2,
            'position': 'Research Scientist'
        }
    ]
    
    for researcher_data in researchers_data:
        # Create user if not exists
        user, created = User.objects.get_or_create(
            username=researcher_data['username'],
            defaults={
                'email': researcher_data['email'],
                'first_name': researcher_data['first_name'],
                'last_name': researcher_data['last_name'],
                'role': UserRole.RESEARCHER,
                'is_approved': True
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            print(f"✅ Created researcher: {user.get_full_name()}")
        else:
            print(f"✅ Using existing researcher: {user.get_full_name()}")
        
        # Assign to lab
        lab = created_labs[researcher_data['lab_index']]
        assignment, created = ResearcherAssignment.objects.get_or_create(
            researcher=user,
            lab=lab,
            department=department,
            defaults={
                'start_date': date.today(),
                'position': researcher_data['position'],
                'status': 'active'
            }
        )
        
        if created:
            print(f"   ✅ Assigned to {lab.name} as {researcher_data['position']}")
        
        # Set lab head if position is Lab Head or Principal Investigator
        if researcher_data['position'] in ['Lab Head', 'Principal Investigator']:
            if not lab.head:
                lab.head = user
                lab.save()
                print(f"   ✅ Set as head of {lab.name}")
    
    print(f"\n🎉 Demo data creation complete!")
    print(f"📊 Summary:")
    print(f"   • Department: {department.name}")
    print(f"   • Labs created: {len(created_labs)}")
    print(f"   • Researchers created: {len(researchers_data)}")
    print(f"\n🔗 Test the new endpoint:")
    print(f"   curl http://localhost:8000/api/organization/departments/{department.id}/info/")

if __name__ == "__main__":
    create_demo_data()
