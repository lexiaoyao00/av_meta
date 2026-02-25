from string import Template
from pydantic import BaseModel

class User(BaseModel):
    name: str = '大CC'
    message: str = 'http://blog.me115.com'
    age : int = 18

tempTemplate = Template("Hello $name ,your website is $message")

user = User()
string = tempTemplate.substitute(user.model_dump())
print(string)