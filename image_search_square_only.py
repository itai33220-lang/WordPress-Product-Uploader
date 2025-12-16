#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Search - SQUARE IMAGES ONLY VERSION
Modified version of image_search_ai_verified.py that filters for square images
"""

import requests
from PIL import Image
from io import BytesIO

# Same site lists as original
TIER1_BRAND_SITES = [
    "shimano.com",
    "sram.com",
    "giant-bicycles.com",
    "specialized.com",
    "trek.com",
    "cannondale.com",
    "scott-sports.com",
    "continental-tires.com",
    "schwalbe.com",
    "maxxis.com",
    "fox.com",
    "rockshox.com",
    "campagnolo.com",
    "canyon.com",
    "santacruzbicycles.com",
    "pivotcycles.com",
    "yetibikes.com",
    "ibiscycles.com"
]

TIER2_SAFE_RETAILERS = [
    "bike-components.de",
    "bike-discount.de",
    "rosebikes.com",
    "bike-mailorder.com",
    "merlincycles.com",
    "probikekit.com",
    "sigmasports.com",
    "tredz.co.uk",
    "cyclestore.co.uk",
    "probikeshop.com",
    "alltricks.com",
    "mantel.com",
    "bikeinn.com",
    "chainreactioncycles.com",
    "wiggle.com"
]

BIKE_RETAIL_SITES = TIER1_BRAND_SITES + TIER2_SAFE_RETAILERS

ISRAELI_BIKE_SITES = [
    "bikemarket.co.il",
    "2ride.co.il",
    "bikeinn.co.il",
    "fridman.co.il",
    "matzman-merutz.co.il",
    "bikesonline.co.il",
    "pedalim.co.il",
    "danielbicycles.co.il",
    "shop.harim.co.il"
]


def is_square_image(width, height, tolerance=0.05):
    """
    Check if image is square within tolerance
    
    Args:
        width: Image width
        height: Image height
        tolerance: Aspect ratio tolerance (0.05 = 5%)
    
    Returns:
        bool: True if square
    """
    if width <= 0 or height <= 0:
        return False
    
    aspect_ratio = width / height
    return (1 - tolerance) <= aspect_ratio <= (1 + tolerance)


def search_google_images_square_only(query, api_key, search_engine_id, num_results=10, israeli_product=False):
    """
    Search for SQUARE images only from bike retail sites
    
    This version filters out non-square images to prevent alignment issues in product grids
    """
    try:
        sites_to_search = ISRAELI_BIKE_SITES if israeli_product else BIKE_RETAIL_SITES
        site_restriction = " OR ".join([f"site:{site}" for site in sites_to_search])
        full_query = f"{query} ({site_restriction})"
        
        print(f"\n{'='*70}")
        print(f"🔍 Searching for SQUARE images: {query}")
        print(f"🌍 Searching {len(sites_to_search)} {'Israeli' if israeli_product else 'international'} sites")
        print(f"🎯 Filter: Square images only (1:1 ratio)")
        print(f"{'='*70}\n")
        
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': full_query,
            'searchType': 'image',
            'num': 10,  # Get extra to filter
            'imgSize': 'large',
            'imgType': 'photo',
            'safe': 'active',
            'imgDominantColor': 'white',
            'fileType': 'jpg,png',
            'imgColorType': 'color',
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'items' in data:
                square_images = []
                
                print(f"   Found {len(data['items'])} total images")
                print(f"   Filtering for square images...\n")
                
                for idx, item in enumerate(data['items'], 1):
                    if 'link' not in item:
                        continue
                    
                    width = item.get('image', {}).get('width', 0)
                    height = item.get('image', {}).get('height', 0)
                    
                    print(f"   Image {idx}: {width}x{height} → ", end='')
                    
                    if is_square_image(width, height):
                        print("✅ SQUARE - ACCEPTED")
                        square_images.append({
                            'url': item['link'],
                            'title': item.get('title', ''),
                            'snippet': item.get('snippet', ''),
                            'context': item.get('image', {}).get('contextLink', ''),
                            'width': width,
                            'height': height,
                        })
                        
                        if len(square_images) >= num_results:
                            break
                    else:
                        aspect = width / height if height > 0 else 0
                        print(f"❌ NOT SQUARE (ratio: {aspect:.2f}) - REJECTED")
                
                print(f"\n   ✅ Found {len(square_images)} square images")
                return square_images
            else:
                print("   ❌ No results found")
                return []
        else:
            error_data = response.json() if response.text else {}
            raise Exception(f"Google API Error {response.status_code}: {error_data.get('error', {}).get('message', 'Unknown error')}")
    
    except Exception as e:
        raise Exception(f"Error searching images: {str(e)}")


def download_image(url, timeout=10):
    """Download an image from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        referer = f"{parsed.scheme}://{parsed.netloc}/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': referer,
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img, response.content
        
        return None, None
    
    except Exception as e:
        print(f"      Error: {e}")
        return None, None


