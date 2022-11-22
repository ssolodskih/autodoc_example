import base64
import json
import sys

if sys.platform.startswith('linux'):
    from cairosvg import svg2png

from abstracts import Visualizer


class AMRDirectVisualizer(Visualizer):
    def __init__(self, height=1054, width=551):
        self._amrs = {}
        self._css_dict = {}
        self._css_header = '<style type="text/css" >\n<![CDATA[\n'
        self._css_footer = ']]>\n</style>\n'
        self._css_style = ''
        self.height = height
        self.width = width
        self._svg_header = f'<svg width="{self.height}" height="{self.width}" viewBox="0 0 {self.height} {self.width}" fill="none" xmlns="http://www.w3.org/2000/svg">\n'
        self._svg_filename = ''
        self._png_filename = ''
        self.png = bytes()
        self.svg = ''

    def __str__(self):
        return str(self._css_style)

    _colors = {
        2: "#C31F1E;",
        1: "#3E9C68;",
        0: "#5F5F5F;"
    }

    def _generate_css(self) -> str:
        try:
            for k, v in self._amrs.items():
                self._css_dict["#" + k] = {
                    "fill:": self._colors[v],
                    "white-space:": "pre;"
                }

            css_body = json.dumps(self._css_dict, indent=5, separators=('', ' '))
            css_body = css_body.replace('"', '').rstrip('}').lstrip('{')
            self._css_style = self._css_header + \
                              css_body + \
                              self._css_footer
            return self._css_style
        except AttributeError:
            raise Exception("Incorrect input data supplied")

    def visualize(self, data: dict) -> bool:
        self._amrs = data
        self._css_style = self._generate_css()

        with open('./methods/AMRDirect/templates/resist_template.svg') as infile:
            svg_full = infile.readlines()

        svg_full.insert(0, self._svg_header)
        svg_full.insert(1, self._css_style)
        self.svg = '\n'.join(svg_full)
        return True
    
    def render_png(self) -> bool:
        try:
            self.png = svg2png(bytestring=self.svg)
            return True
        except Exception as e:
            return False

    def save_png(self, filename: str = 'output.png') -> bool:
        try:
            svg2png(bytestring=self.svg, write_to=filename)
            return True
        except Exception as e:
            return False
    
    def save_svg(self, filename: str = 'output.svg') -> bool:    
        with open(filename, 'w') as outfile:
            outfile.write(self.svg)
        return True

    def generate_base64(self) -> bytes:
        render_type = self.format_selector()
        if render_type == 'png':
            self.render_png()
            encoded_string = base64.urlsafe_b64encode(self.png).decode('utf-8')
        else:
            encoded_string = self.svg
        return encoded_string

    def format_selector(self):
        return 'png'
