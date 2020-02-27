# rtmpserver
RTMP server-side protocol implementation

### FFMPEG publish test command
`ffmpeg -r 30 -f lavfi -i testsrc -vf scale=1280:960 -vcodec libx264 -profile:v baseline -pix_fmt yuv420p -f flv "rtmp://localhost/live/somekey live=True token=1123" -loglevel debug`
