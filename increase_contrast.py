import os
import re
from flashtext import KeywordProcessor
from pydantic import BaseModel, confloat

color_float = confloat(ge=0, le=255)

THRESH = 150
INC_CONTRAST = 45

class Color(BaseModel):
    red: color_float
    green: color_float
    blue: color_float
    alpha: color_float

    @property
    def list(self):
        return [self.red, self.green, self.blue, self.alpha]
    
    @property
    def intlist(self):
        return [int(v) for v in self.list]

    @staticmethod
    def _increase_contrast(val: float, inc: float):
        direction = val > THRESH
        if direction:
            sym = 1
        else:
            sym = -1
        val = val + inc * sym
        val = max(val, 0)
        val = min(val, 255)
        return val

    def increase_contrast(self, inc: float):
        new_inst = self.copy()
        for attr in ["red", "green", "blue"]:
            val = getattr(new_inst, attr)
            new_val = self._increase_contrast(val, inc)
            setattr(new_inst, attr, new_val)
        return new_inst

    @classmethod
    def parse(cls, string: str):
        carr = []

        if string.startswith("rgba"):
            colors = string.strip().strip("rgba").strip("(").strip(")").strip()
            colors = colors.split(",")
            if len(colors) != 4:
                print(
                    f"invalid rgba color ({string}) encountered due to invalid argument count {len(colors)} in parsed arguments {colors}"
                )
                return
            else:
                for i, c in enumerate(colors):
                    try:
                        c = c.strip()
                        cfloat = float(c)
                        carr.append(cfloat)
                    except:
                        print(
                            f"unable to parse rgba argument '{c}' as float at position {i} in rgba color '{string}'"
                        )
                        break
        elif string.startswith("#"):
            colors = string.strip("#")
            l_colors, u_colors = colors.upper(), colors.lower()

            if not any([cs == colors for cs in [l_colors, u_colors]]):
                print(
                    f"skipping invalid hex color code ({colors}) because not all chars are either upper or lower case"
                )
                return

            if len(colors) == 6:
                colors += "00"

            if len(colors) != 8:
                print(
                    f"skipping invalid hex color code ({colors}) because of invalid length: {len(colors)}"
                )
                return
            else:
                for i in range(4):
                    c = colors[i * 2 : (i + 1) * 2]
                    try:
                        cbyte = bytes.fromhex(c)
                        cint = list(cbyte)[0]
                        carr.append(cint)
                    except:
                        print(
                            f"cannot parse '{c}' as hex at position {i} of color code '{colors}'"
                        )
                        break
        else:
            print(f"unrecognized color format of '{string}'")
            return
        if len(carr) == 4:
            ret = cls(**{k:carr[i] for i,k in enumerate(['red', 'green', 'blue', 'alpha'])})
            return ret


class ColorParser:
    __slots__ = ["regex", "serialize"]

    def __init__(self, content: str):
        self.content = content

    def find(self):
        yield from re.findall(self.regex, self.content)

    def parse(self):
        for color in self.find():
            result = Color.parse(color)
            if isinstance(result, Color):
                yield color, result

    def increase_contrast(self, inc: float):
        for color, result in self.parse():
            inc_result = result.increase_contrast(inc)
            inc_color = self.__class__.serialize(inc_result)
            kwpair = (color, inc_color)
            yield kwpair


class RGBHexColorParser(ColorParser):
    regex = r"(#[0-9A-Za-z]{6})[^0-9^A-Z^a-z]"
    serialize = lambda color: f"#{bytes(color.intlist[:3]).hex()}"


class RGBAHexColorParser(ColorParser):
    regex = r"(#[0-9A-Za-z]{8})[^0-9^A-Z^a-z]"
    serialize = lambda color: f"#{bytes(color.intlist).hex()}"


class RGBAFuncColorParser(ColorParser):
    regex = r"rgba\([^\)]+\)"
    serialize = lambda color: f"rgba({','.join(str(v) for v in color.list)})"


class ColorTransformer:
    parsers = [RGBAFuncColorParser, RGBAHexColorParser, RGBHexColorParser]

    def __init__(self, content):
        self.content = content
        self.processor = KeywordProcessor()
        self.processor.add_non_word_boundary("#")

    def increase_contrast(self, inc: float):
        for parser in self.parsers:
            parser_inst = parser(self.content)
            for color, inc_color in parser_inst.increase_contrast(inc):
                print(f"{color} -> {inc_color}")
                self.processor.add_keyword(color, clean_name=inc_color)

        new_content = self.processor.replace_keywords(self.content)
        return new_content


new_dir = "new"
os.system(f"rm -rf {new_dir}")


def get_new_relpath(relpath: str):
    sep = "/"
    elems = relpath.split(sep)
    elems[0] = new_dir
    new_relpath = sep.join(elems)
    return new_relpath


for dirpath, dirpaths, fpaths in os.walk("old"):
    for f in fpaths:
        if f.endswith(".css"):
            relpath = os.path.join(dirpath, f)
            print("READING CSS:", relpath)
            with open(relpath, "r") as obj:
                cnt = obj.read()
                tf = ColorTransformer(cnt)
                new_cnt = tf.increase_contrast(INC_CONTRAST)
                new_relpath = get_new_relpath(relpath)
                print("WRITE TO:", new_relpath)
                new_dirpath = os.path.dirname(new_relpath)
                os.system(f"mkdir -p {new_dirpath}")
                with open(new_relpath, "w+") as new_obj:
                    new_obj.write(new_cnt)
                del tf
