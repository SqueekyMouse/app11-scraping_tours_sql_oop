# commit: oops proj Sec40
class User:

    def __init__(self,name,birthyear) -> None:
        self.name=name
        self.birthyear=birthyear

    def get_name(self):
        return(self.name.upper())

    def age(self,current_year):
        age=current_year-self.birthyear
        return(age)

