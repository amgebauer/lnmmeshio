import re, io
from .ioutils import read_next_key, read_next_option, read_next_value, write_comment, write_option, \
    write_option_list, write_title, line_comment, line_option, line_option_list
from collections import OrderedDict

EXCLUDE_SECTIONS = [
    re.compile(r'^FUNCT\d+$'),
    re.compile(r'^.* CONDITIONS$'),
    re.compile(r'^END$'),
    re.compile(r'^PROBLEM SIZE$'),
    re.compile(r'^DESIGN DESCRIPTION$'),
    re.compile(r'^NODE COORDS$'),
    re.compile(r'^[A-Z]+ ELEMENTS$'),
    re.compile(r'^[A-Z]+-NODE TOPOLOGY$'),
    re.compile(r'^RESULT DESCRIPTION$')
]

SINGLE_OPTION_SECTIONS = [
    re.compile(r'^PROBLEM TYP$'),
    re.compile(r'^IO$'),
    re.compile(r'^STRUCTURAL DYNAMIC$'),
    re.compile(r'^STRUCTURAL DYNAMIC/ONESTEPTHETA$'),
    re.compile(r'^SOLVER \d\s*$')
]

MULTIPLE_OPTION_SECTIONS = [
    re.compile(r'^MATERIALS$')
]

TEXT_SECTIONS = [
    re.compile(r'^TITLE$'),
    re.compile(r'^$')
]

class ContinueFor(Exception):
    pass

class BaseLine:

    def __init__(self, comment=None):
        self.comment = comment

    @staticmethod
    def parse_comment(line):
        l = line.split('//', 1)

        if len(l) == 1:
                return l[0], None
        return l[0].strip(), l[1].strip()
    
    def get_lines(self):
        raise NotImplementedError("This method is not implemented, but should be by the derived class")

class SingleOptionLine(BaseLine):

    def __init__(self, key, value, comment=None):
        super(SingleOptionLine, self).__init__(comment)
        self.key = key
        self.value = value
    
    def write(self, dest):
        comments_written = False
        if self.comment is not None and len(self.comment) > 50:
            # write comment in extra line
            write_comment(dest, self.comment, True)
            comments_written = True
        
        write_option(dest, self.key, self.value, None, newline=False)

        if not comments_written and self.comment is not None:
            dest.write(' ')
            write_comment(dest, self.comment, True)
        else:
            dest.write('\n')

    def get_lines(self):
        l = []
        comments_written = False
        if self.comment is not None and len(self.comment) > 50:
            # write comment in extra line
            l.append(line_comment(self.comment))
            comments_written = True
        
        l.append(line_option(self.key, self.value, None))

        if not comments_written and self.comment is not None:
            l[-1] += ' '
            l[-1] += line_comment(self.comment)
        
        return l

    @staticmethod
    def parse(line):
        l, comment = BaseLine.parse_comment(line)

        if l.strip() == '':
            return None

        l, key = read_next_key(l)
        l, value = read_next_value(l)

        if l.strip() != '':
            raise ValueError('This is not an single option line: {0}'.format(line))

        return SingleOptionLine(key, value, comment)

class MultipleOptionsLine(BaseLine):

    def __init__(self, options, comment=None):
        super(MultipleOptionsLine, self).__init__(comment)
        self.options = options
    
    def write(self, dest):
        comments_written = False
        if self.comment is not None and len(self.comment) > 50:
            # write comment in extra line
            write_comment(dest, self.comment, True)
            comments_written = True
        
        write_option_list(dest, self.options, False)

        if not comments_written and self.comment is not None:
            dest.write(' ')
            write_comment(dest, self.comment, True)
        else:
            dest.write('\n')

    def get_lines(self):
        l = []
        comments_written = False
        if self.comment is not None and len(self.comment) > 50:
            # write comment in extra line
            l.append(line_comment(self.comment))
            comments_written = True
        
        l.append(line_option_list(self.options))

        if not comments_written and self.comment is not None:
            l[-1] += ' '
            l[-1] += line_comment(self.comment)
        
        return l

    @staticmethod
    def parse(line):
        l, comment = BaseLine.parse_comment(line)

        if l.strip() == '':
            return None

        options = {}
        while l.strip() != '':
            l, key = read_next_key(l)
            l, value = read_next_value(l)

            if value is None:
                raise ValueError('Value of {0} is empty: {1}'.format(key, line))

            options[key] = value

        return MultipleOptionsLine(options, comment)

class CommentLine(BaseLine):
    def __init__(self, comment):
        super(CommentLine, self).__init__(comment)
        
    def get_lines(self):
        return line_comment(self.comment)

    @staticmethod
    def parse(line):
        l, comment = BaseLine.parse_comment(line)

        if l.strip() != '':
            raise ValueError('This line contains more than a comment: {0}'.format(line))
        return CommentLine(comment)

