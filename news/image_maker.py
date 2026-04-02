"""
News Image Template - Canva Match
"""

import os
import base64
import logging
from datetime import datetime, timezone, timedelta
from html2image import Html2Image
from PIL import Image

logger = logging.getLogger("ImageMaker")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "news")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")
BDT = timezone(timedelta(hours=6))


def crop_watermark(image_path):
    if not image_path or not os.path.exists(image_path):
        return image_path
    try:
        img = Image.open(image_path)
        w, h = img.size
        img = img.crop((0, 0, w, int(h * 0.82)))
        cropped_path = image_path.rsplit(".", 1)[0] + "_cropped.jpg"
        img.save(cropped_path, "JPEG", quality=95)
        return cropped_path
    except Exception as e:
        logger.error(f"[!] Crop failed: {e}")
        return image_path


def image_to_base64(image_path):
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
    return f"data:image/{mime};base64,{data}"


def build_html(title, news_image_path=None, summary=""):
    if news_image_path:
        news_image_path = crop_watermark(news_image_path)

    img_src = image_to_base64(news_image_path)

    if img_src:
        img_tag = f'<img src="{img_src}" class="news-img" />'
    else:
        img_tag = '<div class="news-img placeholder"></div>'

    # Summary: enough text to fill 2 lines
    summary_line = ""
    if summary and len(summary) > 10:
        summary_line = summary[:130]
        if len(summary) > 130:
            last_space = summary_line.rfind(" ")
            if last_space > 60:
                summary_line = summary_line[:last_space]
            summary_line += "..."

    summary_html = f'<div class="content-text">{summary_line}</div>' if summary_line else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Anek+Bangla:wght@400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700;800;900&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    width: 1080px;
    height: 1080px;
    overflow: hidden;
    margin: 0;
    font-family: 'Anek Bangla', 'Noto Sans Bengali', sans-serif;
  }}

  .container {{
    width: 1080px;
    height: 1080px;
    display: flex;
    flex-direction: column;
  }}

  /* ========== TOP: IMAGE (50%) ========== */
  .image-section {{
    width: 100%;
    height: 500px;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
  }}

  .news-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
  }}

  .news-img.placeholder {{
    background: #333;
    width: 100%;
    height: 100%;
  }}

  /* ========== BRANDING (overlapping center) ========== */
  .brand-wrapper {{
    width: 100%;
    display: flex;
    justify-content: center;
    flex-shrink: 0;
    margin-top: -24px;
    margin-bottom: -24px;
    position: relative;
    z-index: 15;
  }}

  .brand-badge {{
    background: #CC0000;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 20px 8px 10px;
  }}

  .fb-circle {{
    width: 36px;
    height: 36px;
    background: #1877F2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
    font-size: 22px;
    font-weight: 900;
    color: #fff;
  }}

  .page-name {{
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    white-space: nowrap;
    font-family: 'Segoe UI', Arial, sans-serif;
  }}

  /* ========== RED LINE ========== */
  .red-line {{
    width: 100%;
    height: 5px;
    background: #CC0000;
    flex-shrink: 0;
    margin-top: -1px;
  }}

  /* ========== TEXT SECTION (bottom ~45%) ========== */
  .text-section {{
    flex: 1;
    background: #111;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 25px 80px;
    text-align: center;
  }}

  .title {{
    font-size: 50px;
    font-weight: 800;
    font-style: italic;
    color: #ffffff;
    line-height: 1.35;
    margin-bottom: 16px;
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  .content-text {{
    font-size: 28px;
    font-weight: 400;
    color: rgba(255,255,255,0.7);
    line-height: 1.45;
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  /* ========== BOTTOM RED BAR ========== */
  .bottom-bar {{
    width: 100%;
    height: 68px;
    background: #CC0000;
    display: flex;
    align-items: center;
    padding: 0 26px;
    gap: 10px;
    flex-shrink: 0;
  }}

  .action-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,0,0,0.25);
    border-radius: 8px;
    padding: 8px 16px;
  }}

  .icon-box {{
    background: #fff;
    border-radius: 5px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
  }}

  .action-label {{
    color: #fff;
    font-size: 19px;
    font-weight: 700;
    font-family: 'Segoe UI', Arial, sans-serif;
  }}

  .readmore-btn {{
    background: #fff;
    color: #CC0000;
    font-size: 19px;
    font-weight: 800;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 8px 22px;
    border-radius: 8px;
    margin-left: auto;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="image-section">
    {img_tag}
  </div>

  <div class="brand-wrapper">
    <div class="brand-badge">
      <div class="fb-circle">f</div>
      <div class="page-name">@দেশের খবর - Desher Khobor</div>
    </div>
  </div>

  <div class="red-line"></div>

  <div class="text-section">
    <div class="title">{title}</div>
    {summary_html}
  </div>

  <div class="bottom-bar">
    <div class="action-pill">
      <div class="icon-box">👍</div>
      <span class="action-label">LIKE</span>
    </div>
    <div class="action-pill">
      <div class="icon-box">💬</div>
      <span class="action-label">COMMENT</span>
    </div>
    <div class="action-pill">
      <div class="icon-box">↗</div>
      <span class="action-label">SHARE</span>
    </div>
    <div class="readmore-btn">READ MORE</div>
  </div>
</div>
</body>
</html>"""
    return html


def create_news_image(title, news_image_path=None, highlight_text="", article_id="", summary=""):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    now = datetime.now(BDT)
    filename = f"news_{article_id}_{now.strftime('%Y%m%d_%H%M%S')}.png"

    html = build_html(title, news_image_path, summary)

    try:
        hti = Html2Image(
            output_path=OUTPUT_DIR,
            size=(1080, 1200),
            custom_flags=[
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--window-size=1080,1200",
            ],
        )
        paths = hti.screenshot(html_str=html, save_as=filename)
        raw_path = paths[0] if paths else os.path.join(OUTPUT_DIR, filename)

        # Crop to exact 1080x1080
        from PIL import Image as PILImage
        img = PILImage.open(raw_path)
        if img.size != (1080, 1080):
            img = img.crop((0, 0, 1080, 1080))
            img.save(raw_path)

        output_path = raw_path
        logger.info(f"[+] Image created: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"[!] Image creation failed: {e}")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    test_path = create_news_image(
        title="মাদকবিরোধী অভিযান পরিচালনা করবেন আমানউল্লাহ আমান",
        summary="চট্টগ্রামে মাদক ও চাঁদাবাজির বিরুদ্ধে জিরো টলারেন্স নীতিতে কাজ করবেন নবনিযুক্ত সিএমপি কমিশনার।",
        article_id="test",
    )
    print(f"Created: {test_path}")
