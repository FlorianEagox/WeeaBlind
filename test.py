import app_state
from video import Video
import utils

utils.create_output_dir()
app_state.video = Video("https://youtu.be/2rtt6MLvFmc?si=97bT3fy2gD-NAm_C", print)
app_state.video.run_dubbing(print)
