import cv2
import numpy as np
import os

def save_image(image, base_path, suffix):
    """Speichert das Bild im gleichen Verzeichnis wie das Original mit einem angehängten Suffix."""
    directory, filename = os.path.split(base_path)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{suffix}{ext}"
    cv2.imwrite(os.path.join(directory, new_filename), image)

# Pfad zur Bilddatei
image_path = r'F:\Dokumente\Business\Hochschule\Bachelorarbeit\Beispielbilder\Farbwaehler.png'

# Lade das Bild
bgr = cv2.imread(image_path)

# Überprüfe, ob das Bild erfolgreich geladen wurde
if bgr is None:
    print(f"Fehler: Bild konnte nicht geladen werden. Überprüfe den Dateipfad: {image_path}")
    exit()

# Konvertiere das Bild von BGR zu YCrCb
ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)

# Trenne die Y, Cr, Cb Kanäle und konvertiere das Ergebnis in eine Liste
planes = list(cv2.split(ycrcb))

# Erzeuge ein graues Bild mit mittlerer Intensität
gray = np.full((bgr.shape[0], bgr.shape[1]), 128, dtype=np.uint8)

# Erstelle Bilder für die einzelnen Y, Cr, Cb Kanäle
vy = [planes[0], gray.copy(), gray.copy()]
my = cv2.merge(vy)

vcr = [gray.copy(), planes[1], gray.copy()]
mcr = cv2.merge(vcr)

vcb = [gray.copy(), gray.copy(), planes[2]]
mcb = cv2.merge(vcb)

# Speichere die einzelnen Bilder
save_image(bgr, image_path, 'original')
save_image(planes[0], image_path, 'Y_channel')
save_image(planes[1], image_path, 'Cr_channel')
save_image(planes[2], image_path, 'Cb_channel')
save_image(my, image_path, 'Y_colored')
save_image(mcr, image_path, 'Cr_colored')
save_image(mcb, image_path, 'Cb_colored')

# Weichzeichnen des Y-Kanals
planes[0] = cv2.boxFilter(planes[0], ddepth=-1, ksize=(7,7))

# Zusammenführen und Zurückkonvertieren zum BGR-Farbraum
blurred = cv2.merge(planes)
blurred = cv2.cvtColor(blurred, cv2.COLOR_YCrCb2BGR)

# Speichere das weichgezeichnete Bild
save_image(blurred, image_path, 'blurred')
