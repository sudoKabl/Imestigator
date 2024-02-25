import cv2
from scipy.fftpack import dct, idct
import numpy as np

path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\tree_gauss_test_2.jpg"

def dct2(a):
    # Perform the DCT on rows
    tmp = dct(a, axis=0, norm='ortho')
    # Then perform the DCT on columns
    return dct(tmp, axis=1, norm='ortho')

img = cv2.imread(path_org)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
(height, width) = img_gray.shape

# Initialize a collection to store all DCT blocks
dct_blocks = np.zeros((height // 8, width // 8, 8, 8), np.float64)

# Collecting DCT blocks
for x in range(0, width, 8):
    for y in range(0, height, 8):
        block = img_gray[y:y+8, x:x+8]
        
        if block.shape[0] == 8 and block.shape[1] == 8:
            dct_arr = dct2(block)
            dct_blocks[y // 8, x // 8] = dct_arr

# Calculate the variance for each coefficient
variances = np.var(dct_blocks, axis=(0, 1))

# For demonstration, set a threshold for variance to consider as significant
variance_threshold = variances.mean()

# Check each DCT block against variances
min_significant_coeffs = 5  # Minimum number of coefficients that must exceed the variance threshold
blocks_with_significant_variance = 0

for block in np.reshape(dct_blocks, (-1, 8, 8)):
    significant_coeffs = np.sum(np.abs(block) > variance_threshold, axis=(0, 1))
    if significant_coeffs >= min_significant_coeffs:
        blocks_with_significant_variance += 1

print(f"Blocks with at least {min_significant_coeffs} coefficients exceeding the average variance: {blocks_with_significant_variance}")