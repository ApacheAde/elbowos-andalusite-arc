# Andalusite Arc

Full-colour Python 3 neon **magnetic-volley** arcade for ElbowOS.

A copper-and-teal andalusite core sits mid-court and bends every shard.
Keep the ball off your end with A/D. The rift paddle at the top plays back.

Featured: **https://x.com/ElbowOS**

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 andalusite_arc.py --play
```

Controls: `A` / `D` or arrows move · `R` reset · `ESC` quit

## Record a 9:16 reel

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 andalusite_arc.py --record
```

Writes `/home/workdir/artifacts/ANDALUSITE_ARC_ElbowOS.mp4` (1080×1920, 15s, 30fps, H.264).

## Links

- Reel on Drive: https://drive.google.com/file/d/1LGTSOiYwrFpmInhtFpR32tUKG8R75ri7/view
- ElbowOS: https://x.com/ElbowOS
- This repo: https://github.com/ApacheAde/elbowos-andalusite-arc

Needs Python 3.10+ and pygame.