class Section:
    
    def __init__(self, name, comment = None):
        self.name = name
        self.comment = comment

    def __getitem__(self, key):
        raise NotImplementedError("Not implemented!")
    
    def write(self, dest):
        write_title(dest, self.name, True)
        if self.comment is not None:
            write_comment(dest, self.comment, True)
    
    def get_sections(self):
        d = OrderedDict()
        d[self.name] = []

        if self.comment != None:
            d[self.name] = '// {0}'.format(self.comment)
        
        return d

class TextSection(Section):

    def __init__(self, name, lines = None):
        super(TextSection, self).__init__(name)
        if lines is None:
            lines = []
        self.lines = [l.strip() for l in lines]

    def __len__(self):
        return len(self.lines)
    
    def __getitem__(self, i):
        return self.lines[i]

    def get_sections(self):
        d = super(TextSection, self).get_sections()
        for l in self.lines:
            d[self.name].append(l)
        return d

    def write(self, dest):
        super(TextSection, self).write(dest)
        for l in self.lines:
            dest.write('{0}\n'.format(l))

    @staticmethod
    def parse(name, lines):
        return TextSection(name, lines)

class SingleOptionSection(Section):

    def __init__(self, name, comment = None):
        super(SingleOptionSection, self).__init__(name, comment)
        self.lines = []
    
    def write(self, dest):
        super(SingleOptionSection, self).write(dest)
        for l in self.lines:
            l.write(dest)

    def get_sections(self):
        d = super(SingleOptionSection, self).get_sections()
        for l in self.lines:
            d[self.name].extend(l.get_lines())
        return d

    def __len__(self):
        return len(self.lines)
        
    def __getitem__(self, i):
        if type(i) == int:
            return self.lines[i]
        else:
            for l in [l for l in self.lines if type(l) == SingleOptionLine]:
                if l.key == i:
                    return l
        
        return None
    
    def append(self, line):
        self.lines.append(line)

    @staticmethod
    def parse(title, lines):
        section = SingleOptionSection(title)

        for line in lines:
            line_obj = SingleOptionLine.parse(line)
            if line_obj is None:
                # this line in empty or comment
                line_obj = CommentLine.parse(line)
                if line_obj is None:
                    # this is an empty line -> skip
                    continue
            section.append(line_obj)

        return section

class MultipleOptionsSection(Section):

    def __init__(self, name, comment = None):
        super(MultipleOptionsSection, self).__init__(name, comment)
        self.lines = []

    def __len__(self):
        return len(self.lines)
    
    def __getitem__(self, i):
        return self.lines[i]
    
    def append(self, line):
        self.lines.append(line)

    def get_sections(self):
        d = super(MultipleOptionsSection, self).get_sections()
        for l in self.lines:
            d[self.name].extend(l.get_lines())
        return d
    
    def write(self, dest):
        super(MultipleOptionsSection, self).write(dest)
        for l in self.lines:
            l.write(dest)

    @staticmethod
    def parse(name, lines):
        section = MultipleOptionsSection(name)

        for line in lines:
            line_obj = MultipleOptionsLine.parse(line)
            if line_obj is None:
                # this line in empty or comment
                line_obj = CommentLine.parse(line)
                if line_obj is None:
                    # this is an empty line -> skip
                    continue
            
            section.lines.append(line_obj)

        return section

class Head:

    def __init__(self):
        self.sections = {}

    def append(self, section):
        self.sections[section.name] = section

    def __len__(self):
        return len(self.sections)

    def __getitem__(self, key):
        if key not in self.sections:
            return None
        return self.sections[key]
    
    def get_sections(self):
        d = OrderedDict()

        for section in self.sections.values():
            d.update(section.get_sections())

        return d

    def write(self, dest):
        for section in self.sections.values():
            section.write(dest)

    @staticmethod
    def read(sections) -> 'Head':
        head = Head()

        for section, lines in sections.items():
            try:
                # check, whether to exclude
                for ex in EXCLUDE_SECTIONS:
                    if ex.match(section) is not None:
                        raise ContinueFor()
            except ContinueFor:
                continue
        
            # go over single option items
            try:
                for sec in SINGLE_OPTION_SECTIONS:
                    if sec.match(section) is not None:
                        section_obj = SingleOptionSection.parse(section, lines)
                        if section_obj is not None:
                            head.append(section_obj)
                        
                        raise ContinueFor()
            except ContinueFor:
                continue
        
            # go over multiple options items
            try:
                for sec in MULTIPLE_OPTION_SECTIONS:
                    if sec.match(section) is not None:
                        section_obj = MultipleOptionsSection.parse(section, lines)
                        if section_obj is not None:
                            head.append(section_obj)
                            
                            raise ContinueFor()
            except ContinueFor:
                continue
        
            # go over text option items
            try:
                for sec in TEXT_SECTIONS:
                    if sec.match(section) is not None:
                        section_obj = TextSection.parse(section, lines)
                        if section_obj is not None:
                            head.append(section_obj)
                            
                            raise ContinueFor()
            except ContinueFor:
                continue
            
            # this are remaining sections
            print('Unknown section, treat as Text section: {0}'.format(section))
            section_obj = TextSection.parse(section, lines)
            if section_obj is not None:
                head.append(section_obj)

        
        return head
