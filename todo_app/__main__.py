"""Package entrypoint.

Run with (from project root):
    python -m todo_app
"""

from .application import TodoApplication

if __name__ == "__main__":
    TodoApplication().run()
