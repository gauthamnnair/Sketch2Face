import os
import json
import random

# Directories and file listing
photos_dir = r'Kaggle/photos/'
photo_files = sorted(os.listdir(photos_dir))  # Ensuring consistent ordering

# Sample names
male_first_names = ["John", "Michael", "David", "James", "Robert", "William", "Richard", "Joseph", "Charles", "Thomas", "Stephen", "Carlos", "Elon", "Ross"]
female_first_names = ["Mary", "Jennifer", "Jessica", "Linda", "Emily", "Sarah", "Karen", "Lisa", "Nancy", "Sandra", "Queen", "Scarlet", "Bretney", "Elisa"]
last_names = ["Smith", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Martinez"]

# Random crime list
crimes = [
    "Theft", "Burglary", "Fraud", "Assault", "Arson", "Drug Trafficking", "Money Laundering", 
    "Kidnapping", "Murder", "Cyber Crime"
]

# Generate unique name pairs
used_names = set()
records = []
count = 0

for file in photo_files:
    if file.lower().endswith(('.jpg', '.png', '.jpeg')):  # Ensure valid image files
        if file.startswith('f'):
            first_name = random.choice(female_first_names)
        elif file.startswith('m'):
            first_name = random.choice(male_first_names)
        else:
            continue  # Skip files that don't start with 'f' or 'm'
        
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Ensure uniqueness
        while full_name in used_names:
            first_name = random.choice(female_first_names if file.startswith('f') else male_first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
        
        used_names.add(full_name)
        
        record = {
            "name": full_name,
            "crime": random.choice(crimes),
            "photo": file
        }
        records.append(record)
        count += 1 
        print(count)

# Save to JSON file
output_file = 'criminal_records.json'
with open(output_file, 'w') as f:
    json.dump(records, f, indent=4)

print(f"Criminal records saved to {output_file}")
