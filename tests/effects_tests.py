from app.ornaments.effects import apply_histogram_specification
from app.ornaments.effects import apply_brightness
from app.ornaments.effects import apply_blur
from app.ornaments.effects import apply_histogram_equalization
from app.ornaments.effects import apply_contrast
import cv2

def test_apply_brightness():
    img = cv2.imread("assets/ornaments/ornament5.png",cv2.IMREAD_UNCHANGED)
    output = apply_brightness(img,50)

    cv2.imwrite("tests/assets/output_brightness.png", output)

def test_apply_contrast():
    img = cv2.imread("assets/tree.png", cv2.IMREAD_UNCHANGED)   # keeps alpha if present
    output = apply_contrast(img,2)

    cv2.imwrite("tests/assets/output_contrast.png", output)

def test_apply_blur():
    img = cv2.imread("assets/tree.png", cv2.IMREAD_UNCHANGED)   # keeps alpha if present
    output = apply_blur(img,10)

    cv2.imwrite("tests/assets/output_blur.png", output)

def test_apply_histogram_equalization():
    img = cv2.imread("assets/tree.png", cv2.IMREAD_UNCHANGED)   # keeps alpha if present
    output = apply_histogram_equalization(img)

    cv2.imwrite("tests/assets/output_histogram_equalization.png", output)

def test_apply_histogram_specification():
   # run from project root so these relative paths are valid
    src = cv2.imread("assets/tree.png", cv2.IMREAD_UNCHANGED) 
    ref = cv2.imread("assets/artworks/vangogh.jpeg", cv2.IMREAD_COLOR)  # reference color image

    print("src shape:", src.shape)
    print("ref shape:", ref.shape)

    out = apply_histogram_specification(src, ref, match_luminance=False, debug=True)
    cv2.imwrite("tests/assets/output_hist_spec.png", out)


if __name__ == "__main__":
    test_apply_brightness()
    test_apply_contrast()
    test_apply_blur()
    test_apply_histogram_equalization()
    test_apply_histogram_specification()
