import markdown
from markdown.extensions.meta import MetaExtension
import os, sys, StringIO, contextlib
from shutil import copyfile
from bs4 import BeautifulSoup

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

class MarkdownConverter(markdown.Markdown):
    def __init__(self, template='template.html'):
        extensions = [MetaExtension(), MathJaxExtension()]
        super(MarkdownConverter, self).__init__(extensions=extensions)

        with open(template, 'r') as template_file:
            self.template = template_file.read()

    def convert_markdown(self, input):
        """ Parse markdown into html string """

        with open(input, 'r') as markdown_file:
            markdown_str = markdown_file.read()
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

        for element in body_soup:
            page_soup.body.append(element)

        # evaluate all python tags
        pytags = page_soup.find_all('py')
        for py in pytags:
            print py.text
            with stdout_io() as result:
                exec py.text
            eval_str = result.getvalue()
            py.string = eval_str
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

    def parse(self, input_root_directory='input', output_root_directory='output'):
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
                else:
                    # copy over all other files (assets, images, etc.)
                    # Could add filter to exclude files if needed

                    # check if directory exists first
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    copyfile(os.path.join(root, file), os.path.join(output_dir, file))

        return output_files

if __name__ == '__main__':
    # mock variables for now

    mdconv = MarkdownConverter()
    mdconv.parse()
    # print mdconv.Meta