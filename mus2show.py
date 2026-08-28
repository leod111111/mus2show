from base64 import b64decode, b64encode
import subprocess
from datetime import datetime
from PySide6.QtWidgets import QApplication, QCheckBox, QFileDialog, QLabel, QMainWindow, QGridLayout, QMenu, QProgressBar, QScrollArea, QSizePolicy, QToolButton, QWidget, QLineEdit, QPushButton, QPlainTextEdit, QStyle, QVBoxLayout, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QDir, QUrl, QObject, QThread, Signal, Qt, QTimer
from PySide6.QtGui import QAction, QFont, QKeySequence, QMouseEvent, QPainter, QPixmap, QTextOption
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import os
import tempfile

temp_dir = tempfile.gettempdir() + "/mus2show/"
print(temp_dir)

gui_text = [
                "Mus2Show",
                "url de la vidéo à télécharger",
                "Aller à l'url",
                "Le téléchargement a démarré",
                "Téléchargement terminé. Conversion en wav...",
                "Conversion terminée ! Chargement de l'audio...",
                "L'audio est chargé et prêt à être utilisé !",
                "Télécharger l'audio",
                "Conversion en wav...",
                "Réencodage...",
                "Réencodage terminé ! Chargement de l'audio...",#10
                "Charger depuis l'appareil",
                "Opération annulée",
                "début :",
                "h",
                "fin :",
                "min",
                "s",
                "Découpage terminé ! Chargement de l'audio...",
                "Couper l'audio",
                "Le découpage a commencé...",
                "Fichier",
                "Ouvrir",
                "Nouveau",
                "Enregistrer",
                "Jouer",
                "Nom du projet",
                "Titre",
                "Modifier",
                "Supprimer",
                "Enregistrement du fichier",#30
                "Enregistrement terminé",
                "Précédent",
                "Enchaînement automatique",
                "Lecture automatique",
                "Suivant",#35
                "Bienvenue dans Mus2Show !",
                "Chargement de l'interface, veuillez patienter...",
                "Zone téléchargement initialisée",
                "Découpeur et sortie son initialisés",
                "Menu fichier initialisé",#40
                "Lecteur de projet initialisé",
                "Démarrage du logiciel",
                "Mise à jour des dépendances",
            ]

print(gui_text[43])

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.CREATE_NO_WINDOW

print(str(str(os.path.dirname(__file__)) + "/yt_dlp/yt-dlp.exe"))
subprocess.run([str(str(os.path.dirname(__file__)) + "/yt_dlp/yt-dlp.exe"), "-U"])

class TempWriter(QObject):
    progresssignal = Signal(float)
    finishedsignal = Signal()
    
    def __init__(self, data: list):
        self.data = data
        super().__init__()
    
    def run(self):
        total = len(self.data)
        i = 1
        for d in self.data:
            if os.path.exists(f'{temp_dir}{i}.wav'):
                os.remove(f'{temp_dir}{i}.wav')
            with open(f'{temp_dir}{i}.wav', 'xb') as f:
                f.write(d['content'])
            self.progresssignal.emit(i/total*100)
            i += 1
        self.finishedsignal.emit()

class Downloader(QObject):
    logsignal = Signal(str)
    outputsignal = Signal(bytes)
    finishedsignal = Signal()
    
    def __init__(self, url: str, id: int):
        super().__init__()
        self.url = url
        self.id = id
    
    def run(self):
        self.logsignal.emit(gui_text[3])
        subprocess.run([
                str(os.path.dirname(__file__)) + "/yt_dlp/yt-dlp.exe",
                "--ffmpeg-location", str(str(os.path.dirname(__file__)) + "/ffmpeg/bin"),
                "-x",
                "--audio-format", "wav",
                "--no-part",
                "--no-cache-dir",
                #"-q",
                #"--no-warnings",
                "--no-playlist",
                "--extract-audio",
                "--audio-multistreams",
                "--audio-quality", "0",
                "-f", "ba[ext=m4a]/ba[ext=webm]/ba[ext=opus]",
                "--no-check-certificate",
                "--no-mtime",
                "--js-runtimes", f"node:{str(os.path.dirname(__file__))}/nodejs/node.exe",
                "-o", f"{temp_dir}dtemp{self.id}.%(ext)s",
                self.url.replace("&", "^&")
            ],
            text=False,
            startupinfo=startupinfo,
            shell=True
        )
        self.logsignal.emit(gui_text[4])
        for temppath in os.listdir(temp_dir):
            list_temp_path = temppath.split(".")
            list_temp_path.pop()
            for char_index in range(len(list_temp_path) - 1):
                list_temp_path[char_index] += "."
            filename_without_ext = "".join(list_temp_path)
            if filename_without_ext == f"dtemp{self.id}":
                audio_filename = temppath
                break
        with open(f"{temp_dir}{audio_filename}", "rb") as processed_audio_file:
            self.wav_bytes = processed_audio_file.read()
        os.remove(f"{temp_dir}{audio_filename}")
        self.logsignal.emit(gui_text[5])
        self.outputsignal.emit(self.wav_bytes)
        self.finishedsignal.emit()

class Loader(QObject):
    logsignal = Signal(str)
    outputsignal = Signal(bytes)
    finishedsignal = Signal()
    
    def __init__(self, path):
        super().__init__()
        self.path = path
    
    def run(self):
        with open(self.path, "rb") as f:
            self.bytes = f.read()
        if str(self.path)[-4:] != ".wav":
            self.logsignal.emit(gui_text[8])
        else:
            self.logsignal.emit(gui_text[9])
        self.wav_bytes = subprocess.run(["ffmpeg/bin/ffmpeg.exe", "-loglevel", "quiet", "-i", "pipe:0", "-f", "wav", "-acodec", "pcm_s16le", "pipe:1"], input=self.bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, shell=True).stdout
        if str(self.path)[-4:] != ".wav":
            self.logsignal.emit(gui_text[5])
        else:
            self.logsignal.emit(gui_text[10])
        self.outputsignal.emit(self.wav_bytes)
        self.finishedsignal.emit()

