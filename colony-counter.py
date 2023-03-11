print("[0] Initializing dependency importing...")
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage.io import imread, imshow
from skimage.color import rgb2gray
from skimage.morphology import (
    erosion,
    dilation,
    closing,
    opening,
    area_closing,
    area_opening
)
from skimage.measure import label, regionprops, regionprops_table
print("[1] Importing done!")

def count_colonies(image_path):
    colony_image = imread(image_path)
    imshow(colony_image)
    plt.show()
    
    grayscaled_image, binarized_image = binarize_image(colony_image, 0.5)
    imshow(grayscaled_image)
    plt.show()
    imshow(binarized_image)
    plt.show()

    labeled_image = label(binarized_image)
    regions = regionprops(labeled_image)

    imshow(labeled_image)
    plt.show()

    properties = [
        "area",
        "convex_area",
        "bbox_area",
        "extent",
        "mean_intensity",
        "solidity",
        "eccentricity",
        "orientation"
    ]
    rt = regionprops_table(labeled_image, grayscaled_image, properties=properties)
    df = pd.DataFrame(rt)

    print("Region properties DataFrame:")
    print(df)

    filtered_count, indices = filter_regions(regions)

    hide_filtered_regions(colony_image, labeled_image, indices)
    return filtered_count

def binarize_image(image, threshold):
    grayscaled_image = rgb2gray(image)
    binarized_image = grayscaled_image > threshold
    return grayscaled_image, binarized_image


def filter_regions(regions):
    print("*** Filtering detected regions ***")
    masks = []
    bbox = []
    indices = []

    avg_area = -1
    avg_convex_area = -1

    # determine averages among regions
    for i, r in enumerate(regions):
        area = r.area
        convex_area = r.convex_area

        avg_area += area
        avg_convex_area += convex_area

    avg_area /= len(regions)
    avg_convex_area /= len(regions)

    print(f"average region area: {avg_area}")
    print(f"average region convex area: {avg_convex_area}")

    for i, r in enumerate(regions):
        area = r.area
        convex_area = r.convex_area
        eccentricity = r.eccentricity

        ### this filter leaves you with obvious colonies
        # if (
        #     i != 0 and
        #     area > avg_area and
        #     eccentricity < 0.625
        #     # convex_area / area < 1.05 and
        #     # convex_area / area > 0.95
        # ):
        #     masks.append(regions[i].convex_image)
        #     bbox.append(regions[i].bbox)   
        #     indices.append(i)


        ### this filter leaves you with non-obvious colonies
        if (
            i != 0 and
            area > avg_area and
            eccentricity >= 0.625
            # convex_area / area < 1.05 and
            # convex_area / area > 0.95
        ):
            masks.append(regions[i].convex_image)
            bbox.append(regions[i].bbox)   
            indices.append(i)

    filtered_count = len(masks)
    print(f"Filtered out {len(regions) - filtered_count} regions out of {len(regions)} regions.")
    print(f"Final region count: {filtered_count}.")

    return filtered_count, indices

def hide_filtered_regions(original_image, labeled_image, indices):
    rgb_mask = np.zeros_like(labeled_image)
    for i in indices:
        rgb_mask += (labeled_image == i + 1).astype(int)

    red   = original_image[:,:,0] * rgb_mask
    green = original_image[:,:,1] * rgb_mask
    blue  = original_image[:,:,2] * rgb_mask

    filtered_image = np.dstack([red, green, blue])
    print("Filtered image shown now.")
    imshow(filtered_image)
    plt.show()
    return

if __name__ == "__main__":
    # python colony-counter.py -help
    # python colony-counter.py -about
    # python colony-counter.py -a count -p ~/path/to/file.png

    first_arg = sys.argv[1]

    if first_arg == "-help":
        print("Basic usage: python colony-counter.py -a count -p ~/path/to/file.png")
    elif first_arg == "-about":
        pass
    elif first_arg == "-a":
        count_colonies(sys.argv[4])
