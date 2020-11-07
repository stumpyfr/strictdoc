class Section(object):
    def __init__(self, parent, level, title, free_texts, section_contents):
        self.parent = parent
        self.level = int(level)
        self.title = title

        self.free_texts = free_texts
        self.section_contents = section_contents

        self.ng_level = self.level
        self.ng_sections = []
        self.export_title = None

    def __str__(self):
        return "Section: <level: {}, title: {}, section_contents: {}>".format(
            self.level, self.title, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return True


class FreeText:
    def __init__(self, parent, text):
        self.parent = parent
        self.text = text
        self.ng_level = None

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return False

    def text_as_paragraphs(self):
        return self.text.split('\n\n')