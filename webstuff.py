#!/usr/bin/env python3

import mrge
import streamlit as st


class StreamlitFlushable:
    def write(self,*args,**kwargs):
        return st.write(*args,**kwargs)
    def flush(self):
        return

def loadFile():
    fileIn = st.file_uploader(label='Pick a file. Please give it a txt type', type='txt')
    if fileIn is None:
        return None
    # This will be an iterable I guess
    return fileIn 

if __name__ == '__main__':
    st.title("A demo of a My Greedy Randomness Extractor\nREADME could be found here: TODO\nUpload a file to extract randomness from. Each line contains a single input event, separated by newline character")
    file = loadFile()
    if not file:
        print("LOOP?")
        st.write("No file yet")
    else:
        lines=file.getvalue().decode("UTF-8")
        for line in lines:
            print(lines)
        st.write(f"Received {len(lines)} lines of input")
        e = mrge.Extractor(instream=lines)
        # this has a .write so should be valid
        e.outp = StreamlitFlushable()
        e.loop()
    st.write("Endof stuff")
    readme = ""
    with open('README.md','r') as readmeF:
        readme = readmeF.read()
    st.markdown(readme)

    
