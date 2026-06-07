import os
import subprocess
import glob

def convert_to_avif():
    print("Starting AVIF Conversion via Python Controller...")
    # Find all images
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp']
    files = []
    for ext in extensions:
        files.extend(glob.glob(f"manga/**/{ext}", recursive=True))
    
    print(f"Found {len(files)} images to convert.")
    
    count = 0
    for file in files:
        dir_name = os.path.dirname(file)
        # Using npx avif-cli
        # We use -y to skip prompt
        try:
            cmd = ["npx", "-y", "avif", file, "--output", dir_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                os.remove(file)
                count += 1
                if count % 10 == 0:
                    print(f"Converted {count}/{len(files)}...")
            else:
                print(f"Failed to convert {file}: {result.stderr}")
        except Exception as e:
            print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    convert_to_avif()
