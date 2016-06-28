<!--%
from datetime import datetime

def date_sort(p):
    if p.date:
        return p.date
    else:
        return datetime.fromtimestamp(0)
        
sorted_pages = sorted(pages, key=date_sort, reverse=True)

for page in sorted_pages:
    if page.title != 'index':
        date_str = ''
        if page.date is not None:
            date_str = page.date.strftime('%B %d, %Y')
            print('* **[%s](%s)** - %s' % (page.title, page.url, date_str))
        else:
            print('* **[%s](%s)**' % (page.title, page.url))
%-->