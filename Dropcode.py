import sublime, sublime_plugin, os, httplib, urllib, threading, webbrowser

class Dropcode(sublime_plugin.TextCommand):
  stat_chars = "/-\\|"
  stat_cur   = 0
  msg        = ""
  url        = ""

  def __init__(self, view):
    self.settings = sublime.load_settings(__name__ + ".sublime-settings")
    self.view = view

  def run(self, edit, sel = False):
    if self.view.file_name():
      name, ext = os.path.splitext(os.path.basename(self.view.file_name()))
    else:
      name, ext = "Untitled", ".txt" # fix this on the site
    if sel:
      paste = self.view.substr(self.view.sel()[0])
    else:
      paste = self.view.substr(sublime.Region(0, self.view.size()))
    if not paste:
      sublime.status_message("Error: Nothing to paste")
      return
    pst = urllib.urlencode({
     'name': name,
     'syntax': ext[1:],
     'private': self.settings.get('private') or 0,
     'paste': paste
    })
    thread = threading.Thread(target = self.send, args = (pst,))
    thread.start()
    self.check(thread)

  def check(self, thread):
    if thread.is_alive():
      self.stat_cur = 0 if self.stat_cur == 3 else self.stat_cur + 1
      sublime.status_message("Uploading: %s" % self.stat_chars[self.stat_cur])
      sublime.set_timeout(lambda: self.check(thread), 100)
    else:
      sublime.status_message(self.msg)
      sublime.set_clipboard(self.url)
      if self.settings.get("open_url"):
        webbrowser.open(self.url)

  def send(self, params):
    try:
      req = httplib.HTTPConnection("dropcode.b23.be")
      req.request("POST", "/", params, {"Accept": "text/plain"})
      rsp = req.getresponse()
      if rsp.status == 200:
        self.url = rsp.read()
        self.msg = "Upload OK, link copied to clipboard"
      else:
        self.msg = "Upload error (%d): %s" % rsp.status, rsp.read()
    except (Exception) as (e):
      self.msg = '%s: %s' % e
    finally:
      req.close()
