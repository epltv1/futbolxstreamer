# Telegram M3U8 to RTMP Bot

A Telegram bot that generates FFmpeg commands to stream M3U8 links to RTMP servers, deployed on Vercel.

## Usage
- `/stream <m3u8_link> <rtmp_url> <stream_key>`: Get FFmpeg command for streaming.
  - Example: `/stream https://example.com/playlist.m3u8 rtmp://a.rtmp.youtube.com/live2 my-key`

## Deployment on Vercel
1. Fork this repo on GitHub.
2. Create a Vercel project, connect the repo.
3. Set environment variable: `BOT_TOKEN`.
4. Deploy and set Telegram webhook.
5. Test with `/start` and `/stream`.

## Notes
- Requires an external server with FFmpeg to run the streaming command.
- Uses webhooks for Telegram integration.
