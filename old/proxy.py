import zipfile

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

PROXY_HOST = "x.botproxy.net"
# PROXY_PORT = 8443 # HTTPS
PROXY_PORT = 8080
PROXY_USER = "pxu26687-0"
PROXY_PASS = "eyJjf9CAUaOeAZptu4ux"
profile_path = r"C:\Users\glorious\AppData\Local\Google\Chrome\User Data"  # Path to browser profile

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (
    PROXY_HOST,
    PROXY_PORT,
    PROXY_USER,
    PROXY_PASS,
)

def get_driver(url, use_proxy=True):
    options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = "proxy_auth_plugin.zip"
        with zipfile.ZipFile(pluginfile, "w") as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("user-data-dir=" + profile_path) 
    driver = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(), chrome_options=options
    )
    driver.get(url)
    return driver