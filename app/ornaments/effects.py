# app/ornaments/effects.py
from PIL import Image
import cv2
import numpy as np

def convert_to_np_array(img):
    """Convert image to numpy array if not already."""
    if isinstance(img, np.ndarray):
        img_np = img
    else:
        img_np = np.array(img)
    
    # Separate alpha if present
    alpha = None
    if img_np.shape[2] == 4:
        alpha = img_np[:, :, 3]
        img_np = img_np[:, :, :3]
    
    return img_np, alpha

def reattach_alpha(img_np, alpha):
    # Reattach alpha if needed
    if alpha is not None:
        return np.dstack((img_np, alpha))

def apply_brightness(img, value=0):
    """
    Apply brightness safely.
    img: PIL.Image
    value: signed integer, can be negative
    """
    img_np, alpha = convert_to_np_array(img)
    
    # Convert to signed int16 temporarily
    img_np = img_np.astype(np.int16)
    img_np += value  # signed addition
    img_np = np.clip(img_np, 0, 255).astype(np.uint8)  # clip to valid range

    res = reattach_alpha(img_np, alpha)
    return Image.fromarray(res)

def apply_contrast(img, value=5):
    """
    Adjust contrast of the image.
    alpha > 1 increases contrast, 0 < alpha < 1 decreases contrast.
    """
    img_np, alpha = convert_to_np_array(img)
    img_np = img_np.astype(np.float32)  # prevent clipping
    img_np = img_np * value
    img_np = np.clip(img_np, 0, 255).astype(np.uint8)
    res = reattach_alpha(img_np, alpha)
    return Image.fromarray(res)

def apply_blur(img, ksize=5):
    """
    Apply Gaussian blur. ksize must be odd.
    """
    if ksize % 2 == 0:
        ksize += 1
    
    img_np, alpha = convert_to_np_array(img)
    img_np = cv2.GaussianBlur(img_np, (ksize, ksize), 0)
    res = reattach_alpha(img_np, alpha)
    return Image.fromarray(res)

def apply_mosaic(img, scale=0.05):
    img_np, alpha = convert_to_np_array(img)
    h, w = img_np.shape[:2]

    # ensure at least 1 pixel
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    small = cv2.resize(img_np, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    if alpha is not None:
        mosaic = np.dstack((mosaic, alpha))

    return Image.fromarray(mosaic)

def apply_histogram_equalization(img):
    """
    Apply histogram equalization to improve contrast.
    Works on grayscale or color images.
    """
    if len(img.shape) == 2:  # grayscale
        return cv2.equalizeHist(img)
    else:  # color
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

def _match_cdf(source_channel, template_channel):
    """Histogram specification (match) for a single-channel 2D array.
       Uses unique-value CDF mapping (works for uint8)."""
    src = source_channel.ravel()
    tmpl = template_channel.ravel()

    # get unique pixel values and their forward indices & counts
    s_values, s_idx, s_counts = np.unique(src, return_inverse=True, return_counts=True)
    t_values, t_counts = np.unique(tmpl, return_counts=True)

    # compute cumulative distribution (normalized)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # map source quantiles to template values via interpolation
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    # build matched channel (use s_idx to map back to original shape)
    matched = interp_t_values[s_idx].reshape(source_channel.shape)

    # maintain dtype (clip & cast)
    if np.issubdtype(source_channel.dtype, np.integer):
        matched = np.clip(matched, 0, 255).astype(source_channel.dtype)
    return matched

def apply_histogram_specification(src_img, ref_img, match_luminance=True, debug=False):
    """
    Match histogram of src_img to ref_img.
    - If match_luminance=True : convert BGR -> YCrCb and match only Y channel (recommended).
    - Works for grayscale, BGR, and BGRA images. Preserves alpha if present.
    """

    if src_img is None or ref_img is None:
        raise ValueError("src_img and ref_img must be valid images (not None).")

    # copy so we don't mutate inputs
    src = src_img.copy()
    ref = ref_img.copy()

    # If images are loaded with IMREAD_UNCHANGED they may have alpha channel.
    src_alpha = None
    ref_alpha = None

    # Separate alpha if present
    if src.ndim == 3 and src.shape[2] == 4:
        src_alpha = src[:, :, 3].copy()
        src = src[:, :, :3]
        if debug: print("src has alpha; shape after split:", src.shape, "alpha shape:", src_alpha.shape)

    if ref.ndim == 3 and ref.shape[2] == 4:
        ref_alpha = ref[:, :, 3].copy()
        ref = ref[:, :, :3]
        if debug: print("ref has alpha; shape after split:", ref.shape, "alpha shape:", ref_alpha.shape)

    # If grayscale images (H,W) -> convert to (H,W,1) style for unify
    if src.ndim == 2:
        src = src[:, :, np.newaxis]
    if ref.ndim == 2:
        ref = ref[:, :, np.newaxis]

    # Ensure color images have 3 channels (BGR)
    if src.ndim == 3 and src.shape[2] == 3 and ref.ndim == 3 and ref.shape[2] == 3:
        pass
    elif src.shape[2] != ref.shape[2]:
        # fallback: if reference lacks color channels, convert it to 3-channel using cvtColor
        if ref.shape[2] == 1 and src.shape[2] == 3:
            ref = cv2.cvtColor(ref, cv2.COLOR_GRAY2BGR)
        elif ref.shape[2] == 3 and src.shape[2] == 1:
            src = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)
        else:
            # other mismatches: raise helpful error
            raise ValueError(f"Channel mismatch: src channels={src.shape[2]}, ref channels={ref.shape[2]}")

    # Now perform histogram matching
    if src.shape[2] == 1:
        # grayscale: single-channel match
        matched = _match_cdf(src[:, :, 0], ref[:, :, 0])
        result = matched[:, :, np.newaxis]
    else:
        # color: choose strategy
        if match_luminance:
            # convert both to YCrCb, match Y only
            src_ycc = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)
            ref_ycc = cv2.cvtColor(ref, cv2.COLOR_BGR2YCrCb)

            y_matched = _match_cdf(src_ycc[:, :, 0], ref_ycc[:, :, 0])

            # rebuild and convert back to BGR
            out_ycc = src_ycc.copy()
            out_ycc[:, :, 0] = y_matched
            result = cv2.cvtColor(out_ycc, cv2.COLOR_YCrCb2BGR)
        else:
            # match each channel independently (B, G, R)
            channels = []
            for c in range(3):
                ch_mat = _match_cdf(src[:, :, c], ref[:, :, c])
                channels.append(ch_mat)
            result = np.stack(channels, axis=2)

    # Re-attach alpha if it existed in source (we keep src's alpha)
    if src_alpha is not None:
        # ensure result is uint8 and has shape (H,W,3), then stack alpha
        if result.dtype != np.uint8:
            result = np.clip(result, 0, 255).astype(np.uint8)
        result = np.dstack((result, src_alpha))

    # final dtype guard
    if result.dtype != np.uint8:
        result = np.clip(result, 0, 255).astype(np.uint8)

    return result
