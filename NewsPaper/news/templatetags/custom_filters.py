from django import template


register = template.Library()

BAD_WORDS = ['here',
             'Here',
             'article',
             'Article',
             'project',
             'Project'
             ]


@register.filter()
def censor(text: str):
    """Фильтр заменяет нежелательные слова звездочками"""
    for char_index in range(len(text)):
        for bad_word in BAD_WORDS:
            word_len = len(bad_word)
            if text[char_index: char_index+word_len] == bad_word:
                text = text[: char_index+1] + '*' * (word_len-1) + text[char_index+word_len:]
                char_index += word_len
                break

    return text
