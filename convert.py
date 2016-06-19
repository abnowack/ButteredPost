import markdown
from markdown.extensions.meta import MetaExtension
import os
from shutil import copyfile

class MarkdownConverter(markdown.Markdown):
    def __init__(self):
        extensions = [MetaExtension()]
        super(MarkdownConverter, self).__init__(extensions=extensions)

    def convert_markdown(self, input):
        """ Parse markdown into html string """

        with open(input, 'r') as markdown_file:
            markdown_str = markdown_file.read()
            html_str = self.convert(markdown_str)

        self.reset()

        return html_str

    def convert_html(self, html_body):
        """ Parse html by adding meta attributes if present """

        header_template = "<head><title>{title}</title></head>"
        title = self.Meta.get('title', [''])[0]
        header_str = header_template.format(title=title)
        html = header_str + '\n' + html_body
        return html

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
                else:
                    # copy over all other files (assets, images, etc.)
                    # Could add filter to exclude files if needed
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    copyfile(os.path.join(root, file), os.path.join(output_dir, file))

if __name__ == '__main__':
    # mock variables for now

    mdconv = MarkdownConverter()
    mdconv.parse()
    # print mdconv.Meta