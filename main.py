import os
from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform

URL = "https://antrax-app-fixo.serveousercontent.com/"


class AntraxApp(App):

  def build(self):
    if platform == "android":
      Clock.schedule_once(self.init_webview, 0.5)
    return

  def init_webview(self, dt):
    from android.runnable import run_on_ui_thread
    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    WebChromeClient = autoclass("android.webkit.WebChromeClient")

    activity = PythonActivity.mActivity

    @run_on_ui_thread
    def create_view():
      webview = WebView(activity)

      # Ativa suporte completo a JS, armazenamento local e permissões de mídia
      settings = webview.getSettings()
      settings.setJavaScriptEnabled(True)
      settings.setDomStorageEnabled(True)
      settings.setAllowFileAccess(True)
      settings.setAllowContentAccess(True)
      settings.setMediaPlaybackRequiresUserGesture(False)

      webview.setWebViewClient(WebViewClient())
      webview.setWebChromeClient(WebChromeClient())

      # Carrega o painel em tela cheia nativa do app
      webview.loadUrl(URL)
      activity.setContentView(webview)

    create_view()


if __name__ == "__main__":
  AntraxApp().run()
