import unicodedata


def get_visible_len(string):
    """
    表示上での長さを返す。つまり
    全角文字の数×2 + 半角文字の数×1 を返す。
    :param str: 計算に用いる文字列。
    """

    length = 0
    for char in string:
        if unicodedata.east_asian_width(char) in "FWA":
            length += 2
        else:
            length += 1
    return length
