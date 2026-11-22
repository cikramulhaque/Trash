# Premium Product Video Renderer

A GitHub Actions + FFmpeg pipeline for polished 10-second vertical product spots made from genuine product photographs.

## Visual system
- 1080x1920, 30 fps, H.264 MP4
- Dark premium studio gradient, subtle grid and particles
- Glass-like product stage, soft glow and shadow
- Slow cinematic camera push-in and fade transitions
- Clear headline/subtitle hierarchy and animated progress accent
- No unlicensed music; output is silent by default

## Run
Open **Actions → Render product video → Run workflow**. Enter a product title, closing line and 2–5 public HTTPS image URLs.

## Output
The `product-video-output` artifact contains only `product-video.mp4` and `build-report.txt`. Temporary downloads and image derivatives are deleted before upload.

## Skill guide
See [VIDEO_PRODUCTION_SKILL.md](VIDEO_PRODUCTION_SKILL.md) for the creative brief, production workflow and quality gate.

## Safety and verification
Only use images you are permitted to use. The downloader rejects non-HTTPS URLs, private/local network targets, non-image responses, oversized files and invalid image data. The MP4 is verified with ffprobe before success is reported.
