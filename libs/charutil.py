import unicodedata


def get_visible_len(string):
    """
    表示上での長さを返す。つまり
    全角文字の数×2 + 半角文字の数×1 を返す。
    :param string: 計算に用いる文字列。
    """

    length = 0
    for char in string:
        if unicodedata.east_asian_width(char) in "FWA":
            length += 2
        else:
            length += 1
    return length


def get_wrapped(width, string):

    # リスト内包で行けるかと思ったら全角文字に対応できませんでした :/
    text = []
    for char in string:
        if len(text) == 0 or get_visible_len(text[-1:][0] + char) > width:
            text.append(char)
        else:
            text[len(text) - 1] += char

    return text


def right_visibility(width, string):
    """
    表示上での長さをもとに、文字列の左端を切り取る。

    :param width: 表示上での長さ。
    :param string: 切り取る文字列。
    """

    i = 1
    for i in range(1, len(string) + 2):
        if i == len(string) + 1 or get_visible_len(string[-i-1:]) > width:
            break

    if i == len(string) + 1:
        return string[-i:]
    else:
        return string[-i:]
