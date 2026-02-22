import flet as ft

def main(page: ft.Page):
    test_str = "Hello, world!"

    def change_str(e):
        nonlocal test_str
        print(test_str)
        test_str = "Hello, flet!"
        print(test_str)
        page.update()


    page.add(ft.Text(test_str),
             ft.Button(content='修改内容',on_click=change_str))




if __name__ == "__main__":
    ft.run(main)