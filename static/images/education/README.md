# ALS educational artwork

`motor-neuron.webp` and `neuromuscular-junction.webp` are original conceptual
illustrations generated with OpenAI ImageGen for this visual refactor on
2026-09-11. Original images were 1672 × 941. WebP conversion changes encoding only.

They are not microscopy photographs, scans, or medically validated anatomical
models. They illustrate a multipolar neuron and the nerve–muscle connection.
Shape, scale, myelin detail, and signal lights are simplified visual devices.

The silent film uses slow pans/zooms and a cross-dissolve over these two
illustrations. Its captions and adjacent transcript explain the concepts.
It is not a rendered simulation of ALS progression. Rebuild with
`venv/bin/python scripts/render_education_film.py` (FFmpeg + libx264 required).

The interactive model is separately authored in `static/js/education/` with
Three.js and GSAP camera moves. It illustrates loss of nerve supply rather
than presenting demyelination as the primary mechanism of ALS.
