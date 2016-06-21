import markdown
from markdown.extensions.meta import MetaExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
import os, sys, StringIO, contextlib
from shutil import copyfile
from bs4 import BeautifulSoup
from nbconvert import MarkdownExporter
import re

MARKDOWN_FILES = ['.md', '.mdown', '.markdown']
JUPYTER_FILES = ['.ipynb']

# http://stackoverflow.com/questions/3906232/python-get-the-print-output-in-an-exec-statement
@contextlib.contextmanager
def stdout_io(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


# https://github.com/mayoff/python-markdown-mathjax
class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node


class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')


# https://github.com/FND/markdown-checklist/blob/master/markdown_checklist/extension.py
class ChecklistExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('checklist', ChecklistPostprocessor(md),
                '>raw_html')


class ChecklistPostprocessor(markdown.postprocessors.Postprocessor):
    """
    adds checklist class to list element
    """

    pattern = re.compile(r'<li>\[([ Xx])\]')

    def run(self, html):
        html = re.sub(self.pattern, self._convert_checkbox, html)
        before = '<ul>\n<li><input type="checkbox"'
        after = before.replace('<ul>', '<ul class="task-list">')
        return html.replace(before, after)

    def _convert_checkbox(self, match):
        state = match.group(1)
        checked = ' checked' if state != ' ' else ''
        return '<li class="task-list-item"><input type="checkbox" disabled%s>' % checked


class Page(object):
    def __init__(self, filename, input_directory, output_directory):
        self.md_converter = markdown.Markdown(
            extensions=[MetaExtension(), MathJaxExtension(), CodeHiliteExtension(), FencedCodeExtension(),
                        ChecklistExtension()])
        self.jupyter_converter = MarkdownExporter()

        self.filename = filename
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.markdown = ''
        self.html = ''
        self.info = {}
        self.additional_files = {}

        name, extension = os.path.splitext(filename)
        self.html_filename = name + '.html'

        input_filename = os.path.join(input_directory, filename)
        if extension in MARKDOWN_FILES:
            self.read_markdown(input_filename)
        elif extension in JUPYTER_FILES:
            self.read_jupyter(input_filename)
        else:
            pass

    def read_markdown(self, markdown_filepath):
        with open(markdown_filepath, 'r') as markdown_file:
            self.markdown = markdown_file.read()
        self.convert_markdown_to_html()

    def read_jupyter(self, jupyter_filepath):
        (self.markdown, resources) = self.jupyter_converter.from_filename(jupyter_filepath)

        # copy over the other resources
        for key, value in resources['outputs'].iteritems():
            output_filepath = os.path.join(self.output_directory, key)
            self.additional_files[output_filepath] = value
        self.convert_markdown_to_html()

    def convert_markdown_to_html(self):
        self.html = self.md_converter.convert(self.markdown)
        if hasattr(self.md_converter, 'Meta'):
            for key, val in self.md_converter.Meta.iteritems():
                self.info[key] = val
        self.md_converter.reset()


def build(input_directory, template_filepath, output_root_directory='output'):
    with open(template_filepath, 'r') as template_file:
        template = template_file.read()

    pages = []

    # iterate over input tree, creating page objects storing converted html
    for input_root, input_dirs, input_files in os.walk(input_directory):
        # create output directory path
        split_path = input_root.split(os.path.sep)
        root_subdir = ''
        if len(split_path) > 1:
            root_subdir = os.path.join(*split_path[1:])
        output_directory = os.path.join(output_root_directory, root_subdir)

        # create output directory if not exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for input_file in input_files:
            input_filename = os.path.join(input_root, input_file)
            output_filename = os.path.join(output_directory, input_file)
            name, extension = os.path.splitext(input_file)
            if extension in MARKDOWN_FILES + JUPYTER_FILES:
                pages.append(Page(input_file, input_root, output_directory))
            else:
                # copy all other files over
                copyfile(input_filename, output_filename)

    # now that we have all body html elements, and we previously made the output directory tree
    # we iterate through pages, creating a full html page from the template file
    # then execute the python blocks within them, and finally write the file
    for page in pages:
        template_soup = BeautifulSoup(template, 'html.parser')
        page_soup = BeautifulSoup(page.html, 'html.parser')
        insert_page_tag = template_soup.body.find_all('div', {'id': 'post'})[0]

        for element in page_soup:
            insert_page_tag.append(element)

        # eval all <py></py> tags
        pytags = template_soup.find_all('py')
        for py in pytags:
            eval_str = str(eval(py.text))
            py.string = eval_str
            py.unwrap()

        # exec all <pyx></pyx> tags
        pyxtags = template_soup.find_all('pyx')
        for pyx in pyxtags:
            with stdout_io() as result:
                exec(pyx.text, {'pages': pages, 'page': page})
            pyx.string = result.getvalue()
            pyx.unwrap()

        # write rendered html
        with open(os.path.join(page.output_directory, page.html_filename), 'w') as output_html:
            output_html.write(template_soup.prettify())

        # write additional files created by page
        for file_name, file_data in page.additional_files.iteritems():
            output_filename = os.path.join(page.output_directory, file_name)
            with open(file_name, 'wb') as data_file:
                data_file.write(file_data)


if __name__ == '__main__':
    build('input', 'template.html', 'output')