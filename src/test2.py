import re

def normalize(text:str) -> str:
    """替换所有常见的字符"""
    result = text.replace("_", "-")
    result = re.sub(r'cd\d+|CD\d+', '', result)
    return result

def main():
    string = 'CLUB-014-cd3'
    res = normalize(string)
    print(res)

if __name__ == '__main__':
    main()
