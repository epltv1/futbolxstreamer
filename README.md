# Telegram M3U8 to RTMP Bot

A Telegram bot that prepares M3U8 streams with text and logo overlays for RTMP streaming, deployed on Vercel.

## Usage
- `/stream <m3u8_link> <rtmp_url> <stream_key>`: Generate overlays and get FFmpeg command.
  - Example: `/stream https://example.com/playlist.m3u8 rtmp://a.rtmp.youtube.com/live2 my-key`
- Overlays: Text from `OVERLAY_TEXT`, logo from `logo.png`.

## Deployment on Vercel
1. Fork this repo on GitHub.
2. Create a Vercel project, connect the repo.
3. Set environment variables: `BOT_TOKEN`, `OVERLAY_TEXT`.
4. Deploy and set Telegram webhook.
5. Test with `/start` and `/stream`.

## Notes
- Requires an external RTMP server (e.g., YouTube Live) with FFmpeg for streaming.
- Uses Pillow for overlays since Vercel doesn’t support FFmpeg.
- Ensure `logo.png` is in the repo.
