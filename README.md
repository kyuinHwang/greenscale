# GreenScale
# A GUI program for non-destructive body weight estimation of *Deschampsia antarctica* (Antarctic flowering plant) from photograph taken in the field.

GreenScale is developed to estimate the body weight of individual plants in a non-destructive way. 
The software processes field photographs of single plants, detects and counts greenish pixels corresponding to plant body, and uses a pre-trained regression model to estimate body weight from the pixel counts.
While current implementation is optimized for the Antarctic flowering plant *Deschampsia antarctica*, the methodology can be widely adapted to other plant species by rebuilding pre-trained regression model.

## Installation
### 1. Requirements
This software requires Python 3.10 or higher.
It requires the following Python packages: numpy, Pillow (for image handling), and packaging (for version comparison). You can install them via pip if not already installed:

```bash
$pip install numpy pillow packaging
# or
$conda install numpy pillow packaging
```

### 2. Clone the repository

```bash
$git clone https://github.com/kyuinHwang/greenscale.git
$cd greenscale
```

Cloning the repository and setting up the pipeline takes only a few seconds on a standard system.

## Usage
### Field work (Image preparation)

1. Position the camera directly above the target plant, keeping it parallel to the ground. Take photographs from multiple angles and distances to capture the plant thoroughly.

2. To provide a scale reference, put a coin or other known-size object near the plant.

3. It is recommended to take at least 10 photographs per individual plant, capturing the plant from different angles (e.g., rotating around the plant) to account for variations in lighting and perspective.

4. Ensure that the target plant is not occluded by other objects (e.g., soil or coin), and try to avoid including unrelated greenish pixels (e.g., mosses) in the photo.

*Note: The example photograph can be found in `examples`.*

### Running GreenScale
To launch GreenScale, you can:
- Run the `GreenScale.py` script according to your system setup. For example, you can:
-- Double-click the file (if your OS supports it),
-- Right-click and select "Run" or similar option, or
-- Open it in Python IDLE and run the script.

- or **Run from the terminal/command prompt**:

``` bash
python GreenScale.py
```

This will open the GreenScale GUI. Once the GUI window appears, you can navigate through the interface using the buttons.

1. Load Image

- Click the *"Load file"* button and select a prepared photograph of the individual plant.
- Cropping window is automatically appears for the selected photograph

2. Define Scale Reference

- Click the *"SelectCoin"* button.
- Click two points on opposite edges of the coin on the image to measure its diameter.
- This allows GreenScale to calibrate the pixel-to-area conversion for accurate body weight estimation.

3. Crop Plant Region

- Click the *"SelectTarget"* button.
- Click two points corresponding to the top-left and bottom-right corners of the plant, ensuring the entire plant is included.
- If you make a mistake during the operation, click the *"Reload"* button to reset.
- Denoising window is automatically appears for selected region. The greenish pixels of the plant are highlighted in this window.

4. Denoise

- Mask incorrectly detected greenish pixels by rubbing over them using a mouse.
- Masked pixels will not be counted as plant pixel.

5. Biomass estimation

- Click the *"GetMass"* button for calculation. This will yield a total number of pixels of a plant body, the coin radius, the plant pixels calibrated by the coin size, the estimated fresh body weight, and the estimated dry body weight in that order.
- If you make a mistake during the operation, click the *"Clear"* button to reset.

*Repeat Steps 1,2,3,4, and 5 for each photograph*

6. Get Statistics

- Click the *"GetAverage"* button to get average body weight values.
- Check the *"exclude outliers"* checkbox if you want to exclude outliers from the body weight values estimated from multiple photographs.
- Before save result, enter the name of the plant sample in the top-left field labeled "PutSampleName".
- Click the *"SaveSampleData"* button to save the average body weight values per individual plant in csv file (Results.sample.txt).
- Click the *"SavePhotoData"* button to save the body weight values per individual photos in csv file (Results.photo.txt).

*Close the main window and launch GreenScale again if you need to process photographs of another plant*

*Note:* If you have already sorted multiple photographs of each plant into separate directories (e.g. ./plant1/plant1_1stphoto.jpg, ./plant1/plant1_2ndphoto.jpg), you can use *'Load Dir'* button instead.

## License

This repository is released under the MIT License.  
It is officially registered with the Korea Copyright Commission (Registration No. C-2021-014883).

## Contact
If you encounter a problem or have a question, please open an issue on this repository:
👉 [Submit an issue](https://github.com/kyuinHwang/greenscale/issues)

For direct inquiries, you may contact the maintainer at: rbdls77@gmail.com

## Contribution

Dr. Kyung Mo Kim (Korea Polar Research Institute; email: kmkim@kopri.re.kr) has designed the Software and developed its core algorithms.

Dr. Kyuin Hwang (Korea Polar Research Institute; emalil: rbdls77@gmail.com) has developed GUI program


## Version changes
### Stable v3.3.1 - 20250822
Add headers into the result csv files
