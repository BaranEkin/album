from pathlib import Path
from PIL import Image
import os
import re


def resize_thumbnails(folder_path):
    image_extensions = {".jpg", ".jpeg"}

    thumbnail_paths = [
        str(file)
        for file in folder_path.rglob("*")
        if file.suffix.lower() in image_extensions
    ]

    for i, path in enumerate(thumbnail_paths):
        try:
            img = Image.open(path)
            w, h = img.size
            if not (w == 320 and h == 240):
                img.thumbnail((160, 160))

            new_path = path.replace("\\Foto", "\\")
            directory = os.path.dirname(new_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            img.save(new_path, "JPEG")
            # os.remove(path)
            # print(i)

        except Exception as e:
            print(e)
            continue


def fix_csv(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace all new lines with "\n", except those that come after ";any_digit"
    # The pattern looks for ";[0-9]" followed by a newline and preserves those newlines
    fixed_content = re.sub(r';\d\n', lambda match: match.group(0), content)
    fixed_content = fixed_content.replace('\n', '\\n')
    # Restore the newlines after ";any_digit"
    fixed_content = re.sub(r';\d\\n', lambda match: match.group(0).replace('\\n', '\n'), fixed_content)

    # Create a new file name with "_fixed" suffix
    file_dir, file_name = os.path.split(file_path)
    file_name_without_ext, ext = os.path.splitext(file_name)
    new_file_name = f"{file_name_without_ext}_fixed{ext}"
    new_file_path = os.path.join(file_dir, new_file_name)

    # Write the fixed content to a new file
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(fixed_content)

    print(f"Fixed file saved as {new_file_path}")


if __name__ == "__main__":
    fix_csv("C:/album-2/res/database/album.csv")
