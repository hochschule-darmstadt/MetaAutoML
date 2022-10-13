
from threading import Lock

class ThreadLock:

    def __init__(self) -> None:
        self.__lock = Lock()

    def lock(self):
        """
        Lock access to the data storage to a single thread.
        ---
        >>> with data_store.lock():
                # critical region
                sess = data_storage.get_session(...)
                data_storage.update_session(..., {
                    "models": sess["models"] + [new_model]
                })
        """
        return ThreadLock.__Lock(self.__lock)

    class __Lock():
        """
        DataStore internal helper class. Use with `data_store.lock()`
        """
        def __init__(self, inner: Lock):
            self.__inner = inner
            
        def __enter__(self):
            self.__inner.acquire()
            
        def __exit__(self, type, value, traceback):
            self.__inner.release()
