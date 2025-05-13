# my_new_handler.py
#
# TEMPLATE — use for any new “handler” or service class
# that wants detailed, per‐method debug logs (console + CSV).
#
#  • Inherit from HandlerDebugMixin
#  • Accept the shared Conversation in __init__ and assign it to self.conversation
#  • Wrap every public method with debug('→ …') / debug('← …')
#  • (Optional) Use the @trace decorator at the bottom to eliminate boilerplate

from app.utils.debug import HandlerDebugMixin


class MyNewHandler(HandlerDebugMixin):
    """
    Purpose:  Describe what this handler does.
    Usage:    Instantiate with (conversation, any, other, params).
    """

    def __init__(self, conversation, some_dependency, config_value):
        # 1) Wire up debug proxy before any debug() calls
        self.conversation = conversation
        self.debug('→ Entering __init__')

        # 2) Real initialization
        self.some_dependency = some_dependency
        self.config_value = config_value

        # 3) Done
        self.debug('← Exiting __init__')

    def handle_request(self, request_payload: dict) -> dict:
        """
        Entry point for processing a request.
        request_payload: incoming data to act on.
        Returns: some result dict.
        """
        self.debug('→ Entering handle_request')

        # … your business logic here …
        result = {
            'status': 'ok',
            'echo': request_payload
        }


        self.debug('← Exiting handle_request')
        return result

    def helper_method(self, data: str) -> str:
        """
        A secondary method; still traced.
        """
        self.debug('→ Entering helper_method')
        # … transform data …
        transformed = data.upper()
        self.debug('← Exiting helper_method')
        return transformed

# OPTIONAL: if you’d rather not write pairs of debug() calls,
# drop this decorator into app/utils/debug.py (once), then:
#
# from app.utils.debug import trace
#
# and replace your methods with:
#
#     @trace
#     def handle_request(self, request_payload: dict) -> dict:
#         # … method body without manual debug() calls …
#         return {...}
#
# Here’s what @trace might look like:
#
# def trace(fn):
#     def wrapper(self, *args, **kwargs):
#         self.debug(f'→ Entering {fn.__name__}')
#         result = fn(self, *args, **kwargs)
#         self.debug(f'← Exiting {fn.__name__}')
#         return result
#     return wrapper
