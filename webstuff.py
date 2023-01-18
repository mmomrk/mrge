#!/usr/bin/env python3

import mrge
import streamlit as stl


class StreamlitFlushable:
    def write(self, *args, **kwargs):
        return stl.write(*args, **kwargs)

    def flush(self):
        return


class StringerFlushable:
    def __init__(self):
        self.accumulator = []

    def write(self, *args, **kwargs):
        for value in args:
            self.accumulator.append(value)

    def flush(self):
        return

    def __str__(self):
        return ''.join(map(str, self.accumulator))


def loadFile(container):
    fileIn = container.file_uploader(label='Pick a .txt file', type='txt')
    if fileIn is None:
        return None
    # This will be an iterable I guess
    return fileIn


def get_readme():
    readme = ""
    with open('README.md', 'r') as readmeF:
        readme = readmeF.read()
    return readme


if __name__ == '__main__':
    #st = stl
    stl.set_page_config(page_title="MRGE - greedy randomness extractor", page_icon=":game_die:",
                        menu_items={"Report a bug": "mailto:mark.mipt@yahoo.com", "About": get_readme()})
    cont1 = stl.empty()
    cont2 = stl.empty()
    st = stl.empty()
    cont1.write("A demo of a My Greedy Randomness Extractor\n\nREADME could be found in the menu. Upload a file to extract randomness from. \n\nEach line contains a single input event, separated by newline character. Input events will be processed by python float() function")
    file = loadFile(cont2)
    if not file:
        pass
        print("LOOP?")
        #st.write("No file yet")
    else:
        cont1.empty()
        cont2.empty()
        lines = file.getvalue().decode("UTF-8")
        for line in lines:
            print(line)
        # st.empty()
        #st.write(f"Received {len(lines)} lines of input")
        e = mrge.Extractor(instream=lines)
        # this class has a .write so should be valid # valid indeed
        #e.outp = StreamlitFlushable()
        stringer = StringerFlushable()
        e.outp = stringer
        e.loop()
        st.write(stringer)
