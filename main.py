import bpy

label_width = 20

def report(label, data):
    check = 'XXX' if data else ' + '
    result = f': {data}' if data else ''
    label = f'{label}{" "*label_width}'[:max(len(label), label_width)]
    print(f'{check} {label}{result}')

unpacked_images = [
    img.filepath
    for img in bpy.data.images
    if img.filepath and img.users and not img.packed_file
]

library_images = [
    img.library.filepath
    for img in bpy.data.images
    if img.library
]

print(f'results')
print(f'---={"-"*label_width}=-------------------------')
report('unpacked images', unpacked_images)
report('library images', library_images)
