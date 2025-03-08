This script automates the process of searching and downloading images based on exact filenames specified in a text file.

Features

✅ Preserves Exact Filenames – No suffixes or modifications added.
✅ Maintains File Extensions – Uses the extension from your filename or defaults to .jpg if not specified.
✅ Multi-Search Engine Support – Searches using Bing first, then Google if necessary.
✅ Simplified Interface – Just provide a text file and an output directory.

How It Works

Reads filenames from the provided text file.
Searches for images using each filename (without modifications).
Downloads the first matching image that exactly matches the filename.
Saves images to the specified output directory.

How to use it:

python find.py files.txt --output-dir ./images

Your text file should contain filenames like:

Example1.jpg
Example2.png
Example3.webp

The script will download these images with exactly those filenames to your specified output directory.