class M2ShowLoader(QObject):
    outputsignal = Signal(dict)
    progresssignal = Signal(float)
    finishedsignal = Signal()
    
    def __init__(self, path: str):
        self.path = path
        super().__init__()
    
    def run(self):
        with open(self.path, "r") as f:
            total = len(f.read().strip("\n")) - 4
        with open(self.path, "r") as f:
            read_file = {"path": self.path}
            line = f.readline().strip("\n")
            if line != "m2show v1.1":
                return {"error": True}
            line = f.readline().strip("\n")
            read_file["name"] = line
            line = f.readline().strip("\n")
            read_file["date"] = line
            for _ in range(0, 2):
                line = f.readline()
            read_file["data"] = []
            i = 0
            for line in f:
                list_line = line.strip("\n").split(";")
                read_file["data"].append(
                    {
                        "no": int(list_line[0]),
                        "type": list_line[1],
                        "title": list_line[2],
                        "content": b64decode(list_line[3])
                    }
                )
                i += 1
                self.progresssignal.emit(i/total*100)
        self.outputsignal.emit(read_file)
        self.finishedsignal.emit()

class ProjectSaver(QObject):
    logsignal = Signal(str)
    progresssignal = Signal(float)
    finishedsignal = Signal()
    
    def __init__(self, path: str, data: dict):
        self.path = path
        self.data = data
        super().__init__()
    
    def run(self):
        self.logsignal.emit(f'{gui_text[30]} {self.path}')
        with open(self.path, "w") as f:
            f.write("m2show v1.1\n")
            f.write(self.data['name'])
            f.write(f"\n{datetime.now().strftime("%Y-%m-%d")}\n\n")
            f.write("no;type;title;content;startingAt(ifTypeIsAudio);endingAt(ifTypeIsAudio);channels(ifFileTypeIsAudio)")
            for i in range(0, len(self.data['data'])):
                self.progresssignal.emit(i/(len(self.data['data'])) * 100)
                f.write("\n" + str(self.data['data'][i]["no"]) + ";" + self.data['data'][i]["type"] + ";" + self.data['data'][i]["title"] + ";" + b64encode(self.data['data'][i]["content"]).decode('utf-8'))
            self.logsignal.emit(gui_text[31])
            self.finishedsignal.emit()

class Cutter(QObject):
    logsignal = Signal(str)
    outputsignal = Signal(bytes)
    finishedsignal = Signal()
    
    def __init__(self, id, bytes, start, end=0):
        super().__init__()
        self.bytes = bytes
        self.end = end
        self.start = start
        self.id = id
    
    def run(self):
        self.logsignal.emit(gui_text[20])
        input_path = f"{temp_dir}ctemp{self.id}.wav"
        output_path = f"{temp_dir}cotemp{self.id}.wav"
        with open(input_path, "xb") as temp_file:
            temp_file.write(self.bytes)
        if self.end != 0:
            subprocess.run([str(os.path.dirname(__file__)) + "/ffmpeg/bin/ffmpeg.exe", "-f", "wav", "-acodec", "pcm_s16le", "-i", input_path, "-ss", str(self.start / 1000), "-to", str(self.end / 1000), "-c", "copy", "-f", "wav", output_path], startupinfo=startupinfo, shell=True)
        else:
            subprocess.run([str(os.path.dirname(__file__)) + "/ffmpeg/bin/ffmpeg.exe", "-f", "wav", "-acodec", "pcm_s16le", "-i", input_path, "-ss", str(self.start / 1000), "-c", "copy", "-f", "wav", output_path], startupinfo=startupinfo, shell=True)
        with open(output_path, "rb") as temp_file:
            self.outputsignal.emit((temp_file.read()))
        os.remove(input_path)
        os.remove(output_path)
        self.finishedsignal.emit()

class ClickableLabel(QLabel):
    clicked = Signal(int)#emits ms time
    
    def __init__(self, duration: int, width: int):
        super().__init__()
        self.duration = duration #in ms
        self.svgwidth = width
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(event.position().toPoint().x() / self.svgwidth * self.duration)
        super().mousePressEvent(event)

