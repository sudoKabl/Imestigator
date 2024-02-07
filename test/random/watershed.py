import cv2
import numpy as np

def watershed_segmentation(image_path):
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Noise removal
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # Sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    markers = cv2.watershed(image, markers)
    image[markers == -1] = [255, 0, 0]

    return image, markers

def rasterize_and_quantize(image, markers, grid_size):
    h, w = image.shape[:2]
    rasterized_image = np.copy(image)

    for i in range(0, w, grid_size):
        for j in range(0, h, grid_size):
            grid = markers[j:j+grid_size, i:i+grid_size]
            if not np.any(grid == -1):  # If no segment boundary in grid
                rasterized_image[j:j+grid_size, i:i+grid_size] = 0  # Set grid to black

    return rasterized_image

# Apply watershed and then rasterize
image_path = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\ufo.cache-1.jpg"
grid_size = 10  # Adjust grid size as needed

segmented_image, markers = watershed_segmentation(image_path)
rasterized_image = rasterize_and_quantize(segmented_image, markers, grid_size)

# Display or save the result
cv2.imshow('Rasterized Image', rasterized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optionally, save the image
# cv2.imwrite('rasterized_image.jpg', rasterized_image)
