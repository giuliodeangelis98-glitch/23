# 23

A small collection of cool terminal toys. Stdlib-only Python (Pillow optional for image-to-ASCII).

## Tools

### `tools/ascii_art.py` — ASCII art generator
Render text as a banner or convert an image to ASCII.

```sh
python3 tools/ascii_art.py text "HOLA" --color cyan
python3 tools/ascii_art.py image photo.jpg --width 100   # requires Pillow
```

### `tools/git_timelapse.py` — Git commit time-lapse
Animates your repo's commit history as a colored heatmap, one day per frame.

```sh
python3 tools/git_timelapse.py            # animated
python3 tools/git_timelapse.py --no-animate  # static heatmap
```

### `tools/crypto_ticker.py` — Live crypto ticker
Polls Crypto.com's public REST API and renders prices with a rolling sparkline.

```sh
python3 tools/crypto_ticker.py BTC_USDT ETH_USDT SOL_USDT --interval 5
```

### `tools/excuse_generator.py` — Late-commit excuses
Plausible bilingual excuses. With `--blame git`, picks a real coauthor from your git log.

```sh
python3 tools/excuse_generator.py --lang es -n 3
python3 tools/excuse_generator.py --lang en --blame git
```
