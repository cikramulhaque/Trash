# Product Video Renderer

A GitHub Actions + FFmpeg pipeline for producing a verified 10-second vertical product video from genuine product-image URLs. Images are downloaded fresh for each run, validated, used only during rendering, and removed with all image derivatives after MP4 verification. The MP4 and text-only build report are retained as a workflow artifact.

## Run
Open **Actions → Render product video → Run workflow**. Enter the product title, optional subtitle, and 2–5 public HTTPS image URLs. No AI video generator is used.

## Output
The artifact `product-video-output` contains `product-video.mp4` and `build-report.txt` only. The runner removes source images, thumbnails, frame intermediates, and other image derivatives before artifact upload.

## Safety
Only use product images you are permitted to use. The downloader rejects non-HTTPS URLs, private/local network targets, non-image responses, oversized files, and invalid image data. The MP4 is checked with ffprobe before success is reported.