# colony-counter
Colony Counter is a tool written in Python used to aid in MMEJ (microhomology-mediated end joining) research by counting the total number of cell colonies in an image. It leverages the combined power of NumPy and Scikit to accomplish this.

![colony-plots](https://user-images.githubusercontent.com/20894826/224611605-6bbcacec-b4e6-417f-a686-6e1cdabf7352.png)
*Plots of filtered image.*

## Basic usage
#### To run on a single image:

`python colony-counter.py /path/to/file.png /path/to/save/directory`

This command will generate 3 files:
- `low-ecc-regions-in-size-range`: this image ideally contains all singular colonies. Regions in this image have low-eccentricity (are circle-like) and are within 1.5 standard deviations of the average region size.
- `low-ecc-regions-out-size-range`: this image contains colony clusters and noise. Regions in this image have low-eccentricity (are circle-like), but are outside the 1.5 standard deviation range from the average region size. 
- `high-ecc-regions`: this image ideally contains all colony clusters. Regions in this image have high-eccentricity (are oval-like). Visual artifacts (e.g. the wall of the petri dish) are usually present as well.

Users are advised to check over each resultant image and add or subtract from the given count whenever an unexpected region is detected.

## Pitfalls
Users should be aware of a few pitfalls when using `colony-counter`:
- Colonies attached to the petri dish wall may be discarded due to filtering. If a petri dish wall is present in the original image and removed in filtering, the user should count them from the original image.
- Remnant visual artificats may remain even after filtering. Users should review all resultant images and confirm that no extra regions (e.g. text, walls, noise) were left after filtering.

## Background knowledge:

### Eccentricity:
At a high level, the eccentricity of an ellipses describes how "oval-like" it is. A value of 0 indicates that the ellipses is a circle. A value of 1 indicates that the ellipses is a parabola.

We use eccentricity to filter out singular colonies (which are often very circluar) and separate them from colony clusters. To further filter singular colonies, we apply a size filter of +/- 1.5 standard deviations from the average.

A visualization of eccentricity:
https://www.mathsisfun.com/geometry/eccentricity.html
