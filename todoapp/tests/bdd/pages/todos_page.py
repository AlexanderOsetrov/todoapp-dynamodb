from todoapp.tests.bdd.pages import base


class TodosPageLocators:

    TITLE = base.Locator.by_xpath("//h1[.='todos']")
    TODO_INPUT = base.Locator.by_css("input[class='new-todo']")

    @staticmethod
    def todo(todo_title):
        return base.Locator.by_xpath(f"//div[@class='view']/label[.='{todo_title}']")

    @staticmethod
    def todo_cross_icon(todo_title):
        return base.Locator.by_xpath(
            f"//div[@class='view']/label[.='{todo_title}']/following-sibling::button[@class='destroy']")

    @staticmethod
    def todo_edit_field(todo_title):
        return base.Locator.by_xpath(
            f"//div[@class='view']/label[.='{todo_title}']/../following-sibling::input[@class='edit']")

    @staticmethod
    def todo_checkbox(todo_title):
        return base.Locator.by_xpath(
            f"//div[@class='view']/label[.='{todo_title}']/preceding-sibling::input[@type='checkbox']")

    @staticmethod
    def todo_list_item(todo_title):
        return base.Locator.by_xpath(f"//div[@class='view']/label[.='{todo_title}']/../..")


class TodosPage(base.BasePage):

    def __init__(self, driver):
        super().__init__(driver)

    def is_title_present(self):
        return self.is_element_present(TodosPageLocators.TITLE)

    def add_todo(self, title):
        self.input_text(TodosPageLocators.TODO_INPUT, title)
        self.press_keys(TodosPageLocators.TODO_INPUT, "ENTER")

    def is_todo_item_visible(self, title):
        self.wait_for_presence_of(TodosPageLocators.todo(title))
        return self.is_element_visible(TodosPageLocators.todo(title))

    def click_todo_cross_icon(self, title):
        self.hover_mouse_over(TodosPageLocators.todo(title))
        self.wait_for_visibility_of(TodosPageLocators.todo_cross_icon(title))
        self.click_element(TodosPageLocators.todo_cross_icon(title), use_action_chains=True)

    def is_todo_item_present(self, title):
        return self.is_element_present(TodosPageLocators.todo(title))

    def change_title(self, title, new_title):
        self.doubleclick_element(TodosPageLocators.todo(title))
        self.press_keys(TodosPageLocators.todo_edit_field(title), "CONTROL+A")
        self.input_text(TodosPageLocators.todo_edit_field(title), new_title)
        self.press_keys(TodosPageLocators.todo_edit_field(title), "ENTER")

    def check_todo(self, title):
        self.wait_for_visibility_of(TodosPageLocators.todo(title))
        self.click_element(TodosPageLocators.todo_checkbox(title))

    def is_todo_completed(self, title):
        class_value = self.get_attribute(TodosPageLocators.todo_list_item(title), "class")
        return class_value == "completed"
