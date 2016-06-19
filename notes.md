Markdown provides extensions which can be used to extend markdown syntax.
http://pythonhosted.org/Markdown/

Most useful is the meta-data extension which will allows writing header level meta attributes for a markdown post which 
can then be accessed within python.
http://pythonhosted.org/Markdown/extensions/meta_data.html

This, combined with a post-process step after the html conversion can be used for MathJax

Desired features:
 - Meta data for title, date, tags
 - MathJax support as in jupyter notebooks
 - Layout control and CSS through a defined template
 - Main index.html showing a list of all posts
 - Additional GitHub markdown like features such as checklists, emoji, syntax highlighting, URL linking.
 
 All of this should be able to serve locally
 
 # Roadmap
 
## Basic
[x] - Given an input markdown file, produce an html file.
[x] - Read and use title meta data attribute
[x] - Given an input directory, do this over all markdown files.
[x] - Do over a tree of directories
[x] - Also copy over any other files (images, etc.)

## Intermediate
[ ] - HTML template insertion
[ ] - MathJax support
[ ] - Checklists (create a Markdown extension)
[ ] - Syntax Highlighting
[ ] - URL linking

## Advanced
[ ] - Emoji
[ ] - Github pages integration
[ ] - URL linking
[ ] - Various Regex fixes for things like & -> %amp; correctly in html