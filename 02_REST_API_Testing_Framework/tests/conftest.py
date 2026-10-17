import pytest
from api.client import APIClient

CATEGORY_LABELS = {
    "smoke": "SMOKE TESTS", "posts": "POSTS", "users": "USERS",
    "comments": "COMMENTS", "todos": "TODOS", "albums": "ALBUMS",
    "photos": "PHOTOS", "contract": "CONTRACT / SCHEMA",
    "headers": "HTTP HEADERS", "filtering": "FILTERING / QUERY PARAMETERS",
    "crud": "CRUD / HTTP METHODS", "negative": "NEGATIVE CASES",
    "robustness": "ROBUSTNESS / PERFORMANCE", "data_integrity": "DATA INTEGRITY / RELATIONSHIPS",
}
CATEGORY_ORDER = list(CATEGORY_LABELS)

@pytest.fixture(scope="session")
def api_client():
    client = APIClient()
    yield client
    client.session.close()

@pytest.fixture
def valid_post_payload():
    return {"title": "QA framework test", "body": "Created during API automation testing", "userId": 1}

@pytest.fixture
def valid_todo_payload():
    return {"title": "Complete API tests", "completed": False, "userId": 1}

def pytest_collection_modifyitems(items):
    def key(item):
        marks = {mark.name for mark in item.iter_markers()}
        category = next((name for name in CATEGORY_ORDER if name in marks), "other")
        return (CATEGORY_ORDER.index(category) if category in CATEGORY_ORDER else len(CATEGORY_ORDER), item.nodeid)
    items.sort(key=key)

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location):
    
    pass

class CategoryReporter:
    def __init__(self, terminalreporter):
        self.terminalreporter = terminalreporter
        self.current_category = None

    def pytest_runtest_logstart(self, nodeid, location):
        session = self.terminalreporter.config._api_category_session
        item = next((i for i in session.items if i.nodeid == nodeid), None)
        if item is None:
            return
        marks = {mark.name for mark in item.iter_markers()}
        category = next((name for name in CATEGORY_ORDER if name in marks), "other")
        if category != self.current_category:
            self.current_category = category
            label = CATEGORY_LABELS.get(category, "OTHER TESTS")
            self.terminalreporter.write_sep("=", f"{label} — {nodeid.split('::')[0]}")

def pytest_configure(config):
    config.pluginmanager.register(CategoryPlugin(config), "api-category-plugin")

class CategoryPlugin:
    def __init__(self, config):
        self.config = config
        self.current_category = None

    def pytest_sessionstart(self, session):
        self.config._api_category_session = session

    def pytest_runtest_logstart(self, nodeid, location):
        terminal = self.config.pluginmanager.get_plugin("terminalreporter")
        session = getattr(self.config, "_api_category_session", None)
        if terminal is None or session is None:
            return
        item = next((i for i in session.items if i.nodeid == nodeid), None)
        if item is None:
            return
        marks = {mark.name for mark in item.iter_markers()}
        category = next((name for name in CATEGORY_ORDER if name in marks), "other")
        if category != self.current_category:
            self.current_category = category
            label = CATEGORY_LABELS.get(category, "OTHER TESTS")
            terminal.write_sep("=", f"{label} — {nodeid.split('::')[0]}")
