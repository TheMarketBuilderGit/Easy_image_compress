import os
import sys
import time
import threading
from PIL import Image
from send2trash import send2trash  # Moves files to the Recycle Bin

# Define the minimum file size in bytes (1 MB)
MIN_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

def process_images(folder):
    """
    Processes eligible images in the given folder:
      - Supported extensions: PNG, JPG, JPEG.
      - File name does NOT include '_optim'.
      - File size is greater than 1 MB.
    
    For each qualifying image:
      1. Opens the image.
      2. Calculates new dimensions (75% of the original).
      3. Resizes using bicubic interpolation.
      4. Saves as JPEG with quality=90 and '_optim' appended to the filename.
      5. Moves the original file to the Recycle Bin.
    """
    # Supported extensions (lowercase for consistency)
    supported_ext = {".png", ".jpg", ".jpeg"}
    
    for filename in os.listdir(folder):
        name, ext = os.path.splitext(filename)
        file_path = os.path.join(folder, filename)
        
        # Debug: list all files considered.
        print(f"Found file: {filename} \n")
        
        # Process only supported files that do not have the '_optim' suffix.
        if ext.lower() in supported_ext and not name.endswith("_optim"):
            file_size = os.path.getsize(file_path)
            print(f"  -> Eligible extension. Size: {file_size/1024:.2f} KB")
            
            if file_size > MIN_FILE_SIZE:
                try:
                    with Image.open(file_path) as img:
                        # Compute new dimensions (75% of the original)
                        new_width = int(img.width * 0.75)
                        new_height = int(img.height * 0.75)
                        new_dimensions = (new_width, new_height)
                        
                        # Resize using bicubic resampling.
                        resized_img = img.resize(new_dimensions, resample=Image.BICUBIC)
                        
                        # Create new filename with '_optim' suffix.
                        new_filename = f"{name}_optim.jpg"
                        new_file_path = os.path.join(folder, new_filename)
                        
                        # Save as JPEG with quality=90.
                        resized_img.save(new_file_path, "JPEG", quality=90)
                        print(f"  Converted '{filename}' -> '{new_filename}'")
                        
                        # Move the original file to the Recycle Bin.
                        send2trash(file_path)
                        print(f"  Moved original file '{filename}' to the Recycle Bin.")
                except Exception as e:
                    print(f"  Error processing '{filename}': {e}")
            else:
                print(f"  Skipped '{filename}' (size is less than 1 MB)")
        else:
            print(f"  Skipped '{filename}' (unsupported file or already optimized)")

if __name__ == "__main__":
    # Determine the folder where the executable resides when frozen,
    # otherwise use the script's directory.
    if getattr(sys, 'frozen', False):
        current_folder = os.path.dirname(sys.executable)
    else:
        current_folder = os.path.dirname(os.path.abspath(__file__))
    
    # Print initial messages and start processing concurrently.
    print("-------------------------------")
    print("")
    print("Easy_image_compress running")
    print("The old files will be moved to the Recycle Bin")
    print("") 
    print("-------------------------------")
    
    # Start the image processing in a separate thread.
    processing_thread = threading.Thread(target=process_images, args=(current_folder,))
    processing_thread.start()
    
    # Sleep 2 seconds in the main thread so the initial message remains visible.
    time.sleep(2)
    
    # Wait for the image processing to finish.
    processing_thread.join()
    
    print("""\n
  _____   ___   _   _  ______ 
 |  __ \ / _ \ | \ | ||  ____|
 | |  | | | | ||  \| || |__   
 | |  | | | | || . ` ||  __|  
 | |__| | |_| || |\  || |____ 
 |_____/ \___/ |_| \_||______|
\n""")
    print("Conversion complete. Original files placed in the Recycle Bin. The program will exit automatically.")
    time.sleep(1)
    sys.exit(0)
