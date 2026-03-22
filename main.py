def fetch_video_info(video_id):
    options = {
        'geo_bypass': True,
        'no_check_certificate': True,
        'http_finalize': True,
    }
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.params['http_headers'] = headers
        ydl.params['player_skip'] = True
        ydl.params['retries'] = 10
        ydl.params['backoff_factor'] = 5
        ydl.params['socket_timeout'] = 10
        info = ydl.extract_info(video_id, download=False)
        return info
