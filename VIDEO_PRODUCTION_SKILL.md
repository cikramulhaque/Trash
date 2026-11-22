---
name: premium-product-video
description: Produce professional short-form product videos from genuine product photographs using the repository's FFmpeg renderer. Use for product ads, ecommerce reels, launch teasers and vertical product spotlights.
---

# Premium Product Video Production Skill

## Core objective
Create a polished, credible product advertisement using genuine product photography. The finished MP4 is the deliverable. Do not stop at a script, storyboard, source ZIP, or editor link when rendering is possible.

## Default visual direction
- Format: 1080x1920 vertical, 30 fps, 10 seconds unless the user specifies otherwise.
- Style: premium studio, cinematic dark gradient background, restrained accent color, subtle grid/particles, glass-like product stage, soft shadow and controlled highlights.
- Motion: slow camera push-in, clean scene changes, subtle fade transitions, kinetic typography reveals, animated progress/accent lines and deliberate pacing.
- Typography: one strong headline, one concise supporting line, consistent hierarchy, safe margins, high contrast and no overcrowding.
- Product: use genuine, current product photos. Preserve the product's shape, finish, logo and color. Never fabricate, redraw, or materially alter product details.
- Audio: do not add unlicensed music. Default to silent output unless the user provides a track or explicitly requests generated/original audio.
- Branding: use the user's brand assets only when supplied or approved. Do not invent brand logos.

## Production workflow
1. Identify product name, variant, key selling points, target platform and duration from the request and available context.
2. Gather 2–5 genuine product image URLs or use user-provided images. Prefer official manufacturer/retailer sources and use fresh URLs for each render.
3. Check the image URLs are accessible, HTTPS, public, and actual image files. Reject suspicious, private-network, oversized, or invalid content.
4. Plan a compact sequence: hook/product reveal, design/detail, feature/benefit, closing brand/product line. Match scene count to the available photos.
5. Render locally with `renderer/render.py` through FFmpeg. Use the premium dark studio treatment and restrained motion system.
6. Verify duration, dimensions, frame rate, codec and non-zero output. Inspect a frame/contact sheet when available; fix clipping, text overflow, weak contrast or poor product scale.
7. Remove all source images and image derivatives after rendering. Retain only the final MP4 and text build report.
8. Provide the actual verified MP4 file. Never invent a download link or claim a render succeeded before verification.

## Quality gate
- Product remains the visual hero and is large enough to identify on a phone.
- Text is readable at mobile size and remains within platform-safe margins.
- No clipped headlines, accidental glyphs, broken logos, image stretching or abrupt black frames.
- Background animation supports the product instead of competing with it.
- Transitions are smooth and timing feels intentional.
- MP4 passes ffprobe verification and build report records its SHA-256.
- Cleanup check confirms no downloaded source image files remain in the workspace.

## User preferences
The user prefers a complete, finished output and does not want to manually edit code or assemble assets. Automate the build and hand over the MP4 whenever possible. Be explicit about limitations and never substitute a code ZIP for a rendered video.
