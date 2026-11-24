from io import BytesIO

import numpy as np
from PIL import Image

from .schemas import CaptureRequest



def render_png(request: CaptureRequest)->bytes:
    rng = np.random.default_rng(request.seed)
    y,x = np.indices((128,128))
    specimen = np.full((128,128), 4.0)
    true_focus = rng.uniform(-3, 3)

    sigma = np.hypot(1.2, 0.55 * (request.z_um - true_focus))

    for cx, cy in rng.uniform(10, 118, size=(24, 2)):
        distance_sq = (x-cx)**2 + (y-cy)**2
        specimen += 130*(1.2/sigma)**2*np.exp(
            -distance_sq/(2*sigma**2))
        
    noisy = rng.poisson(specimen*request.exposure_ms/25)
    pixels = np.clip(noisy, 0, 255).astype(np.uint8)
    buffer = BytesIO()
    Image.fromarray(pixels).save(buffer, format="PNG")
    return buffer.getvalue()