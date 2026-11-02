# Video Downloader

תוכנה להורדת סרטונים מאתרים שונים באמצעות yt-dlp עם ממשק גרפי פשוט.

## תכונות

- ✅ הורדת סרטונים באיכויות שונות (1080p+, 720p, 480p)
- ✅ המרה ל-MP3 (אודיו בלבד)
- ✅ FFmpeg מובנה (לא צריך התקנה נפרדת)
- ✅ ממשק גרפי פשוט
- ✅ סרגל התקדמות בזמן אמת

## בניית EXE עם GitHub Actions

1. העלה את הקבצים ל-repo חדש ב-GitHub
2. לחץ על "Actions" בתפריט
3. בחר את ה-workflow "Build Windows EXE"
4. לחץ על "Run workflow"
5. לאחר הסיום, הורד את ה-EXE מה-artifacts

## שימוש בסקריפט פייתון

דורש Python ו-FFmpeg:

```bash
pip install yt-dlp
python video_downloader.py
```

## קבצים

- `video_downloader.py` - תוכנה עם ממשק גרפי (GUI)
- `video_downloader_cli.py` - תוכנה עם ממשק שורת פקודה (CLI)
- `.github/workflows/build.yml` - GitHub Action לבניית EXE