def make_square_image(img, size=500):
    """Convert image to square with WHITE background"""
    # Create WHITE background
    square = Image.new('RGB', (size, size), (255, 255, 255))
    
    # Handle different image modes
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode == 'P':
        img = img.convert('RGB')
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize image to fit in square
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    
    # Center the image
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    
    square.paste(img, (x, y))
    
    return square


def fetch_square_product_images(
    product_name, 
    product_specs,
    google_api_key,
    google_search_id,
    max_images=10,
    israeli_product=False
):
    """
    Fetch SQUARE product images only
    
    This version ensures all returned images are square (1:1 ratio) to prevent
    alignment issues in product grids
    """
    
    print(f"\n{'='*70}")
    print(f"🔍 Searching for SQUARE images: {product_name}")
    print(f"📋 Product specs: {product_specs}")
    print(f"{'='*70}\n")
    
    # Build search term
    search_term = product_specs.get('search_term', product_name)
    
    # Search for square images
    results = search_google_images_square_only(
        query=search_term,
        api_key=google_api_key,
        search_engine_id=google_search_id,
        num_results=max_images,
        israeli_product=israeli_product
    )
    
    if not results:
        print("❌ No square images found")
        return []
    
    print(f"\n{'='*70}")
    print(f"📥 Downloading {len(results)} square images...")
    print(f"{'='*70}\n")
    
    all_images = []
    
    for img_num, result in enumerate(results, 1):
        print(f"   Image {img_num}/{len(results)}:")
        print(f"      URL: {result['url'][:80]}...")
        print(f"      Size: {result['width']}x{result['height']} (square)")
        
        original_url = result['url']
        
        # Download image
        img, img_bytes = download_image(original_url)
        
        if not img or not img_bytes:
            print(f"      ❌ Download failed\n")
            continue
        
        # Verify it's actually square
        width, height = img.size
        if not is_square_image(width, height):
            print(f"      ⚠️  WARNING: Image not square after download ({width}x{height})")
            print(f"      Converting to square...\n")
        else:
            print(f"      ✅ Verified square: {width}x{height}")
        
        # Always ensure 500x500 square
        square_img = make_square_image(img, 500)
        print(f"      📐 Final: 500x500 square")
        
        output = BytesIO()
        square_img.save(output, format='JPEG', quality=95)
        final_bytes = output.getvalue()
        
        all_images.append((final_bytes, 'image/jpeg', original_url))
        
        print(f"      ✅ Added ({len(all_images)}/{max_images})\n")
    
    if all_images:
        print(f"{'='*70}")
        print(f"🎉 SUCCESS! Found {len(all_images)} square images")
        print(f"{'='*70}\n")
    else:
        print(f"{'='*70}")
        print(f"❌ No images downloaded successfully")
        print(f"{'='*70}\n")
    
    return all_images
