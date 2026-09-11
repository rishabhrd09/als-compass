"""Render the silent 30-second illustrated guide from original project artwork.

Requires FFmpeg with libx264. Camera moves are pans/zooms over conceptual
illustrations; this is deliberately not described as microscopy or a simulation.
Run: venv/bin/python scripts/render_education_film.py
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'static' / 'images' / 'education'
OUTPUT = ROOT / 'static' / 'videos' / 'nerve-muscle-guide.mp4'


def main():
    # 16 s + 15 s with a 1 s dissolve = 30 s, at 24 fps. Render from a
    # larger working frame to keep the slow fractional pans smooth.
    filter_graph = (
        "[0:v]scale=3200:1800,setsar=1,"
        "zoompan=z='1.04+0.00025*on':x='iw*0.18-iw/zoom*0.18':y='ih/2-ih/zoom/2':"
        "d=384:s=1600x900:fps=24,format=yuv420p[first];"
        "[1:v]scale=3200:1800,setsar=1,"
        "zoompan=z='1.14-0.0002*on':x='iw/2-iw/zoom/2':y='ih*0.48-ih/zoom*0.48':"
        "d=360:s=1600x900:fps=24,format=yuv420p[second];"
        "[first][second]xfade=transition=fade:duration=1:offset=15,"
        "fade=t=in:st=0:d=0.7,fade=t=out:st=29.3:d=0.7[out]"
    )
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y',
        '-i', str(ASSETS / 'motor-neuron.webp'),
        '-i', str(ASSETS / 'neuromuscular-junction.webp'),
        '-filter_complex', filter_graph, '-map', '[out]',
        '-t', '30', '-an', '-c:v', 'libx264', '-crf', '20',
        '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        str(OUTPUT),
    ], check=True)
    print(f'Rendered {OUTPUT.name}: {OUTPUT.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
