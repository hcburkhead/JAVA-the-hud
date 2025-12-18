# JAVA-the-hud
Just. Another. Voice. Assistant.

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⣿⣿⣿⣷⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⣷⡄⠀⠙⢿⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣸⣿⣿⣦⡀⠀⠙⢿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣦⣄⠀⠈⠛⠿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣷⣤⣀⠀⠘⢿⣿⡧⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠘⢁⣴⣾⣿⡿⠋⠀⠀⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⠇⢀⣶⣿⣿⣿⠋⠀⢀⣤⣾⣷⠀⠀
⠀⠀⠀⠀⠠⠤⠶⣶⣤⣄⣉⠙⠿⣿⡿⠃⣰⣿⣿⣿⣿⠃⠀⢰⣿⣿⣿⣿⡇⠀
⠀⠀⣤⣤⣤⣄⡀⠈⠻⣿⣿⣷⣦⡈⠁⣼⣿⣿⣿⣿⣿⠀⠀⣿⣿⣿⣿⣿⠃⠀
⠀⢸⣿⣿⣿⣿⣷⠀⠀⢹⣿⣿⣿⣷⡀⢻⣿⣿⣿⣿⣿⠀⠀⢹⣿⣿⣿⡟⠀⠀
⠀⠘⣿⣿⣿⣿⣿⣇⠀⠈⠻⣿⣿⣿⣷⠀⣿⣿⣿⣿⠟⠀⠀⣾⣿⣿⡟⠀⠀⠀
⠀⠀⠙⣿⣿⣿⣿⣿⣦⣀⠀⠀⠉⠛⠻⠀⣿⡿⠟⠁⠀⣠⣾⣿⡿⠋⠀⠀⠀⠀
⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣶⣶⠄⠀⠈⠋⠀⢀⣠⣾⡿⠟⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

a personal AI to help you automate tasks by speaking to it with a GUI with waveforms to see responses. This acts as a wrapper for whatever LLM you want just needs an API Key

prerequisites: 
- ElevenLabs API Key (required for voice commands)
- MAPS API Key (optional)
- LLM Key (obviously) (0.0)

Installation: 

CLI: Download the repo and run it in Python in it's own virtual environment (python venv -name-). It should detect your microphone after initializing run [java-activate] 

The GUI is a plasmoid accessed in KDE (This project requires Linux -"I use Arch btw"- ...but can also be ran on MacOS) which will run after you have started the backend ^SEE ABOVE^

Use:

JAVA is able to do the following:
-> Open apps placed in the app allow list [java-add]
-> Install apps placed in the app allow list [java-add] (requires sudo group access so you can run [/.java-sudo-access.sh] if you want
-> Perform specific actions in the app specified in the config: power users go wild!
  -> Search Google Maps for travel information: (requires MAPS API Key) ie "Java, how long of a drive would it be to go to -destination- ?" Java will respond with the time it would take and ask if you would like directions
  -> Perform searches via voice: ie "Java, search for linux commands" Java will open your default browser (unless you specify it in the command ie "Brave") and search for linux commands
