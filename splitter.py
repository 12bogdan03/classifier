import re


class TextSplitter:

    def split_on_sentence(self, text) -> list:

        t = self.__abbr(text)
        t9 = self.__quest(t)
        split = self.__split_on_3_dots(t9)

        result_sent=list()

        for sent in split:
            result_sent.extend(self.__simple_split_on_sentence(sent))
        result_sent = [i.replace('$', '.') for i in result_sent]
        result_sent = [i.replace('#', '...') for i in result_sent]
        result_sent = [i.replace('&', '?') for i in result_sent]
        result_sent = [i.replace('@', '!') for i in result_sent]
        result_sent = [i.replace('%', '-') for i in result_sent]
        # for i in result_sent:
        #    print(i)
        return result_sent

    def split_on_words(self, text: str) -> list:
        result_sent = self.split_on_sentence(text)
        result=list()
        for i in result_sent:
            i = self.__abbr(i)
            result.extend(self.__split_on_words(i))
            result = [i.replace('$', '.') for i in result]
            result = [i.replace('%', '-') for i in result]
        return result

    def __split_on_words(self, text) -> list:
        text = u''.join([ch for ch in text if ch not in u'-—,()/?!.«;:»"'])
        text = text.split(' ')
        words = [word.strip('.') for word in text]
        return words

    def __abbr(self, text):
        p1 = re.compile('\([а-яюєїі]+\. [A-ZA-ЯЇЮЄІ][^\)]+\)')
        m1 = re.findall(p1, text)
        for m in m1:
            text = text.replace(m, m.replace('.', '$'))

        p4 = re.compile('[\"\«][А-ЯЮЄЇІа-яюєїіA-Za-z ]+\. [А-ЯЮЄЇІа-яюєїіA-Za-z 0-9]+[\"\»]')
        m4 = re.findall(p4, text)
        for m in m4:
            text = text.replace(m, m.replace('.', '$'))

        p5 = re.compile('[а-яюєїіА-ЯЮЄЇІ]+\. [а-яюєїі]+[\.]*')
        m5 = re.findall(p5, text)
        for m in m5:
            text = text.replace(m, m.replace('.', '$'))

        p7 = re.compile(' [а-яюєїіА-ЯЮЄЇІ]\. [А-ЯЮЄЇІ][а-яюєїі]*')
        m7 = re.findall(p7, text)
        for m in m7:
            text = text.replace(m, m.replace('.', '$'))

        p10 = re.compile('[А-ЯЮЄЇІа-яюєїі]+-[[А-ЯЮЄЇІа-яюєїі]+')
        m10 = re.findall(p10, text)
        for m in m10:
            text = text.replace(m, m.replace('-', '%'))
        p14 = re.compile('\«[А-ЯЮІЄЇа-яюєії ,-?!]+\»')
        m14 = re.findall(p14, text)
        for m in m14:
            text = text.replace(m, m.replace('.', '$'))
        return text

    def __quest(self, text: str) -> str:
        p910 = re.compile('[\(\"\«][А-ЯЮЄЇІа-яюєїіґ ]+\![\)\"\»]')
        m910 = re.findall(p910, text)
        for m in m910:
            text = text.replace(m, m.replace('!', '@'))

        p12 = re.compile('\- [А-ЯЮЄЇа-яюєїі\, ]+\? \-')
        m12 = re.findall(p12, text)
        for m in m12:
            text = text.replace(m, m.replace('?', '&'))

        p13 = re.compile('\"[А-ЯЮЄЇа-яюєїі ]+\?\.\.\"')
        m13 = re.findall(p13, text)
        for m in m13:
            text = text.replace(m, m.replace('?..', '&'))
        return text

    def __split_on_3_dots(self, text:str)->list:
        text=text.replace('...','#')
        lines=text.split('#')
        lines = [sent.strip(' ') for sent in lines]
        lines =[sent + '#' for i,sent in enumerate(lines)]
        lines[-1] = lines[-1][:-1]
        return lines

    def __simple_split_on_sentence(self, text:str)->list:
        lines = text.split('.')
        lines = [sent.strip(' ') for sent in lines]
        lines =[sent + '.' for i, sent in enumerate(lines)]
        lines[-1] = lines[-1][:-1]
        return lines
