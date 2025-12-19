"""
Image Upload Tool for ALS AI Assistant
Interactive tool to upload and organize medical images
"""
import os
import sys
from pathlib import Path
from typing import Optional, List
import shutil
from datetime import datetime
import re

# Try to import PIL for image preview
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️  PIL not installed. Install with: pip install Pillow")

# Try to import clipboard support
try:
    from PIL import ImageGrab
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False


class ImageUploadTool:
    """Interactive tool for uploading and organizing images"""
    
    def __init__(self, images_dir: str = "ai_assistant_images"):
        self.images_dir = Path(images_dir)
        self.categories = self._get_categories()
        
        # Category descriptions for better suggestions
        self.category_descriptions = {
            'tracheostomy': 'TT tubes, cuffs, dressing, suctioning equipment',
            'respiratory_support': 'BiPAP, oxygen, ventilators, masks',
            'feeding_nutrition': 'PEG tubes, feeding positions, nutrition supplies',
            'mobility_equipment': 'Wheelchairs, lifts, transfer equipment',
            'communication_devices': 'Eye trackers, communication boards, AAC devices',
            'daily_care': 'Positioning, hygiene, skin care',
            'emergency_procedures': 'CPR, choking response, emergency protocols'
        }
    
    def _get_categories(self) -> List[str]:
        """Get list of existing categories"""
        if not self.images_dir.exists():
            return []
        return [d.name for d in self.images_dir.iterdir() if d.is_dir()]
    
    def run(self):
        """Run the interactive upload tool"""
        self._print_header()
        
        while True:
            print("\n" + "="*70)
            print("📸 Image Upload Tool")
            print("="*70)
            print("\nOptions:")
            print("  1. Upload image from file")
            print("  2. Upload from clipboard (screenshot)")
            print("  3. View categories and image counts")
            print("  4. Create new category")
            print("  5. Rebuild image catalog")
            print("  6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                self._upload_from_file()
            elif choice == '2':
                self._upload_from_clipboard()
            elif choice == '3':
                self._show_categories()
            elif choice == '4':
                self._create_category()
            elif choice == '5':
                self._rebuild_catalog()
            elif choice == '6':
                print("\n✅ Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def _print_header(self):
        """Print welcome header"""
        print("\n" + "="*70)
        print("      ALS COMPASS - Medical Image Upload Tool")
        print("="*70)
        print("\nThis tool helps you organize medical images for the AI assistant.")
        print("Images will be stored in:", self.images_dir.absolute())
        print("\n💡 Tip: Use descriptive filenames (e.g., 'bipap_mask_fitting.jpg')")
    
    def _upload_from_file(self):
        """Upload image from file path"""
        print("\n📁 Upload Image from File")
        print("-" * 50)
        
        # Get file path
        file_path = input("\nEnter image file path (or drag & drop): ").strip().strip('"')
        
        if not file_path:
            print("❌ No file path provided.")
            return
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        if not file_path.is_file():
            print(f"❌ Not a file: {file_path}")
            return
        
        # Check if it's an image
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        if file_path.suffix.lower() not in image_extensions:
            print(f"❌ Not a supported image format. Supported: {', '.join(image_extensions)}")
            return
        
        self._process_image(file_path)
    
    def _upload_from_clipboard(self):
        """Upload image from clipboard"""
        if not HAS_CLIPBOARD:
            print("\n❌ Clipboard support not available.")
            print("   Install with: pip install Pillow")
            return
        
        print("\n📋 Upload Image from Clipboard")
        print("-" * 50)
        print("\n💡 Copy an image to clipboard first (screenshot or copy image)")
        
        try:
            img = ImageGrab.grabclipboard()
            
            if img is None:
                print("❌ No image found in clipboard.")
                print("   Take a screenshot (Win+Shift+S) or copy an image first.")
                return
            
            # Save to temp file
            temp_path = Path("temp_clipboard_image.png")
            img.save(temp_path)
            
            print("✅ Image captured from clipboard!")
            self._process_image(temp_path, from_clipboard=True)
            
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
                
        except Exception as e:
            print(f"❌ Error accessing clipboard: {e}")
    
    def _process_image(self, source_path: Path, from_clipboard: bool = False):
        """Process and save image with metadata"""
        
        # Show image info
        print(f"\n📷 Image Information:")
        if HAS_PIL:
            try:
                with Image.open(source_path) as img:
                    print(f"   Format: {img.format}")
                    print(f"   Size: {img.size[0]}x{img.size[1]} pixels")
                    print(f"   Mode: {img.mode}")
            except Exception as e:
                print(f"   Could not read image details: {e}")
        
        # Suggest category
        print(f"\n📂 Select Category:")
        category = self._select_category(source_path.stem if not from_clipboard else "screenshot")
        
        if not category:
            print("❌ Upload cancelled.")
            return
        
        # Suggest filename
        print(f"\n📝 Choose Filename:")
        filename = self._suggest_filename(source_path.stem if not from_clipboard else "image", category)
        
        if not filename:
            print("❌ Upload cancelled.")
            return
        
        # Ensure extension
        if not filename.endswith(source_path.suffix):
            filename += source_path.suffix
        
        # Create destination path
        dest_dir = self.images_dir / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename
        
        # Check if file exists
        if dest_path.exists():
            overwrite = input(f"\n⚠️  File already exists: {filename}\n   Overwrite? (y/n): ").lower()
            if overwrite != 'y':
                # Suggest unique name
                base = dest_path.stem
                ext = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = dest_dir / f"{base}_{counter}{ext}"
                    counter += 1
                filename = dest_path.name
                print(f"   Using new name: {filename}")
        
        # Copy/move file
        try:
            shutil.copy2(source_path, dest_path)
            print(f"\n✅ Image saved successfully!")
            print(f"   Location: {dest_path.relative_to(self.images_dir.parent)}")
            
            # Ask for additional keywords
            print(f"\n🏷️  Add Additional Keywords (optional):")
            print("   (Press Enter to skip, or enter comma-separated keywords)")
            keywords = input("   Keywords: ").strip()
            
            if keywords:
                keywords_list = [k.strip() for k in keywords.split(',')]
                print(f"   Added keywords: {', '.join(keywords_list)}")
                # Note: Keywords will be picked up when catalog is rebuilt
            
            # Ask if they want to rebuild catalog now
            rebuild = input("\n♻️  Rebuild image catalog now? (recommended) (y/n): ").lower()
            if rebuild == 'y':
                self._rebuild_catalog()
            
        except Exception as e:
            print(f"❌ Error saving image: {e}")
    
    def _select_category(self, hint: str = "") -> Optional[str]:
        """Interactive category selection"""
        
        # Suggest category based on filename hint
        suggestions = []
        if hint:
            hint_lower = hint.lower()
            for cat in self.categories:
                cat_words = cat.lower().split('_')
                if any(word in hint_lower for word in cat_words):
                    suggestions.append(cat)
        
        print("\n   Available categories:")
        for i, cat in enumerate(self.categories, 1):
            desc = self.category_descriptions.get(cat, "")
            suggested = " ⭐ [SUGGESTED]" if cat in suggestions else ""
            print(f"   {i}. {cat.replace('_', ' ').title()}{suggested}")
            if desc:
                print(f"      ({desc})")
        
        print(f"   {len(self.categories) + 1}. Create new category")
        print(f"   0. Cancel")
        
        while True:
            choice = input(f"\n   Select category (0-{len(self.categories) + 1}): ").strip()
            
            if choice == '0':
                return None
            
            if choice == str(len(self.categories) + 1):
                return self._create_category(interactive=True)
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.categories):
                    return self.categories[idx]
                else:
                    print("   ❌ Invalid selection.")
            except ValueError:
                print("   ❌ Please enter a number.")
    
    def _suggest_filename(self, original_name: str, category: str) -> Optional[str]:
        """Suggest and confirm filename"""
        
        # Clean filename
        clean_name = re.sub(r'[^\w\s-]', '', original_name).strip()
        clean_name = re.sub(r'[-\s]+', '_', clean_name).lower()
        
        # Add category context if not already present
        category_words = category.split('_')
        has_category = any(word in clean_name for word in category_words)
        
        suggested = clean_name if has_category else f"{category_words[0]}_{clean_name}"
        
        print(f"\n   Suggested filename: {suggested}")
        print(f"   (without extension)")
        
        choice = input("\n   1. Use suggested name\n   2. Enter custom name\n   0. Cancel\n\n   Choice: ").strip()
        
        if choice == '0':
            return None
        elif choice == '2':
            custom = input("   Enter filename: ").strip()
            # Clean custom name
            custom = re.sub(r'[^\w\s-]', '', custom).strip()
            custom = re.sub(r'[-\s]+', '_', custom).lower()
            return custom if custom else suggested
        else:
            return suggested
    
    def _show_categories(self):
        """Show categories and image counts"""
        print("\n📊 Image Categories")
        print("-" * 50)
        
        total = 0
        for cat in self.categories:
            cat_dir = self.images_dir / cat
            image_count = len([f for f in cat_dir.iterdir() if f.is_file()])
            total += image_count
            
            desc = self.category_descriptions.get(cat, "")
            print(f"\n   📁 {cat.replace('_', ' ').title()}: {image_count} images")
            if desc:
                print(f"      {desc}")
        
        print(f"\n   Total: {total} images across {len(self.categories)} categories")
    
    def _create_category(self, interactive: bool = False) -> Optional[str]:
        """Create a new category"""
        print("\n➕ Create New Category")
        print("-" * 50)
        
        cat_name = input("\n   Enter category name (use underscores for spaces): ").strip().lower()
        
        if not cat_name:
            print("   ❌ Category name cannot be empty.")
            return None
        
        # Clean name
        cat_name = re.sub(r'[^\w_]', '', cat_name)
        cat_name = re.sub(r'_+', '_', cat_name)
        
        # Create directory
        cat_dir = self.images_dir / cat_name
        if cat_dir.exists():
            print(f"   ⚠️  Category already exists: {cat_name}")
            return cat_name if interactive else None
        
        try:
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            # Ask for description
            desc = input("   Enter description (optional): ").strip()
            if desc:
                self.category_descriptions[cat_name] = desc
            
            self.categories = self._get_categories()
            print(f"   ✅ Created category: {cat_name}")
            return cat_name
            
        except Exception as e:
            print(f"   ❌ Error creating category: {e}")
            return None
    
    def _rebuild_catalog(self):
        """Rebuild the image catalog"""
        print("\n♻️  Rebuilding Image Catalog...")
        print("-" * 50)
        
        try:
            from image_manager import ImageManager
            manager = ImageManager(str(self.images_dir))
            manager.rebuild_catalog()
            
            stats = manager.get_catalog_stats()
            print(f"\n✅ Catalog rebuilt successfully!")
            print(f"   Total images: {stats['total_images']}")
            print(f"   Categories: {len(stats['categories'])}")
            for cat, count in stats['categories'].items():
                print(f"      - {cat}: {count} images")
            
        except Exception as e:
            print(f"❌ Error rebuilding catalog: {e}")


def main():
    """Main entry point"""
    tool = ImageUploadTool()
    
    try:
        tool.run()
    except KeyboardInterrupt:
        print("\n\n✅ Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
