import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from skimage.io import imread, imsave, imshow
from skimage.color import rgb2gray
from skimage.measure import label, regionprops, regionprops_table

def count_colonies(image_path, save_path):
    colony_image = imread(image_path)

    grayscaled_image, binarized_image = binarize_image(colony_image, 0.55)

    labeled_image = label(binarized_image)
    regions = regionprops(labeled_image)

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

    obvious_filtered_count, obvious_indices = filter_for_obvious(regions)
    non_obvious_filtered_count, non_obvious_indices = filter_for_non_obvious(regions)
    low_ecc_noise_count, low_ecc_indices = filter_for_low_ecc_noise(regions)

    obvious_filtered_image = hide_filtered_regions(colony_image, labeled_image, obvious_indices)
    non_obvious_filtered_image = hide_filtered_regions(colony_image, labeled_image, non_obvious_indices)
    low_ecc_noise_filtered_image = hide_filtered_regions(colony_image, labeled_image, low_ecc_indices)

    display_plots(
        colony_image,
        obvious_filtered_image,
        obvious_filtered_count,
        non_obvious_filtered_image,
        non_obvious_filtered_count,
        low_ecc_noise_filtered_image,
        low_ecc_noise_count,
        save_path
    )

    return obvious_filtered_count, non_obvious_filtered_count, low_ecc_noise_count


def binarize_image(image, threshold):
    grayscaled_image = rgb2gray(image)
    binarized_image = grayscaled_image > threshold
    return grayscaled_image, binarized_image


def filter_for_obvious(regions):
    masks = []
    bboxes = []
    filtered_indices = []

    high_masks = []
    high_bboxes = []
    low_eccentricity_indices = []

    areas = []
    convex_areas = []
    for i, r in enumerate(regions):
        eccentricity = r.eccentricity

        if (
            i != 0 and
            eccentricity < 0.625
        ):
            areas.append(r.area)
            convex_areas.append(r.convex_area)

            high_masks.append(regions[i].convex_image)
            high_bboxes.append(regions[i].bbox)
            low_eccentricity_indices.append(i)

    avg_area = np.average(areas)
    std_area = np.std(areas)

    avg_convex_area = np.average(convex_areas)
    std_convex_area = np.std(convex_areas)

    for i, r in enumerate(regions):
        area = r.area

        if (
            i != 0 and
            i in low_eccentricity_indices and
            area <= avg_area + 1.5 * std_area and
            area >= avg_area - 1.5 * std_area
        ):
            masks.append(regions[i].convex_image)
            bboxes.append(regions[i].bbox)
            filtered_indices.append(i)

    filtered_count = len(filtered_indices)

    return filtered_count, filtered_indices


def filter_for_non_obvious(regions):
    masks = []
    bboxes = []
    filtered_indices = []

    high_masks = []
    high_bboxes = []
    high_eccentricity_indices = []

    for i, r in enumerate(regions):
        area = r.area
        convex_area = r.convex_area
        eccentricity = r.eccentricity

        ### this filter leaves you with non-obvious clusters and potential noise
        if (
            i != 0 and
            eccentricity >= 0.625
        ):
            high_masks.append(regions[i].convex_image)
            high_bboxes.append(regions[i].bbox)
            high_eccentricity_indices.append(i)

    # Iterate over all regions and filter for low eccentricity regions (singular colonies).
    # Calculate singular colony 
    areas = []
    convex_areas = []
    for i, r in enumerate(regions):
        area = r.area
        convex_area = r.area

        if (
            i != 0 and
            i in high_eccentricity_indices
        ):
            areas.append(area)
            convex_areas.append(convex_area)

    avg_area = np.average(areas)
    std_area = np.std(areas)

    avg_convex_area = np.average(convex_areas)
    std_convex_area = np.std(convex_areas)
 
    for i, r in enumerate(regions):
        area = r.area
        convex_area = r.area

        if (
            i != 0 and
            i in high_eccentricity_indices
            # area >= avg_area + 0.5 * std_area or
            # area <= avg_area - 0.5 * std_area
        ):
            masks.append(regions[i].convex_image)
            bboxes.append(regions[i].bbox)
            filtered_indices.append(i)

    filtered_count = len(filtered_indices)

    return filtered_count, filtered_indices


def filter_for_low_ecc_noise(regions):
    masks = []
    bboxes = []
    filtered_indices = []

    high_masks = []
    high_bboxes = []
    noise_indices = []

    areas = []
    convex_areas = []
    for i, r in enumerate(regions):
        eccentricity = r.eccentricity

        if (
            i != 0 and
            eccentricity < 0.625
        ):
            areas.append(r.area)
            convex_areas.append(r.convex_area)

            high_masks.append(regions[i].convex_image)
            high_bboxes.append(regions[i].bbox)
            noise_indices.append(i)

    avg_area = np.average(areas)
    std_area = np.std(areas)

    avg_convex_area = np.average(convex_areas)
    std_convex_area = np.std(convex_areas)

    for i, r in enumerate(regions):
        area = r.area

        if (
            i != 0 and
            i in noise_indices and
            area >= avg_area + 1.5 * std_area or
            area <= avg_area - 1.5 * std_area
        ):
            masks.append(regions[i].convex_image)
            bboxes.append(regions[i].bbox)
            filtered_indices.append(i)

    filtered_count = len(filtered_indices)

    return filtered_count, filtered_indices


def hide_filtered_regions(original_image, labeled_image, indices):
    rgb_mask = np.zeros_like(labeled_image)
    for i in indices:
        rgb_mask += (labeled_image == i + 1).astype(int)

    red   = original_image[:,:,0] * rgb_mask
    green = original_image[:,:,1] * rgb_mask
    blue  = original_image[:,:,2] * rgb_mask

    filtered_image = np.dstack([red, green, blue])

    return filtered_image


def display_plots(
        original_image,
        obvious_image,
        obvious_count,
        non_obvious_image,
        non_obvious_count,
        low_ecc_noise_image,
        low_ecc_noise_count,
        save_path
    ):
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(8, 3))

    ax[0][0].imshow(original_image, cmap='gray')
    ax[0][0].set_title('Original image', fontsize=20)

    ax[0][1].imshow(obvious_image, cmap='gray')
    ax[0][1].set_title(r'Low-ecc. regions: %i' % obvious_count, fontsize=20)

    ax[1][0].imshow(non_obvious_image, cmap='gray')
    ax[1][0].set_title(r'High-ecc. regions: %i' % non_obvious_count, fontsize=20)

    ax[1][1].imshow(low_ecc_noise_image, cmap='gray')
    ax[1][1].set_title(r'Low-ecc. regions outside size range: %i' % low_ecc_noise_count, fontsize=20)

    for a in ax:
        for row in a:
            row.axis('off')

    imsave(f"{save_path}/low-ecc-regions.png", obvious_image)
    imsave(f"{save_path}/high-ecc-regions.png", non_obvious_image)
    imsave(f"{save_path}/low-ecc-oob-regions.png", low_ecc_noise_image)

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    # python colony-counter.py /path/to/file.png /path/to/save
    low_ecc_count, high_ecc_count, low_ecc_noise_count = count_colonies(sys.argv[1], sys.argv[2])

    print(f"Detected {low_ecc_count} low-ecc. regions.")
    print(f"Detected {low_ecc_noise_count} low-ecc. regions outside size range.")
    print(f"Detected {high_ecc_count} high-ecc. regions.")
