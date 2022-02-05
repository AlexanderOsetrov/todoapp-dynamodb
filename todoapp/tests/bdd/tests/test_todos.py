from todoapp.tests.bdd.pages import todos_page
from pytest_bdd import given, when, then, scenario


@scenario("todos.feature", "User can add todo to the list")
def test_add_todo():
    pass


@scenario("todos.feature", "User can delete todo from the list")
def test_delete_todo():
    pass


@scenario("todos.feature", "User can modify todo title")
def test_modify_todo():
    pass


@scenario("todos.feature", "User can mark todo as completed")
def test_mark_todo_as_competed():
    pass


@given('todos page is opened')
def todos_page_is_opened(random_todo, browser, context, delete_items, app_host):
    context.todos_page = todos_page.TodosPage(browser)
    context.todos_page.open_page(app_host)
    assert context.todos_page.is_title_present()


@when('user adds a new todo item')
def user_adds_todo_item(context, random_title):
    context.todos_page.add_todo(random_title)


@then('todo item is displayed in the list')
def todo_item_is_displayed(context, random_title):
    assert context.todos_page.is_todo_item_visible(random_title)


@given('user has a todo in the list')
def todo_item_is_displayed_in_the_list(context, random_todo):
    assert context.todos_page.is_todo_item_visible(random_todo.get('title'))


@when('user hovers over todo and clicks the cross icon')
def user_removes_todo_item(context, random_title):
    context.todos_page.click_todo_cross_icon(random_title)


@then('todo item is not displayed in the list')
def todo_item_is_not_displayed(context, random_title):
    assert not context.todos_page.is_todo_item_present(random_title)


@when('user modifies the todo title')
def user_modifies_todo_item(context, random_title):
    context.todos_page.change_title(random_title, f"{random_title}_edit")


@then('todo title is changed')
def todo_item_is_changed(context, random_title):
    assert context.todos_page.is_todo_item_visible(f"{random_title}_edit")


@when('user marks the todo as completed')
def user_checks_todo_item(context, random_title):
    context.todos_page.check_todo(random_title)
    pass


@then('todo title is displayed as completed')
def todo_item_is_strikethrough(context, random_title):
    assert context.todos_page.is_todo_completed(random_title)
