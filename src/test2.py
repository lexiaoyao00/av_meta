from pydantic import BaseModel

class User(BaseModel):
    name: str = '大CC'
    message: str = 'http://blog.me115.com'
    age : int = 18


str_tmp = "Hello {name} ,your website is {message}"

user = User()
dict_info = user.model_dump()
print(dict_info)
string = str_tmp.format(**dict_info)
print(string)