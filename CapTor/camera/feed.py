from numpy import empty
from caption_gen import *
import streamlit as st
import cv2
import csv
from PIL import Image
import pandas as pd
import time
from datetime import datetime
import tempfile
from imageio import imread

# To display the webcam feed
FRAME_WINDOW = st.image([])


def run_app():
    # sidebar
    st.sidebar.image("../assets/logo.png")
    st.sidebar.header("Log maker")
    st.sidebar.markdown(
        "Generate continuous textual description for video frames being captured by the camera for easy language based queries."
    )
    st.sidebar.markdown(
        "[Github Repository]()"
    )
    st.sidebar.markdown("[Proposal Video]()")

    # source selector
    st.header("Perform Suitable Action from Dropbox")
    source = st.selectbox("", ("Connect a Live Camera", "Upload Captured"))

    if source == "Upload Captured":
        video_file = st.file_uploader(
            "Camera History", accept_multiple_files=False, type=["mp4"]
        )
        tfile = tempfile.NamedTemporaryFile(delete=False)
        if video_file is not None:
            tfile.write(video_file.read())
        vid = cv2.VideoCapture(tfile.name)
    if source == "Connect a Live Camera":
        vid = cv2.VideoCapture(0)
    run = st.checkbox("Trigger", key="start")
    show_frame = st.checkbox("Display Video Frames", key="frame")
    entry = []
    csvw = CSVWorker(entry)
    # Starts the app, when the button is clicked
    while run:
        _, frame = vid.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if show_frame:
            FRAME_WINDOW.image(frame)
        # img = Image.fromarray(frame)
        # img = img.resize((224, 224))
        pred = cap_gen(frame)
        print(pred)
        csvw.write(pred,entry)
        caption = " "
        caption.join(pred)
        st.write(caption)
        time.sleep(5)
    vid.release()
    cv2.destroyAllWindows()


def main():
    run_app()


@st.cache(show_spinner=False)
class CSVWorker:
    entry = []
    def __init__(self,entry):
        self.fields = [
            "w1",
            "w2",
            "w3",
            "w4",
            "w5",
            "w6",
            "w7",
            "w8",
            "w9",
            "w10",
            "time",
            "camera",
        ]
        self.filename = "results.csv"
        # self.create_csv()

    def create_csv(self):
        df = pd.DataFrame(list(), columns=self.fields)
        df.to_csv(self.filename)

    def write(self, pred, entry):
        # df = pd.read_csv(self.filename)
        pred = pred[1:-1]
        if len(pred) == 10:
            for i in range (0,10):
                lst = []
                lst.append(pred[i])
                if(i == 9):
                    lst.append(datetime.now())
                    lst.append(1)
            lst = tuple(lst)
            entry.append(lst)
        elif len(pred) < 10:
            lst = []
            for i in range(len(pred)):
                lst.append(pred[i])
            for j in range(len(pred),10):
                lst.append(" ")
            lst.append(datetime.now())
            lst.append(1)
            lst = tuple(lst)
            entry.append(lst)
        filename = open(self.filename, "w+")
        with filename as csvfile:
            csvwriter = csv.writer(csvfile)
            entry = tuple(entry)
            for en in range(1, len(entry)):
                csvwriter.writerow(entry[en])


if __name__ == "__main__":
    main()