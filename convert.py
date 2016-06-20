import markdown
from markdown.extensions.meta import MetaExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
import os, sys, StringIO, contextlib
from shutil import copyfile
from bs4 import BeautifulSoup
from nbconvert import MarkdownExporter
import re

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


class MarkdownConverter(markdown.Markdown):
    def __init__(self, template='template.html'):
        extensions = [MetaExtension(), MathJaxExtension(), CodeHiliteExtension(), FencedCodeExtension(),
                      ChecklistExtension()]
        super(MarkdownConverter, self).__init__(extensions=extensions)

        with open(template, 'r') as template_file:
            self.template = template_file.read()

        self.nb_md_converter = MarkdownExporter()

    def convert_markdown(self, input, is_file=True):
        """ Parse markdown into html string """

        if is_file:
            with open(input, 'r') as markdown_file:
                markdown_str = markdown_file.read()
        else:
            markdown_str = input

        html_str = self.convert(markdown_str)
        self.reset()

        return html_str

    def convert_html(self, html_body):
        """ Parse html by adding meta attributes if present """

        # change to use template, parse html using HTMLParser
        # header_template = "<head><title>{title}</title></head>"
        # title = self.Meta.get('title', [''])[0]
        # header_str = header_template.format(title=title)
        # html = header_str + '\n' + html_body

        page_soup = BeautifulSoup(self.template, 'html.parser')
        body_soup = BeautifulSoup(html_body, 'html.parser')
        insert_page_tag = page_soup.body.find_all('div', {'id': 'post'})[0]

        for element in body_soup:
            insert_page_tag.append(element)

        # exec all python pyx tags
        pytags = page_soup.find_all('pyx')
        for py in pytags:
            with stdout_io() as result:
                exec py.text
            eval_str = result.getvalue()
            py.string = eval_str
            print py.text, eval_str
            py.unwrap()

        # eval all python py tags
        pytags = page_soup.find_all('py')
        for py in pytags:
            eval_str = str(eval(py.text))
            py.string = eval_str
            print py.text, eval_str
            py.unwrap()

        return page_soup.prettify()

    def parse_file(self, input, output=None):
        """ Full input to output process for single file """

        if output is None:
            input_name, _ = os.path.splitext(input)
            output = input_name

        html_raw = self.convert_markdown(input)
        html = self.convert_html(html_raw)

        with open(output, 'w') as html_file:
            html_file.write(html)

    def parse_to_html(self, input_root_directory='input', output_root_directory='output'):
        output_files = []
        for root, dirs, files in os.walk(input_root_directory):
            split_path = root.split(os.path.sep)
            root_subdir = ''
            if len(split_path) > 1:
                root_subdir = os.path.join(*split_path[1:])

            output_dir = os.path.join(output_root_directory, root_subdir)

            for file in files:
                name, extension = os.path.splitext(file)
                if extension in ['.md', '.mdown', '.markdown']:
                    input_path = os.path.join(root, file)

                    # check if directory exists first
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    output_path = os.path.join(output_dir, name + '.html')
                    self.parse_file(input_path, output_path)

                    output_files.append(output_path)
                elif extension in ['.ipynb']:
                    # Convert jupyter notebook to markdown and convert, copying the images as well
                    (md_body, resources) = self.nb_md_converter.from_filename(os.path.join(root, file))
                    html_body = self.convert_markdown(md_body, is_file=False)
                    html = self.convert_html(html_body)

                    # check if directory exists first
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    output_path = os.path.join(output_dir, name + '.html')
                    with open(output_path, 'w') as html_file:
                        html_file.write(html)

                    output_files.append(output_path)

                    # copy over the other resources
                    for res in resources['outputs']:
                        print res, type(res), type(resources['outputs'][res])
                        with open(os.path.join(output_dir, res), 'wb') as notebook_resource:
                            notebook_resource.write(resources['outputs'][res])

                else:
                    # copy over all other files (assets, images, etc.)
                    # Could add filter to exclude files if needed

                    # check if directory exists first
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    copyfile(os.path.join(root, file), os.path.join(output_dir, file))

        return output_files

    def render_html(self, files):
        pass

def build():
    mdconv = MarkdownConverter()
    pages = mdconv.parse()



if __name__ == '__main__':
    # mock variables for now

    mdconv = MarkdownConverter()
    mdconv.parse()
    # print mdconv.Meta