#!/usr/bin/env python3
"""
Test ACF Integration Service
Tests the ACF field generation for Brazilian industries
"""

import sys
import json
sys.path.append('/home/douglaskenzy/workspace/kenzysites/backend')

from app.services.acf_integration import acf_service

def test_restaurant_fields():
    """Test restaurant industry field generation"""
    print("🍕 Testing Restaurant Fields Generation...")
    
    # Generate fields for restaurant industry
    field_groups = acf_service.generate_industry_fields('restaurante')
    
    print(f"✅ Generated {len(field_groups)} field groups for restaurant")
    
    # Display field groups
    for group in field_groups:
        print(f"\n📋 Field Group: {group['title']}")
        print(f"   Key: {group['key']}")
        print(f"   Fields: {len(group['fields'])}")
        
        # Show first 3 fields as example
        for field in group['fields'][:3]:
            print(f"   - {field['label']} ({field['type']})")
    
    # Export to JSON for WordPress import
    json_export = acf_service.export_to_json(field_groups)
    
    # Save to file
    with open('/home/douglaskenzy/workspace/kenzysites/acf_restaurant_fields.json', 'w', encoding='utf-8') as f:
        f.write(json_export)
    
    print("\n✅ Exported to acf_restaurant_fields.json")
    
    # Also generate PHP code
    php_export = acf_service.export_to_php(field_groups)
    
    with open('/home/douglaskenzy/workspace/kenzysites/acf_restaurant_fields.php', 'w', encoding='utf-8') as f:
        f.write(php_export)
    
    print("✅ Exported to acf_restaurant_fields.php")
    
    return field_groups

def test_dentist_fields():
    """Test dentist clinic field generation"""
    print("\n🦷 Testing Dentist Fields Generation...")
    
    field_groups = acf_service.generate_industry_fields('dentista')
    
    print(f"✅ Generated {len(field_groups)} field groups for dentist")
    
    for group in field_groups:
        print(f"\n📋 Field Group: {group['title']}")
        print(f"   Fields: {len(group['fields'])}")
    
    return field_groups

def test_gym_fields():
    """Test gym/fitness field generation"""
    print("\n💪 Testing Gym Fields Generation...")
    
    field_groups = acf_service.generate_industry_fields('academia')
    
    print(f"✅ Generated {len(field_groups)} field groups for gym")
    
    for group in field_groups:
        print(f"\n📋 Field Group: {group['title']}")
        print(f"   Fields: {len(group['fields'])}")
    
    return field_groups

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 KenzySites ACF Integration Test")
    print("=" * 50)
    
    # Test different industries
    test_restaurant_fields()
    test_dentist_fields()
    test_gym_fields()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("=" * 50)
    
    print("\n📝 Next steps:")
    print("1. Import acf_restaurant_fields.json in WordPress ACF")
    print("2. Or copy acf_restaurant_fields.php to WordPress theme")
    print("3. Create a page and fill the ACF fields")
    print("4. Test the conversion with real data")

if __name__ == "__main__":
    main()