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
[x] - HTML template insertion
[x] - MathJax support
[x] - Checklists (create a Markdown extension) , almost working, doesn't display right, need to fix it
        https://github.com/facelessuser/pymdown-extensions/blob/master/pymdownx/tasklist.py
        use the above to get it right
        Actually just included some CSS, it works as long as you don't do two tasks lists sequentially
[x] - Syntax Highlighting
        Supported using the builtin CodeHilite extension and the Fenced Code Blocks extensions for github style markup
[ ] - Commandline arguments

## Advanced
[ ] - Github pages integration
[x] - URL linking
        Markdown is supposed to do this automatically
[x] - Various Regex fixes for things like & -> %amp; correctly in html
        Markdown is supposed to do this automatically
[1] - Use a local MathJax installation
[ ] - Automatic Webserve rebuild on detect changes
        Only update files if succeeded?
[x] - Automatically convert jupyter notebooks into markdown and copy, convert

## Roadmap
[ ] - Generate an index page listing all posts
[ ] - Tagging Support, show all posts matching tag
[ ] - Menu bar

## Optional
[ ] - Emoji

Commands:
--build
--serve
--publish
--run (build, publish on success), default command
    (if github not present, pull github, run output, on success commit w/ date timestamp, push)
        
What Poole does

Pass theme to init, pages.html is main template

Contains css, header in file, all content goes in __content__ key
go through markdown files using os.walk and create a Page class
run hook preconvert functions, dont appear to be any defined

read template file as default_template unless template is in page class instance, then set that to template,
pages were already sorted by the key `sval`

gets python statements to run
runs python states by performing repl_exec over all python statements and replacing the contents with it

feeds output of this to markdown.Markdown converter, stored in page.html attribute

run postconvert hooks, none defined

loop over pages, eval repls and replace, write html files
