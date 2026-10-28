"""Builds Elementor templates (JSON) from index.html / thanks.html.
Run from repo root: python3 wordpress/build_elementor.py"""
import base64, json, random, re

random.seed(7)
def eid(): return '%07x' % random.randrange(16**7)
def data_uri(path, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(open(path,'rb').read()).decode())

src = open('index.html', encoding='utf-8').read()
font_link = re.search(r'<link href="https://fonts\.googleapis\.com[^>]*>', src).group(0)
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
body = src[src.index('<body>')+6 : src.index('</body>')]

# images -> embedded, so nothing needs uploading
body = re.sub(r' data-label="[^"]*"', '', body)
for name in ['shai-hero.jpg', 'shai-portrait.jpg']:
    body = body.replace('src="images/%s"' % name, 'src="%s"' % data_uri('images/'+name, 'image/jpeg'))
css = css.replace('url(images/courtroom-bg.jpg)', 'url(%s)' % data_uri('images/courtroom-bg.jpg', 'image/jpeg'))
assert 'images/' not in body.split('<script>')[0] and 'images/' not in css

# keep the page's styles from fighting Elementor's own wrappers
css += '''
/* Elementor wrappers */
section.elementor-section{padding:0}
.elementor-widget-html .elementor-widget-container{padding:0;margin:0}
.lp-form .elementor-widget-wrap{align-content:flex-start}
.lp-form .lp-note{margin-top:12px;font-size:14px;color:#AEB9C8;text-align:center}
.lp-form .lp-note b{color:var(--gold)}
'''

body = body.replace('<main>', '').replace('</main>', '')
body = body.replace('href="privacy.html"', 'href="/privacy-policy/"').replace('href="accessibility.html"', 'href="/accessibility-statement/"')

top = body[: body.index('<!-- 10 FORM -->')]
form_sec = body[body.index('<!-- 10 FORM -->') : body.index('<footer>')]
bottom = body[body.index('<footer>'):]
text_col = re.search(r'(<div class="stack" style="gap:18px">.*?</div>\s*</div>)', form_sec, re.S).group(1)
bottom = bottom.replace('<script>\n(function(){', '<script>\nwindow.fbq = window.fbq || function(){};\n(function(){', 1)

def html_widget(html): return {"id": eid(), "elType": "widget", "widgetType": "html", "settings": {"html": html}, "elements": []}
def column(size, widgets): return {"id": eid(), "elType": "column", "settings": {"_column_size": size, "_inline_size": None}, "elements": widgets}
def section(cols, **settings): return {"id": eid(), "elType": "section", "settings": settings, "elements": cols, "isInner": False}

full = dict(layout="full_width", gap="no", padding={"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True})

page = {
  "version": "0.4", "title": "ליטיגטור – דף נחיתה", "type": "page",
  "page_settings": {"template": "elementor_canvas", "hide_title": "yes"},
  "content": [
    section([column(100, [html_widget(font_link + '\n<style>' + css + '</style>\n' + top)])], **full),
    section([
      column(55, [html_widget(text_col)]),
      column(45, [
        {"id": eid(), "elType": "widget", "widgetType": "shortcode",
         "settings": {"shortcode": "[להחליף בטופס של האתר – ראו קובץ ההוראות]"}, "elements": []},
        html_widget('<p class="lp-note"><b>הקורס הבא עומד להיפתח · מקומות מוגבלים</b><br>השארת הפרטים אינה מחייבת הרשמה או תשלום.</p>'),
      ]),
    ], layout="boxed", content_width={"unit": "px", "size": 1120, "sizes": []}, gap="wider",
       css_classes="dark court lp-form", _element_id="form",
       background_background="classic", background_color="#0E1A2B",
       padding={"unit": "px", "top": "96", "right": "20", "bottom": "96", "left": "20", "isLinked": False},
       padding_mobile={"unit": "px", "top": "64", "right": "16", "bottom": "64", "left": "16", "isLinked": False}),
    section([column(100, [html_widget(bottom)])], **full),
  ],
}
json.dump(page, open('wordpress/litigator-elementor.json', 'w', encoding='utf-8'), ensure_ascii=False)

t = open('thanks.html', encoding='utf-8').read()
t_head_links = '\n'.join(re.findall(r'<link [^>]*>', t))
t_css = re.search(r'<style>(.*?)</style>', t, re.S).group(1).replace('body{', '.lp-thanks{')
t_body = t[t.index('<body>')+6 : t.index('</body>')]
thanks_html = (t_head_links + '\n<style>' + t_css + '</style>\n<div class="lp-thanks">' + t_body + '</div>\n'
               "<script>if (window.fbq) fbq('track','Lead');</script>")
thanks = {"version": "0.4", "title": "ליטיגטור – דף תודה", "type": "page",
  "page_settings": {"template": "elementor_canvas", "hide_title": "yes"},
  "content": [section([column(100, [html_widget(thanks_html)])], **full)]}
json.dump(thanks, open('wordpress/litigator-thanks-elementor.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok')
