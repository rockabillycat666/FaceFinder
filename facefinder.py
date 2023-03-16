import os
import cv2
import face_recognition
import imghdr
import shutil
from PIL import Image

def get_encodings(image_paths):
    encodings = []
    for image_path in image_paths:
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) > 0:
            encodings.append(face_encodings[0])
    return encodings

def create_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    image = Image.open(image_path)
    image.thumbnail(size)
    image.save(thumbnail_path)

def find_files_with_face(face_encodings, source_folder, destination_folder):
    matched_files = []

    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)

            if imghdr.what(file_path) is not None:
                image = face_recognition.load_image_file(file_path)
                target_face_encodings = face_recognition.face_encodings(image)

                for target_encoding in target_face_encodings:
                    matches = face_recognition.compare_faces(face_encodings, target_encoding)
                    if True in matches:
                        print(f"Found a match: {file_path}")
                        matched_files.append(file_path)

                        if not os.path.exists(destination_folder):
                            os.makedirs(destination_folder)

                        thumbnail_folder = os.path.join(destination_folder, "thumbnails")
                        if not os.path.exists(thumbnail_folder):
                            os.makedirs(thumbnail_folder)

                        thumbnail_path = os.path.join(thumbnail_folder, file)
                        create_thumbnail(file_path, thumbnail_path)

    return matched_files

def generate_html(matched_files, destination_folder):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Recognition Results</title>
    <style>
        body {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            padding: 20px;
        }
        img {
            margin: 10px;
            border: 1px solid #ccc;
            box-shadow: 2px 2px 6px 0px rgba(0, 0, 0, 0.3);
            cursor: pointer;
        }
    </style>
</head>
<body>
    """

    for file_path in matched_files:
        thumbnail_path = os.path.join(destination_folder, "thumbnails", os.path.basename(file_path))
        html += f'<a href="{file_path}" target="_blank"><img src="{thumbnail_path}" alt="Thumbnail"></a>\n'

    html += """
</body>
</html>
    """

    with open(os.path.join(destination_folder, "index.html"), "w") as f:
        f.write(html)

def main():
    reference_images = input("Enter the paths of the reference images (separated by commas): ").split(',')
    reference_images = [image.strip() for image in reference_images]
    source_folder = input("Enter the path of the folder to search in: ")
    destination_folder = input("Enter the path of the folder to save matches: ")

    reference_face_encodings = get_encodings(reference_images)

    if len(reference_face_encodings) == 0:
        print("No face found in the reference images.")
        return


    matched_files = find_files_with_face(reference_face_encodings, source_folder, destination_folder)

    if len(matched_files) == 0:
        print("No matches found.")
    else:
        generate_html(matched_files, destination_folder)
        print(f"Generated HTML file with matched images at {os.path.join(destination_folder, 'index.html')}")

if __name__ == "__main__":
    main()
