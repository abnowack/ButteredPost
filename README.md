# ButteredPost

:bread:

ButteredPost is a small and simple static site generator written in Python. It will input a template.html file, a directory containing markdown files, media files, or jupyter notebooks and create an output folder of the rendered html.

It allows writing Python within either the markdown or template.html so simple site navigation can be created through the ButteredPost library.

This is done in two ways:

`{{ statement }}` will evaluate `statement` using python eval. Useful if you want to display the title of the current page via `{{ page.title }}`

```
  <!--%
  statement1
  print foo(statement1)
  %-->
```
This method will use python exec to interpret multiple lines. The html to display is done by printing it within the block.

Changes to the site layout are done by creating or modifying the template.html file. Just create a `<div id="post"></div>` within the html body and the post will be appended right before the `</div>` tag.

After that it's mostly up to you, changes should all be possible from the template.html file and the python code within your markdown scripts. The goal is to keep it a single file, and as minimal as possible. Contributions welcome! :bread:
