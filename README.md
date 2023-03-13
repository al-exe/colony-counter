# colony-counter
Colony Counter is a tool used to aid in MMEJ (microhomology-mediated end joining) research.

## Usage
`python colony-counter.py -a count -p ~/path/to/file.png`

## Background knowledge:

### Eccentricity:
At a high level, the eccentricity of an ellipses describes how "oval-like" it is. A value of 0 indicates that the ellipses is a circle. A value of 1 indicates that the ellipses is a parabola.

We use eccentricity to filter out singular colonies (which are often very circluar) and separate them from colony clusters.

A visualization of eccentricity:
https://www.mathsisfun.com/geometry/eccentricity.html