class AudioTimeline(QWidget):
    cursor_moved = Signal(int) #emits the time in ms
    
    def __init__(self, duration: int, width: int):
        super().__init__()
        self.duration = duration #in ms
        self.svgwidth = width
        self.current_time = 0 #ms too
        
        self.label = ClickableLabel(self.duration, self.svgwidth)
        self.label.clicked.connect(self.on_clicked)
        self.update_svg()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_cursor)
        
        self.width_timer = QTimer()
        self.width_timer.timeout.connect(self.update_width)
        #self.width_timer.start(100)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_svg)
        self.update_timer.start(50)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def update_width(self):
        self.layout().update()
        new_width = self.width() - self.layout().contentsMargins().left() - self.layout().contentsMargins().right()
        self.svgwidth = new_width
        self.label.svgwidth = new_width
        self.update_svg()
    
    def change_playing(self, playing: bool):
        if playing:
            self.timer.start(20)
        else:
            self.timer.stop()
    
    def update_svg(self):
        cursor_x = self.current_time / self.duration * self.svgwidth
        svg = f'''
            <svg width="{self.svgwidth}" height="100" viewBox="0 0 {self.svgwidth} 100" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
                <rect x="0" y="45" width="{self.svgwidth}" height="10" fill="black" />
                <rect x="0" y="0" width="10" height="100" fill="black" />
                <rect x="{self.svgwidth - 10}" y="0" width="10" height="100" />
                <rect id="cursor" x="{cursor_x}" y="0" width="10" height="100" fill="cadetblue" />
                <text x="{self.svgwidth / 2}" y="90" font-family="Arial" font-size="15" font-weight="bold" text-anchor="middle" fill="black">{self.current_time // 3600000}:{(self.current_time % 3600000) // 60000}:{(self.current_time % 60000) / 1000}</text>
            </svg>
        '''
        renderer = QSvgRenderer()
        renderer.load(svg.encode("utf-8"))
        
        pixmap = QPixmap(self.svgwidth, 100)
        pixmap.fill("white")
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        self.label.setPixmap(pixmap)
    
    def update_cursor_from_player(self, time):
        self.current_time = time
        self.update_svg()
    
    def update_cursor(self):
        self.current_time += 20
        if self.current_time >= self.duration:
            self.current_time = 0
        self.update_svg()
    
    def update_duration(self, duration: int):
        self.duration = duration
        self.label.duration = duration
    
    def on_clicked(self, time: int):
        self.current_time = time
        self.update_svg()
        self.cursor_moved.emit(time)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(gui_text[0])
        self.setGeometry(15, 50, 700, 450)
        self.currentthreadsid = 0
        self.currentworkerid = 0
        self.threads = {}
        self.workers = {}
        self.data = {
            'path': '',
            'name': '',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'data': []
        }
        self.player_mode = False
        
        print(gui_text[37])
        
        #Main containers
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.central_widget_container = QWidget()
        self.central_widget = QWidget()
        self.central_widget_layout = QVBoxLayout()
        self.central_widget_container.setLayout(self.central_widget_layout)
        self.central_widget_layout.addWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget_container)
        
        #Downloader
        self.downloader_layout = QGridLayout()
        self.url_input = QLineEdit()
        self.url_input.setText("https://www.youtube.com/")
        self.url_input.setPlaceholderText(gui_text[1])
        self.downloader_layout.addWidget(self.url_input, 0, 0)
        self.url_go_button = QPushButton(gui_text[2])
        self.url_go_button.clicked.connect(self.go_to_url)
        self.downloader_layout.addWidget(self.url_go_button, 0, 3)
        self.video_view = QWebEngineView(url=QUrl("https://www.youtube.com/"))
        self.video_view.urlChanged.connect(self.update_displayed_url)
        self.downloader_layout.addWidget(self.video_view, 1, 0, 2, 4)
        self.back_video_view_button = QPushButton()
        self.back_video_view_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        self.downloader_layout.addWidget(self.back_video_view_button, 0, 1)
        self.back_video_view_button.clicked.connect(self.video_view.back)
        self.forward_video_view_button = QPushButton()
        self.forward_video_view_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        self.forward_video_view_button.clicked.connect(self.video_view.forward)
        self.downloader_layout.addWidget(self.forward_video_view_button, 0, 2)
        self.download_button = QPushButton(gui_text[7])
        self.download_button.clicked.connect(self.download)
        self.downloader_layout.addWidget(self.download_button, 0, 4, 2, 1)
        self.load_button = QPushButton(gui_text[11])
        self.load_button.clicked.connect(self.load_audio_file)
        self.downloader_layout.addWidget(self.load_button, 0, 5, 2, 1)
        self.download_status = QPlainTextEdit()
        self.download_status.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.download_status.setReadOnly(True)
        self.downloader_layout.addWidget(self.download_status, 2, 4, 1, 2)
        self.main_layout.addLayout(self.downloader_layout, 0, 1)
        
        print(gui_text[38])
        
        #Cutter
        self.cutter_layout = QGridLayout()
        self.cutter_timeline = AudioTimeline(2000, 600)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.playingChanged.connect(self.cutter_change_playing)
        self.player.positionChanged.connect(self.cutter_timeline.update_cursor_from_player)
        self.player.durationChanged.connect(self.cutter_timeline.update_duration)
        self.player.mediaStatusChanged.connect(self.check_media_status)
        self.cutter_timeline.label.clicked.connect(self.player.setPosition)
        self.cutter_layout.addWidget(self.cutter_timeline, 1, 0, 1, 16)
        
        self.cutter_play_button = QPushButton()
        self.cutter_play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.cutter_play_button.clicked.connect(self.on_cutter_play_clicked)
        self.cutter_layout.addWidget(self.cutter_play_button, 0, 0)
        
        self.cutter_start_button = QPushButton(gui_text[13])
        self.cutter_start_button.clicked.connect(self.set_start_to_pos)
        self.cutter_layout.addWidget(self.cutter_start_button, 0, 1)
        
        self.cutter_hour_start_input = QLineEdit()
        self.cutter_layout.addWidget(self.cutter_hour_start_input, 0, 2)
        
        self.cutter_hour_start_label = QLabel(gui_text[14])
        self.cutter_layout.addWidget(self.cutter_hour_start_label, 0, 3)
        
        self.cutter_minute_start_input = QLineEdit()
        self.cutter_layout.addWidget(self.cutter_minute_start_input, 0, 4)
        
        self.cutter_minute_start_label = QLabel(gui_text[16])
        self.cutter_layout.addWidget(self.cutter_minute_start_label, 0, 5)
        
        self.cutter_second_start_input = QLineEdit()
        self.cutter_layout.addWidget(self.cutter_second_start_input, 0, 6)
        
        self.cutter_second_start_label = QLabel(gui_text[17])
        self.cutter_layout.addWidget(self.cutter_second_start_label, 0, 7)
        
        self.cutter_end_button = QPushButton(gui_text[15])
        self.cutter_end_button.clicked.connect(self.set_end_to_pos)
        self.cutter_layout.addWidget(self.cutter_end_button, 0, 8)
        
        self.cutter_hour_end_input = QLineEdit()
        self.cutter_layout.addWidget(self.cutter_hour_end_input, 0, 9)
        
        self.cutter_hour_end_label = QLabel(gui_text[14])
        self.cutter_layout.addWidget(self.cutter_hour_end_label, 0, 10)
        
        self.cutter_minute_end_input = QLineEdit()
        self.cutter_layout.addWidget(self.cutter_minute_end_input, 0, 11)
        
        self.cutter_minute_end_label = QLabel(gui_text[16])
        self.cutter_layout.addWidget(self.cutter_minute_end_label, 0, 12)
        
        self.cutter_second_end_input = QLineEdit()
        self.cutter_layout.addWidget(self.cutter_second_end_input, 0, 13)
        
        self.cutter_second_end_label = QLabel(gui_text[17])
        self.cutter_layout.addWidget(self.cutter_second_end_label, 0, 14)
        
        self.cutter_cut_button = QPushButton(gui_text[19])
        self.cutter_cut_button.clicked.connect(self.cut_and_update)
        self.cutter_layout.addWidget(self.cutter_cut_button, 0, 15)
        
        self.main_layout.addLayout(self.cutter_layout, 1, 1)
        
        print(gui_text[39])
        
        #File editor
        self.file_editor_layout = QVBoxLayout()
        self.file_editor_container = QWidget()
        self.file_editor_container.setLayout(self.file_editor_layout)
        self.file_editor_scroll_area = QScrollArea()
        self.file_editor_scroll_area.setMinimumWidth(200)
        self.file_editor_scroll_area.setWidgetResizable(True)
        self.file_editor_scroll_area.setWidget(self.file_editor_container)
        self.file_editor_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.file_editor_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.file_editor_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_editor_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.file_menu_tool_button = QToolButton()
        self.file_menu_tool_button.setText("Fichier")
        self.file_menu_tool_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_menu = QMenu()
        
        self.open_action = QAction(gui_text[22], self)
        self.open_action.setShortcut(QKeySequence('Ctrl+O'))
        self.open_action.triggered.connect(self.load_m2show_file)
        self.file_menu.addAction(self.open_action)
        
        self.new_action = QAction(gui_text[23], self)
        self.new_action.setShortcut(QKeySequence('Ctrl+N'))
        self.new_action.triggered.connect(self.new_project)
        self.file_menu.addAction(self.new_action)
        
        self.save_action = QAction(gui_text[24], self)
        self.save_action.setShortcut(QKeySequence('Ctrl+S'))
        self.save_action.triggered.connect(self.save_project)
        self.file_menu.addAction(self.save_action)
        
        self.play_action = QAction(gui_text[25], self)
        self.play_action.setShortcut(QKeySequence('Ctrl+P'))
        self.play_action.triggered.connect(self.play_project)
        self.file_menu.addAction(self.play_action)
        
        self.file_menu_tool_button.setMenu(self.file_menu)
        self.file_editor_layout.addWidget(self.file_menu_tool_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.audios_items = []
        
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText(gui_text[26])
        self.project_name_input.textChanged.connect(self.update_project_name)
        self.file_editor_layout.addWidget(self.project_name_input, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.add_audio_button = QPushButton("+")
        self.add_audio_button.clicked.connect(lambda : self.add_audio(None, None, None))
        self.file_editor_layout.addWidget(self.add_audio_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        self.file_editor_layout.addStretch()
        
        self.main_layout.addWidget(self.file_editor_scroll_area, 0, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignTop)

        print(gui_text[40])
        
        #player
        self.player_container = QWidget()
        self.player_layout = QGridLayout()
        self.player_container.setLayout(self.player_layout)
        self.central_widget_layout.addWidget(self.player_container)
        self.player_container.hide()
        
        self.back_to_editor_button = QPushButton("←")
        self.back_to_editor_button.clicked.connect(self.back_to_editor)
        self.player_layout.addWidget(self.back_to_editor_button, 0, 0)
        
        self.player_title_label = QLabel()
        self.player_title_label.setFont(QFont('Helvetica', 22, 700))
        self.player_layout.addWidget(self.player_title_label, 0, 3, 1, 3)
        
        self.former_audio_button = QPushButton(gui_text[32])
        self.former_audio_button.clicked.connect(self.former_audio)
        self.player_layout.addWidget(self.former_audio_button, 0, 7, 1, 2)
        
        self.former_audio_label = QLabel()
        self.player_layout.addWidget(self.former_audio_label, 0, 9)
        
        self.audio_label = QLabel()
        self.audio_label.setFont(QFont('Helvetica', 16, 500))
        self.player_layout.addWidget(self.audio_label, 1, 0, 2, 2)
        
        self.player_audio_timeline = AudioTimeline(2000, 100)
        self.player.positionChanged.connect(self.player_audio_timeline.update_cursor_from_player)
        self.player.durationChanged.connect(self.player_audio_timeline.update_duration)
        self.player_audio_timeline.label.clicked.connect(self.player.setPosition)
        self.player_layout.addWidget(self.player_audio_timeline, 1, 2, 2, 5)
        
        self.auto_continue_checkbox = QCheckBox()
        self.auto_continue_checkbox.setCheckState(Qt.CheckState.Checked)
        self.player_layout.addWidget(self.auto_continue_checkbox, 1, 7)
        
        self.auto_continue_label = QLabel(gui_text[33])
        self.player_layout.addWidget(self.auto_continue_label, 1, 8, 1, 2)
        
        self.auto_play_checkbox = QCheckBox()
        self.auto_play_checkbox.setCheckState(Qt.CheckState.Unchecked)
        self.player_layout.addWidget(self.auto_play_checkbox, 2, 7)
        
        self.auto_play_label = QLabel(gui_text[34])
        self.player_layout.addWidget(self.auto_play_label, 2, 8, 1, 2)
        
        self.back_10_button = QPushButton("-10")
        self.back_10_button.clicked.connect(self.player_back_10)
        self.player_layout.addWidget(self.back_10_button, 3, 3)
        
        self.play_audio_button = QPushButton()
        self.play_audio_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPlay))
        self.play_audio_button.clicked.connect(self.player_play)
        self.player_layout.addWidget(self.play_audio_button, 3, 4)
        
        self.forward_10_button = QPushButton("+10")
        self.forward_10_button.clicked.connect(self.player_forward_10)
        self.player_layout.addWidget(self.forward_10_button, 3, 5)
        
        self.next_button = QPushButton(gui_text[35])
        self.next_button.clicked.connect(self.next_audio)
        self.player_layout.addWidget(self.next_button, 3, 7, 1, 2)
        
        self.next_audio_label = QLabel()
        self.player_layout.addWidget(self.next_audio_label, 3, 9)
        print(gui_text[41])
        print(gui_text[42])
    
    def check_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.player_mode and self.auto_continue_checkbox.isChecked():
            self.play_audio_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPlay))
            self.next_audio()
    
    def player_forward_10(self):
        self.player.setPosition(self.player.position() + 10000)
    
    def player_play(self):
        if self.player.isPlaying():
            self.player.pause()
            self.play_audio_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPlay))
        else:
            self.player.play()
            self.play_audio_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPause))
    
    def player_back_10(self):
        self.player.setPosition(self.player.position() - 10000)
    
    def next_audio(self):
        if os.path.exists(f'{temp_dir}{self.player_current_audio + 1}.wav'):
            self.player.setSource(f'{temp_dir}{self.player_current_audio + 1}.wav')
            self.player_current_audio += 1
            self.former_audio_label.setText(f'{self.player_current_audio - 1}. {self.data['data'][self.player_current_audio - 2]['title']}')
            self.audio_label.setText(f'{self.player_current_audio}. {self.data['data'][self.player_current_audio - 1]['title']}')
            if len(self.data['data']) > self.player_current_audio:
                self.next_audio_label.setText(f'{self.player_current_audio + 1}. {self.data['data'][self.player_current_audio]['title']}')
            else:
                self.next_audio_label.setText('')
            
            if self.auto_play_checkbox.isChecked():
                self.player.play()
                self.play_audio_button.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPause))
    
    def former_audio(self):
        if os.path.exists(f'{temp_dir}{self.player_current_audio - 1}.wav'):
            self.player.setSource(f'{temp_dir}{self.player_current_audio - 1}.wav')
            self.player_current_audio -= 1
            self.next_audio_label.setText(f'{self.player_current_audio + 1}. {self.data['data'][self.player_current_audio]['title']}')
            self.audio_label.setText(f'{self.player_current_audio}. {self.data['data'][self.player_current_audio - 1]['title']}')
            if self.player_current_audio > 1:
                self.former_audio_label.setText(f'{self.player_current_audio - 1}. {self.data['data'][self.player_current_audio - 2]['title']}')
            else:
                self.former_audio_label.setText('')
    
    def update_project_name(self, name: str):
        self.data['name'] = name
        self.player_title_label.setText(name)
    
    def add_audio(self, content=None, no=None, title=None):
        if content == None and no ==  None and title == None:
            content = self.cache_audio
            no = len(self.data['data']) + 1
            title = str(no)
            self.data['data'].append({
                'content': content,
                'no': no,
                'title': title,
                'type': 'audio'
            })
        
        self.audios_items.append({
            'layout': None,
            'no_label': None,
            'title_input': None,
            'title_lambda': None,
            'modify_button': None,
            'up_button': None,
            'down_button': None,
            'del_button': None,
            'up_lambda': None,
            'down_lambda': None,
            'modify_lambda': None,
            'del_lambda': None
        })
        
        self.audios_items[len(self.audios_items) - 1]['layout'] = QHBoxLayout()
        
        self.audios_items[len(self.audios_items) - 1]['no_label'] = QLabel(str(self.data['data'][no - 1]['no']) + ".")
        self.audios_items[len(self.audios_items) - 1]['layout'].addWidget(self.audios_items[len(self.audios_items) - 1]['no_label'], alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.audios_items[len(self.audios_items) - 1]['title_input'] = QLineEdit()
        self.audios_items[len(self.audios_items) - 1]['title_input'].setPlaceholderText(gui_text[27])
        self.audios_items[len(self.audios_items) - 1]['title_input'].setText(title)
        self.audios_items[len(self.audios_items) - 1]['title_lambda'] = lambda text, no=len(self.audios_items): self.update_audio_title(no, text)
        self.audios_items[len(self.audios_items) - 1]['title_input'].textChanged.connect(self.audios_items[len(self.audios_items) - 1]['title_lambda'])
        self.audios_items[len(self.audios_items) - 1]['layout'].addWidget(self.audios_items[len(self.audios_items) - 1]['title_input'], alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.audios_items[len(self.audios_items) - 1]['modify_button'] = QPushButton(gui_text[28])
        self.audios_items[len(self.audios_items) - 1]['modify_lambda'] = lambda clicked, bytes=self.data['data'][no - 1]['content']: self.update_cache_audio(bytes)
        self.audios_items[len(self.audios_items) - 1]['modify_button'].clicked.connect(self.audios_items[len(self.audios_items) - 1]['modify_lambda'])
        self.audios_items[len(self.audios_items) - 1]['layout'].addWidget(self.audios_items[len(self.audios_items) - 1]['modify_button'], alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.audios_items[len(self.audios_items) - 1]['up_button'] = QPushButton("↑")
        self.audios_items[len(self.audios_items) - 1]['up_lambda'] = lambda clicked, no=len(self.data['data']): self.audio_up(no)
        self.audios_items[len(self.audios_items) - 1]['up_button'].clicked.connect(self.audios_items[len(self.audios_items) - 1]['up_lambda'])
        self.audios_items[len(self.audios_items) - 1]['layout'].addWidget(self.audios_items[len(self.audios_items) - 1]['up_button'], alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.audios_items[len(self.audios_items) - 1]['down_button'] = QPushButton("↓")
        self.audios_items[len(self.audios_items) - 1]['down_lambda'] = lambda clicked, no=len(self.data['data']): self.audio_down(no)
        self.audios_items[len(self.audios_items) - 1]['down_button'].clicked.connect(self.audios_items[len(self.audios_items) - 1]['down_lambda'])
        self.audios_items[len(self.audios_items) - 1]['layout'].addWidget(self.audios_items[len(self.audios_items) - 1]['down_button'], alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.audios_items[len(self.audios_items) - 1]['del_button'] = QPushButton(gui_text[29])
        self.audios_items[len(self.audios_items) - 1]['del_lambda'] = lambda clicked, no=len(self.data['data']): self.audio_del(no)
        self.audios_items[len(self.audios_items) - 1]['del_button'].clicked.connect(self.audios_items[len(self.audios_items) - 1]['del_lambda'])
        self.audios_items[len(self.audios_items) - 1]['layout'].addWidget(self.audios_items[len(self.audios_items) - 1]['del_button'], alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.file_editor_layout.insertLayout(len(self.audios_items) + 1, self.audios_items[len(self.audios_items) - 1]['layout'])
        QTimer.singleShot(10, lambda: self.file_editor_scroll_area.ensureWidgetVisible(self.add_audio_button))
    
    def audio_del(self, no):
        self.audios_items[no - 1]['no_label'].deleteLater()
        self.audios_items[no - 1]['title_input'].deleteLater()
        self.audios_items[no - 1]['modify_button'].deleteLater()
        self.audios_items[no - 1]['up_button'].deleteLater()
        self.audios_items[no - 1]['down_button'].deleteLater()
        self.audios_items[no - 1]['del_button'].deleteLater()
        self.audios_items[no - 1]['layout'].deleteLater()
        self.audios_items.pop(no - 1)
        self.data['data'].pop(no - 1)
        for i in range(no - 1, len(self.audios_items)):
            self.data['data'][i]['no'] = i + 1
        for i in self.audios_items:
            i['no_label'].setText(f'{self.audios_items.index(i) + 1}.')
            i['up_button'].clicked.disconnect(i['up_lambda'])
            i['up_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_up(no)
            i['up_button'].clicked.connect(i['up_lambda'])
            i['down_button'].clicked.disconnect(i['down_lambda'])
            i['down_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_down(no)
            i['down_button'].clicked.connect(i['down_lambda'])
            i['del_button'].clicked.disconnect(i['del_lambda'])
            i['del_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_del(no)
            i['del_button'].clicked.connect(i['del_lambda'])
            i['title_input'].textChanged.disconnect(i['title_lambda'])
            i['title_lambda'] = lambda text, no=self.audios_items.index(i) + 1: self.update_audio_title(no, text)
            i['title_input'].textChanged.connect(i['title_lambda'])
    
    def audio_up(self, no: int):
        print('audio_up called for audio', no)
        if no != 1:
            self.data['data'].insert(no-2, self.data['data'][no-1])
            self.data['data'].pop(no)
            self.audios_items[no - 1]['layout'] = self.file_editor_layout.takeAt(no + 1)
            self.file_editor_layout.insertLayout(no, self.audios_items[no - 1]['layout'])
        else:
            self.data['data'].insert(len(self.data['data']), self.data['data'][no-1])
            self.data['data'].pop(no - 1)
            self.audios_items[no - 1]['layout'] = self.file_editor_layout.takeAt(no + 1)
            self.file_editor_layout.insertLayout(len(self.audios_items) + 1, self.audios_items[no - 1]['layout'])
        for d in self.data['data']:
            d['no'] = self.data['data'].index(d) + 1
        if no != 1:
            self.audios_items.insert(no - 2, self.audios_items[no - 1])
            self.audios_items.pop(no)
        else:
            self.audios_items.insert(len(self.audios_items), self.audios_items[no - 1])
            self.audios_items.pop(no - 1)   
        for i in self.audios_items:
            i['no_label'].setText(f'{self.audios_items.index(i) + 1}.')
            i['up_button'].clicked.disconnect(i['up_lambda'])
            i['up_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_up(no)
            i['up_button'].clicked.connect(i['up_lambda'])
            i['down_button'].clicked.disconnect(i['down_lambda'])
            i['down_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_down(no)
            i['down_button'].clicked.connect(i['down_lambda'])
            i['del_button'].clicked.disconnect(i['del_lambda'])
            i['del_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_del(no)
            i['del_button'].clicked.connect(i['del_lambda'])
            i['title_input'].textChanged.disconnect(i['title_lambda'])
            i['title_lambda'] = lambda text, no=self.audios_items.index(i) + 1: self.update_audio_title(no, text)
            i['title_input'].textChanged.connect(i['title_lambda'])
    
    def audio_down(self, no):
        if no != len(self.audios_items):
            self.data['data'].insert(no, self.data['data'][no-1])
            self.data['data'].pop(no - 1)
            self.audios_items[no - 1]['layout'] = self.file_editor_layout.takeAt(no + 1)
            self.file_editor_layout.insertLayout(no + 2, self.audios_items[no - 1]['layout'])
            self.audios_items.insert(no + 1, self.audios_items[no - 1])
            self.audios_items.pop(no - 1)
        else:
            self.data['data'].insert(0, self.data['data'][no-1])
            self.data['data'].pop()
            self.audios_items[no - 1]['layout'] = self.file_editor_layout.takeAt(no + 1)
            self.file_editor_layout.insertLayout(2, self.audios_items[no - 1]['layout'])
            self.audios_items.insert(0, self.audios_items[no - 1])
            self.audios_items.pop()
        for d in self.data['data']:
            d['no'] = self.data['data'].index(d) + 1
        for i in self.audios_items:
            i['no_label'].setText(f'{self.audios_items.index(i) + 1}.')
            i['up_button'].clicked.disconnect(i['up_lambda'])
            i['up_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_up(no)
            i['up_button'].clicked.connect(i['up_lambda'])
            i['down_button'].clicked.disconnect(i['down_lambda'])
            i['down_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_down(no)
            i['down_button'].clicked.connect(i['down_lambda'])
            i['del_button'].clicked.disconnect(i['del_lambda'])
            i['del_lambda'] = lambda clicked, no=self.audios_items.index(i) + 1: self.audio_del(no)
            i['del_button'].clicked.connect(i['del_lambda'])
            i['title_input'].textChanged.disconnect(i['title_lambda'])
            i['title_lambda'] = lambda text, no=self.audios_items.index(i) + 1: self.update_audio_title(no, text)
            i['title_input'].textChanged.connect(i['title_lambda'])

    def update_audio_title(self, no, text):
        self.data['data'][no - 1]['title'] = text

    def load_m2show_file(self):
        self.new_project()
        
        loader_file_dialog = QFileDialog()
        loader_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        loader_file_dialog.setFilter(QDir.Filter.Readable)
        path = loader_file_dialog.getOpenFileName(self.central_widget)[0]
        
        if path and path != ".m2show":
            thread_id = self.currentthreadsid
            self.currentthreadsid += 1
            self.threads[thread_id] = QThread()
            self.threads[thread_id].finished.connect(self.threads[thread_id].deleteLater)
            worker_id = self.currentworkerid
            self.workers[worker_id] = M2ShowLoader(path)
            self.currentworkerid += 1
            self.workers[worker_id].outputsignal.connect(self.update_data)
            self.workers[worker_id].finishedsignal.connect(self.workers[worker_id].deleteLater)
            self.progressbar = QProgressBar()
            self.progressbar.setValue(0)
            self.main_layout.addWidget(self.progressbar, 0, 0, 1, 2)
            self.progressbar.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.workers[worker_id].progresssignal.connect(self.progressbar.setValue)
            self.workers[worker_id].finishedsignal.connect(self.progressbar.deleteLater)
            self.workers[worker_id].moveToThread(self.threads[thread_id])
            self.threads[thread_id].started.connect(self.workers[worker_id].run)
            self.threads[thread_id].start()
        else:
            self.add_download_log(gui_text[12])
    
    def update_data(self, data: dict):
        self.data = data
        self.project_name_input.setText(self.data['name'])
        for d in data['data']:
            self.add_audio(d['content'], d['no'], d['title'])
    
    def new_project(self):
        if len(self.audios_items) > 0:
            for _ in range(len(self.audios_items)):
                self.audio_del(1)
        self.data['name'] = ''
        self.project_name_input.setText('')
        self.data['path'] = ''
    
    def save_project(self):
        if self.data['path']:
            path = self.data['path']
        else:
            loader_file_dialog = QFileDialog()
            loader_file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            loader_file_dialog.setFilter(QDir.Filter.Writable)
            loader_file_dialog.selectUrl(f'{self.data['name']}.m2show')
            loader_file_dialog.setDefaultSuffix('.m2show')
            path = loader_file_dialog.getSaveFileName(self.central_widget)[0]
            if path[:-7] != ".m2show":
                path += ".m2show"
        
        if path and path != ".m2show":
            thread_id = self.currentthreadsid
            self.currentthreadsid += 1
            self.threads[thread_id] = QThread()
            self.threads[thread_id].finished.connect(self.threads[thread_id].deleteLater)
            worker_id = self.currentworkerid
            self.workers[worker_id] = ProjectSaver(path, self.data)
            self.currentworkerid += 1
            self.workers[worker_id].finishedsignal.connect(self.workers[worker_id].deleteLater)
            self.workers[worker_id].logsignal.connect(self.add_download_log)
            self.progressbar = QProgressBar()
            self.progressbar.setValue(0)
            self.main_layout.addWidget(self.progressbar, 0, 0, 1, 2)
            self.progressbar.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.workers[worker_id].progresssignal.connect(self.progressbar.setValue)
            self.workers[worker_id].finishedsignal.connect(self.progressbar.deleteLater)
            self.workers[worker_id].moveToThread(self.threads[thread_id])
            self.threads[thread_id].started.connect(self.workers[worker_id].run)
            self.threads[thread_id].start()
        else:
            self.add_download_log(gui_text[12])
    
    def back_to_editor(self):
        self.player_container.hide()
        self.central_widget.show()
        self.player_mode = False
    
    def play_project(self):
        if len(self.data['data']) > 0:
            self.player.setSource("")
            thread_id = self.currentthreadsid
            self.currentthreadsid += 1
            self.threads[thread_id] = QThread()
            self.threads[thread_id].finished.connect(self.threads[thread_id].deleteLater)
            worker_id = self.currentworkerid
            self.workers[worker_id] = TempWriter(self.data['data'])
            self.currentworkerid += 1
            self.workers[worker_id].finishedsignal.connect(self.workers[worker_id].deleteLater)
            self.progressbar = QProgressBar()
            self.progressbar.setValue(0)
            self.main_layout.addWidget(self.progressbar, 0, 0, 1, 2)
            self.progressbar.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.workers[worker_id].progresssignal.connect(self.progressbar.setValue)
            self.workers[worker_id].finishedsignal.connect(self.progressbar.deleteLater)
            self.workers[worker_id].finishedsignal.connect(self.launch_playing)
            self.workers[worker_id].moveToThread(self.threads[thread_id])
            self.threads[thread_id].started.connect(self.workers[worker_id].run)
            self.threads[thread_id].start()
    
    def launch_playing(self):
        self.player.setSource(f'{temp_dir}1.wav')
        self.player_current_audio = 1
        self.central_widget.hide()
        self.audio_label.setText('1. ' + self.data['data'][0]['title'])
        if len(self.data['data']) > 1:
            self.next_audio_label.setText('2. ' + self.data['data'][1]['title'])
        self.player_container.show()
        self.player_audio_timeline.svgwidth = self.player_layout.cellRect(1, 2).width() + self.player_layout.cellRect(1, 3).width() + self.player_layout.cellRect(1, 4).width() + self.player_layout.cellRect(1, 5).width() + self.player_layout.cellRect(1, 6).width() - self.player_layout.contentsMargins().left() - self.player_layout.contentsMargins().right()
        self.player_audio_timeline.label.svgwidth = self.player_audio_timeline.svgwidth
        self.player_audio_timeline.update_svg()
        self.player_mode = True
    
    def cut_and_update(self):
        thread_id = self.currentthreadsid
        self.currentthreadsid += 1
        self.threads[thread_id] = QThread()
        self.threads[thread_id].finished.connect(self.threads[thread_id].deleteLater)
        worker_id = self.currentworkerid
        self.workers[worker_id] = Cutter(thread_id, self.cache_audio, self.get_cutter_start_time(), self.get_cutter_end_time())
        self.currentworkerid += 1
        self.workers[worker_id].logsignal.connect(self.add_download_log)
        self.workers[worker_id].outputsignal.connect(self.update_cache_audio)
        self.workers[worker_id].finishedsignal.connect(self.workers[worker_id].deleteLater)
        self.workers[worker_id].moveToThread(self.threads[thread_id])
        self.threads[thread_id].started.connect(self.workers[worker_id].run)
        self.threads[thread_id].start()

    def set_end_to_pos(self):
        self.cutter_end_input.setText(f"{self.player.position() // 3600000}:{(self.player.position() % 3600000) // 60000}:{(self.player.position() % 60000) / 1000}")
    
    def set_start_to_pos(self):
        self.cutter_start_input.setText(f"{self.player.position() // 3600000}:{(self.player.position() % 3600000) // 60000}:{(self.player.position() % 60000) / 1000}")
    
    def cutter_change_playing(self):
        if self.player.isPlaying():
            self.cutter_play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.cutter_play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    
    def get_cutter_start_time(self):
        try:
            time = 0
            if self.cutter_hour_start_input.displayText() != "":
                time = int(self.cutter_hour_start_input.displayText()) * 3600000
            if self.cutter_minute_start_input.displayText() != "":
                time += int(self.cutter_minute_start_input.displayText()) * 60000
            if self.cutter_second_start_input.displayText() != "":
                time += round(float(self.cutter_second_start_input.displayText()) * 1000)
            return time
        except Exception:
            return 0
    
    def get_cutter_end_time(self):
        try:
            time = 0
            if self.cutter_hour_end_input.displayText() != "":
                time = int(self.cutter_hour_end_input.displayText()) * 3600000
            if self.cutter_minute_end_input.displayText() != "":
                time += int(self.cutter_minute_end_input.displayText()) * 60000
            if self.cutter_second_end_input.displayText() != "":
                time += round(float(self.cutter_second_end_input.displayText()) * 1000)
            return int(time  != 0) * time + int(time == 0) * self.player.duration()
        except Exception:
            return self.cutter_timeline.duration
    
    def on_cutter_player_timer_timeout(self):
        if self.player.position() >= self.get_cutter_end_time():
            self.cutter_player_timer.stop()
            self.on_cutter_play_clicked(self.get_cutter_end_time())
    
    def on_cutter_play_clicked(self, pos: int | None = None):
        self.cutter_timeline.current_time = self.player.position()
        self.cutter_timeline.update_svg()
        if self.player.isPlaying():
            self.cutter_play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.player.pause()
            print(self.player.position())
            if pos:
                self.player.setPosition(pos)
        else:
            self.cutter_play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            if self.cutter_timeline.current_time < self.get_cutter_start_time() or self.cutter_timeline.current_time >= self.get_cutter_end_time():
                self.player.setPosition(self.get_cutter_start_time())
                self.cutter_timeline.current_time = self.get_cutter_start_time()
                self.cutter_timeline.update_svg()
            if self.get_cutter_end_time() != self.player.duration():
                self.player.play()
                self.cutter_player_timer = QTimer()
                self.cutter_player_timer.timeout.connect(self.on_cutter_player_timer_timeout)
                self.cutter_player_timer.start(1)
            else:
                self.player.play()
    
    def update_displayed_url(self, url: QUrl):
        self.url_input.setText(url.toString())
    
    def go_to_url(self):
        self.video_view.setUrl(self.url_input.displayText())
    
    def add_download_log(self, text):
        self.download_status.appendPlainText(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {text}")
        self.download_status.ensureCursorVisible()
    
    def update_cache_audio(self, bytes: bytes):
        self.cache_audio = bytes
        self.player.setSource(QUrl(""))
        if os.path.exists(f"{temp_dir}temp.wav"):
            os.remove(f"{temp_dir}temp.wav")
        with open(f"{temp_dir}temp.wav", "xb") as temp:
            temp.write(self.cache_audio)
        self.cutter_hour_start_input.setText("")
        self.cutter_minute_start_input.setText("")
        self.cutter_second_start_input.setText("")
        self.cutter_hour_end_input.setText("")
        self.cutter_minute_end_input.setText("")
        self.cutter_second_end_input.setText("")
        self.player.setSource(QUrl(os.path.normpath(f"{temp_dir}temp.wav").replace(os.sep, '/')))
        self.add_download_log(gui_text[6])
    
    def load_audio_file(self):
        loader_file_dialog = QFileDialog()
        loader_file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        loader_file_dialog.setFilter(QDir.Filter.Readable)
        
        thread_id = self.currentthreadsid
        self.currentthreadsid += 1
        self.threads[thread_id] = QThread()
        self.threads[thread_id].finished.connect(self.threads[thread_id].deleteLater)
        worker_id = self.currentworkerid
        path = loader_file_dialog.getOpenFileName(self.central_widget)[0]
        if path:
            self.workers[worker_id] = Loader(path)
            self.currentworkerid += 1
            self.workers[worker_id].logsignal.connect(self.add_download_log)
            self.workers[worker_id].outputsignal.connect(self.update_cache_audio)
            self.workers[worker_id].finishedsignal.connect(self.workers[worker_id].deleteLater)
            self.workers[worker_id].moveToThread(self.threads[thread_id])
            self.threads[thread_id].started.connect(self.workers[worker_id].run)
            self.threads[thread_id].start()
        else:
            self.add_download_log(gui_text[12])
    
    def download(self):
        thread_id = self.currentthreadsid
        self.currentthreadsid += 1
        self.threads[thread_id] = QThread()
        self.threads[thread_id].finished.connect(self.threads[thread_id].deleteLater)
        worker_id = self.currentworkerid
        self.workers[worker_id] = Downloader(self.video_view.url().toString(), thread_id)
        self.currentworkerid += 1
        self.workers[worker_id].logsignal.connect(self.add_download_log)
        self.workers[worker_id].outputsignal.connect(self.update_cache_audio)
        self.workers[worker_id].finishedsignal.connect(self.workers[worker_id].deleteLater)
        self.workers[worker_id].moveToThread(self.threads[thread_id])
        self.threads[thread_id].started.connect(self.workers[worker_id].run)
        self.threads[thread_id].start()

    def resizeEvent(self, event):
        self.file_editor_scroll_area.setFixedHeight(self.main_layout.cellRect(0, 0).height() + self.main_layout.cellRect(1, 0).height())
        self.file_editor_scroll_area.ensureWidgetVisible(self.add_audio_button)
        if self.player_mode:
            self.player_audio_timeline.svgwidth = self.player_layout.cellRect(1, 2).width() + self.player_layout.cellRect(1, 3).width() + self.player_layout.cellRect(1, 4).width() + self.player_layout.cellRect(1, 5).width() + self.player_layout.cellRect(1, 6).width() - self.player_layout.contentsMargins().left() - self.player_layout.contentsMargins().right()
            self.player_audio_timeline.label.svgwidth = self.player_audio_timeline.svgwidth
            self.player_audio_timeline.update_svg()
        else:
            self.cutter_timeline.svgwidth = self.cutter_layout.cellRect(1, 0).width() + self.cutter_layout.cellRect(1, 1).width() + self.cutter_layout.cellRect(1, 2).width() + self.cutter_layout.cellRect(1, 3).width() + self.cutter_layout.cellRect(1, 4).width() + self.cutter_layout.cellRect(1, 5).width() + self.cutter_layout.cellRect(1, 6).width() + self.cutter_layout.cellRect(1, 7).width() + self.cutter_layout.cellRect(1, 8).width() + self.cutter_layout.cellRect(1, 9).width() + self.cutter_layout.cellRect(1, 10).width() + self.cutter_layout.cellRect(1, 11).width() + self.cutter_layout.cellRect(1, 12).width() + self.cutter_layout.cellRect(1, 13).width() + self.cutter_layout.cellRect(1, 14).width()
            self.cutter_timeline.label.svgwidth = self.cutter_timeline.svgwidth
            self.cutter_timeline.update_svg()
        super().resizeEvent(event)

if __name__ == "__main__":
    print(gui_text[36])
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()