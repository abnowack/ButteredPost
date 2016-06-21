<ul>
<pyx>
html = r"<li>boop <strong><a href=\"{url}\">{title}</a></strong></li>"
for page in pages:
    print html.format(url="blank", title=page.filename)
</pyx>
</ul>