"""
Quick test script for image selection
Tests if UPS image appears for power-related queries
"""
from image_manager import ImageManager

# Initialize manager
manager = ImageManager()

# Set high priority for UPS image (emergency-critical)
manager.add_image_metadata(
    'electricity_backup_ups/ups_tech_specs_backup_kva_voltage.png',
    priority=9  # High priority for emergency equipment
)

# Test queries
test_queries = [
    "how to manage backup needs during emergency power cut off",
    "what UPS do I need for medical equipment",
    "power outage emergency backup",
    "electricity failure what to do",
    "battery backup for ventilator"
]

print("\n" + "="*70)
print("🔍 TESTING IMAGE SELECTION FOR POWER/UPS QUERIES")
print("="*70)

for query in test_queries:
    images = manager.suggest_images(query, max_images=3)
    print(f"\n📝 Query: {query}")
    if images:
        print(f"   ✅ Found {len(images)} image(s):")
        for img in images:
            print(f"      • {img['description']}")
            print(f"        Category: {img['category']}")
    else:
        print("   ❌ No images found")

print("\n" + "="*70)
print("✅ Test complete!")
print("="*70)
