# Mus2show
Mus2show is a piece of software allowing you to :
1. Download Sounds/Music from Youtube
2. Cut them as you want
3. Put them into a whole 'project' file
4. Do that again, until you have everything you need in your 'project'
5. Reorganize and modify the audios
6. Save your project (.m2show file)
7. Re-open it at any time
8. 'Play' your project : all the features you need for a smooth playing are in the User Interface :    
    * 'Auto-play' and 'Auto-continuing' checkboxes for more convenience.
    * A clickable timeline for the audio
    * Of course, labels with the names you defined for your audio
9. 'Former' audio and 'Next' audio buttons

### Requirements

There are two different manners of running Mus2Show. If you just want to simply use Mus2Show, you can download the .zip file of the latest release, unzip it on your computer, and you're done ! The only requirement for this way of running Mus2Show is Windows.

If you want to run Mus2Show for development purposes (make improvements and changes in the source code), here's what you will need :
* Windows (the latest version if possible)
* A copy/clone of this repository
* The latest version of python installed on your computer
* The following python packages :    
    * requests
    * PySide6
* The latest versions of the following software **in the mus2show folder** :    
    * [yt-dlp](https://github.com/yt-dlp/yt-dlp)    
    * [node.js](https://nodejs.org/en/download)    
    * [ffmpeg](https://ffmpeg.org/download.html)


For the python packages, you can run the following command (if you have pip installed) : `pip install pyside6 requests`.

For the other dependancies (yt-dlp, node.js and ffmpeg), install them that so it follows the following structure :
```text
mus2show/
├── mus2show.py
├── gui_resources/
│   └── downloadIcon.svg
├── yt_dlp/
│   └── yt-dlp.exe
├── nodejs/
│   ├── node_modules/
│   ├── other node js files
│   └── node.exe
└── ffmpeg/
    ├── bin/
    │   ├── ffmpeg.exe
    │   ├── ffprobe.exe
    │   └── ffplay.exe
    └── other ffmpeg files
```

I also plan to make an in-app tutorial by the end of 2026, to make learning how to use the app more easy and enjoyable.