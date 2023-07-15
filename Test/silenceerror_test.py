#import threading
import cgitb
cgitb.enable(format = 'text')
def startSearch(self, dir, text, type='.php'):
    if self.search_thread:
        try:
            stop_thread(self.search_thread)
        except:
            pass
        self.search_thread = None
    self.search_thread = threading.Thread(target=self.searchText, args=[dir, text, type])
    self.search_thread.start()

